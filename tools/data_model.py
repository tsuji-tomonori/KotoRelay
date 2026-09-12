#!/usr/bin/env python3
"""静的な設計モデルからDSQL DDL案・全カラム辞書を生成/差分検査する。DB接続はしない。"""
from pathlib import Path
import argparse, importlib.util, json, re
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('model', ROOT/'design/data/model.py')
model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
TABLES=model.TABLES

def validate():
    by={t['name']:t for t in TABLES};assert len(by)==len(TABLES)
    ready=set();ncols=0;nfks=0
    for t in TABLES:
        name=t['name'];assert re.fullmatch('[a-z][a-z0-9_]*',name)
        cols={c['name']:c for c in t['columns']};assert len(cols)==len(t['columns'])
        ncols+=len(cols)
        for c in t['columns']:
            assert re.fullmatch('[a-z][a-z0-9_]*',c['name']) and c['description']
            assert re.fullmatch(r'uuid|text|boolean|bigint|integer|timestamptz|date|jsonb|varchar\(\d+\)|numeric\(\d+,\d+\)',c['type']),c
        for key in [t['primary']]+t['unique']+t['indexes']:
            assert 0<len(key)<=8 and len(set(key))==len(key)
            assert all(k in cols and cols[k]['type']!='jsonb' for k in key)
            size=sum(16 if cols[k]['type']=='uuid' else 8 if cols[k]['type'] in ('bigint','integer','timestamptz','date') else int(re.search(r'\d+',cols[k]['type']).group())*4 if cols[k]['type'].startswith('varchar') else 16 for k in key)
            assert size<=1024, (name,key,size)
        assert len(t['unique'])+len(t['indexes'])+1<=24
        assert len({tuple(k) for k in t['unique']})==len(t['unique'])
        for f in t['foreign_keys']:
            target=by[f['target']];tc={c['name']:c for c in target['columns']}
            assert f['target'] in ready or f['target']==name,(name,f['target'],'DDL order')
            assert len(f['columns'])==len(f['references'])
            assert f['references'] in [target['primary']]+target['unique'],(name,f,'nonunique target')
            for c,r in zip(f['columns'],f['references']):assert cols[c]['type']==tc[r]['type'],(name,c,f['target'],r)
            if f['target']!='organizations':assert f['columns'][0]=='organization_id' and f['references'][0]=='organization_id'
            nfks+=1
        ready.add(name)
    return {'tables':len(TABLES),'columns':ncols,'foreign_keys':nfks,'secondary_indexes':sum(len(t['indexes']) for t in TABLES),'unique_constraints':sum(len(t['unique']) for t in TABLES)}

def render():
    stats=validate()
    sql=['-- KotoRelay / Aurora DSQL データモデル v0.2 / 2026-09-12',
         '-- 設計案。実DSQLでは未適用。1 DDLずつautocommitで実行し、ASYNC jobの完了を確認する。',
         '-- BEGINやmigration toolの全体transactionで包まない。GRANT/IAM・移行・初期データは別設計。',
         '-- https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-ddl.html','',
         'CREATE SCHEMA kotorelay;','']
    md=['# KotoRelay — テーブル・カラム辞書','',
        '版0.2 / 2026-09-12 / 提案設計。`design/data/model.py` から生成。実DBのas-builtではない。','',
        f'**{stats["tables"]}テーブル / {stats["columns"]}カラム / {stats["foreign_keys"]}外部キー / {stats["secondary_indexes"]}追加検索インデックス**。全テーブルを専用スキーマ `kotorelay` に置く。','',
        '全ての `id` はランダムUUIDの主キー。`organization_id` は複合FKと全APIのWHERE条件に使用する。NULL可以外はNOT NULL。DEFAULTを省き、アプリが値を明示する。S3バケットは環境設定で固定し、DBの任意バケット名から読み込まない。','',
        '| テーブル | 役割 |','| --- | --- |']
    for t in TABLES:md.append(f'| [{t["name"]}](#{t["name"]}) | {t["purpose"]} |')
    for ti,t in enumerate(TABLES,1):
        name=t['name'];definitions=[]
        for c in t['columns']:definitions.append('  '+c['name']+' '+c['type']+('' if c['nullable'] else ' NOT NULL'))
        definitions.append('  PRIMARY KEY ('+', '.join(t['primary'])+')')
        for k in t['unique']:definitions.append('  UNIQUE ('+', '.join(k)+')')
        for ci,expr in enumerate(t['checks'],1):definitions.append(f'  CONSTRAINT ck_{ti:02}_{ci:02} CHECK ({expr})')
        for fi,f in enumerate(t['foreign_keys'],1):definitions.append(f'  CONSTRAINT fk_{ti:02}_{fi:02} FOREIGN KEY ('+', '.join(f['columns'])+') REFERENCES kotorelay.'+f['target']+' ('+', '.join(f['references'])+') ON DELETE RESTRICT ON UPDATE RESTRICT')
        sql+=['-- '+t['purpose'],'CREATE TABLE kotorelay.'+name+' (',',\n'.join(definitions),' );','']
        md+=['',f'## {name}','',t['purpose'],'','| カラム | 型 | NULL | 内容 |','| --- | --- | --- | --- |']
        for c in t['columns']:md.append(f'| `{c["name"]}` | `{c["type"]}` | {"可" if c["nullable"] else "不可"} | {c["description"].replace("|","/")} |')
        md+=['','主キー: `'+', '.join(t['primary'])+'`。']
        if t['unique']:md+=['','一意制約: '+' / '.join('`'+', '.join(k)+'`' for k in t['unique'])+'。']
        if t['foreign_keys']:
            md+=['','外部キー（すべてRESTRICT。認可は別途アプリで強制）:','']
            for f in t['foreign_keys']:md.append('- `('+', '.join(f['columns'])+')` → `'+f['target']+'('+', '.join(f['references'])+')`')
        if t['checks']:md+=['','DBチェック: '+' / '.join('`'+x+'`' for x in t['checks'])+'。']
        if t['indexes']:md+=['','検索インデックス: '+' / '.join('`'+', '.join(k)+'`' for k in t['indexes'])+'。']
        if t['rules']:md+=['','業務制約・更新規則: '+t['rules']]
    sql+=['-- 以下の各CREATE INDEX ASYNCも、別々のトランザクションで実行する。','-- 戻り値のjob IDで完了と索引の利用可能性を確認してから次工程へ進む。','']
    for ti,t in enumerate(TABLES,1):
        for i,k in enumerate(t['indexes'],1):sql.append(f'CREATE INDEX ASYNC ix_{ti:02}_{i:02} ON kotorelay.{t["name"]} ('+', '.join(k)+');')
    dictionary='\n'.join(md)+'\n'
    narrative=(ROOT/'docs/design/DATA-MODEL.md').read_text()
    combined=narrative+'\n\n---\n\n'+dictionary
    return {ROOT/'design/data/schema.sql':'\n'.join(sql)+'\n',ROOT/'design/data/schema.json':json.dumps({'project':'KotoRelay','version':'0.2','stats':stats,'tables':TABLES},ensure_ascii=False,indent=2)+'\n',ROOT/'docs/design/TABLES.md':dictionary,ROOT/'KotoRelay-データモデル.md':combined},stats

def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['generate','check']);args=parser.parse_args()
    outputs,stats=render()
    for path,content in outputs.items():
        if args.command=='generate':path.write_text(content)
        else:assert path.read_text()==content, '生成差分: '+str(path)
    print('PASS static data model '+args.command+': '+json.dumps(stats,ensure_ascii=False))
    print('FK参照先・型・UNIQUE・DDL順・組織境界・索引列数/最大バイト数・生成差分を静的確認。DSQL構文実行・性能・業務不変条件の製品検証は未実施。')
if __name__=='__main__':main()
