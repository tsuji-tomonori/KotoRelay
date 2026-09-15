import { useEffect, useState } from 'react';
import './database.css';
import { Graph } from './DatabaseGraph';

export type Column = {
  logicalName: string;
  description: string;
  name: string;
  type: string;
  nullable: boolean;
  primaryKey: boolean;
  default: string | null;
  definition: string;
};
export type Table = {
  logicalName: string;
  description: string;
  group: string;
  annotatedDdl: string;
  name: string;
  columns: Column[];
  primaryKey: string[];
  constraints: string[];
  source: string;
  ddl: string;
};
export type Relationship = {
  id: string;
  from: string;
  to: string;
  columns: string[];
  targetColumns: string[];
  definition: string;
};
type Query = {
  id: string;
  source: string;
  description: string;
  sql: string;
  access: Record<string, string>;
};
type Operation = {
  id: string;
  method: string;
  path: string;
  summary: string;
  queries: string[];
  documents: Record<string, string>;
};
type Database = {
  schemaVersion: number;
  tables: Table[];
  relationships: Relationship[];
  queries: Query[];
  operations: Operation[];
};

const actions = { C: '作成', R: '参照', U: '更新', D: '削除' };
function Crud({ value }: { value: string }) {
  return (
    <span className="db-crud">
      {[...value].map((a) => (
        <span key={a} title={actions[a as keyof typeof actions]}>
          {a}
        </span>
      ))}
    </span>
  );
}

export function DatabaseExplorer({
  revision,
  onNavigate,
}: {
  revision: string;
  onNavigate: (id: string) => void;
}) {
  const [data, setData] = useState<Database | null>(null);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState('documents');
  const [search, setSearch] = useState('');
  const [relatedOnly, setRelatedOnly] = useState(false);
  const [tab, setTab] = useState('columns');
  const [apiSearch, setApiSearch] = useState('');
  const [action, setAction] = useState('');
  const [columnSearch, setColumnSearch] = useState('');
  const [column, setColumn] = useState('');
  const [relation, setRelation] = useState('');
  const [nameMode, setNameMode] = useState('both');
  const [focus, setFocus] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    void fetch('./design-data/DATABASE.gen.json', { signal: controller.signal })
      .then((r) => {
        if (!r.ok) throw Error();
        return r.json();
      })
      .then((value: Database) => {
        if (
          value.schemaVersion !== 2 ||
          !value.tables.length ||
          !Array.isArray(value.queries) ||
          !Array.isArray(value.operations) ||
          !Array.isArray(value.relationships)
        )
          throw Error();
        setData(value);
        if (!value.tables.some((t) => t.name === 'documents')) setSelected(value.tables[0].name);
      })
      .catch((e: Error) => {
        if (e.name !== 'AbortError')
          setError('DB設計データを読み込めませんでした。ページを再読み込みしてください。');
      });
    return () => controller.abort();
  }, []);
  if (error) return <p role="alert">{error}</p>;
  if (!data) return <p role="status">DB設計を読み込み中…</p>;
  const table = data.tables.find((t) => t.name === selected)!;
  const relations = data.relationships.filter((r) => r.from === selected || r.to === selected);
  const neighbors = new Set([selected, ...relations.flatMap((r) => [r.from, r.to])]);
  const visible = data.tables.filter((t) => !relatedOnly || neighbors.has(t.name));
  const queries = data.queries.filter((q) => q.access[selected]);
  const queryMap = new Map(queries.map((q) => [q.id, q]));
  const operations = data.operations.filter((op) => op.queries.some((id) => queryMap.has(id)));
  function select(name: string) {
    setSelected(name);
    setColumn('');
    setRelation('');
    setColumnSearch('');
    setApiSearch('');
    setAction('');
  }
  function source(path: string) {
    return `https://github.com/tsuji-tomonori/KotoRelay/blob/${encodeURIComponent(revision)}/${path}`;
  }
  function sqlCard(q: Query) {
    const callers = data!.operations.filter((op) => op.queries.includes(q.id));
    return (
      <details className="db-sql" key={q.id}>
        <summary>
          <Crud value={q.access[selected]} /> {q.description}
        </summary>
        <a href={source(q.source)} target="_blank" rel="noreferrer">
          {q.source}
        </a>
        <pre>
          <code>{q.sql}</code>
        </pre>
        <div className="db-chips">
          {Object.entries(q.access).map(([name, value]) => (
            <button key={name} onClick={() => select(name)}>
              {name} <Crud value={value} />
            </button>
          ))}
        </div>
        <p>
          呼び出し元API:{' '}
          {callers.length
            ? callers.map((op) => op.id).join(' / ')
            : 'APIからの到達なし（API以外の処理も確認してください）'}
        </p>
      </details>
    );
  }
  return (
    <div className={'db-explorer' + (focus ? ' db-focus' : '')}>
      <div className="db-topbar">
        <div>
          <strong>スキーマ閲覧</strong>
          <span>
            {data.tables.length}テーブル · {data.relationships.length}外部キー ·{' '}
            {data.operations.length} API
          </span>
        </div>
        <div className="db-toolbar">
          <label>
            図の名前表示
            <select value={nameMode} onChange={(e) => setNameMode(e.target.value)}>
              <option value="both">論理名 / 物理名</option>
              <option value="logical">論理名（和名）</option>
              <option value="physical">物理名</option>
            </select>
          </label>
          <button aria-pressed={focus} onClick={() => setFocus(!focus)}>
            {focus ? 'パネルを表示' : '図に集中'}
          </button>
        </div>
      </div>
      <div className="db-workspace">
        <aside className="db-objects" aria-label="オブジェクト一覧">
          <h2>テーブル</h2>
          <label>
            テーブル・カラムを検索
            <input
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="和名 / テーブル / カラム"
            />
          </label>
          <div aria-label="テーブル一覧">
            {[...new Set(data.tables.map((t) => t.group))].map((group) => {
              const found = data.tables.filter(
                (t) =>
                  t.group === group &&
                  [
                    t.name,
                    t.logicalName,
                    ...t.columns.flatMap((c) => [c.name, c.logicalName]),
                  ].some((s) => s.toLowerCase().includes(search.toLowerCase())),
              );
              return found.length ? (
                <section key={group}>
                  <h3>
                    {group} <small>{found.length}</small>
                  </h3>
                  {found.map((t) => (
                    <button
                      key={t.name}
                      aria-label={t.name}
                      aria-pressed={selected === t.name}
                      onClick={() => select(t.name)}
                    >
                      <strong>{t.logicalName}</strong>
                      <span>{t.name}</span>
                      <small>{t.columns.length}</small>
                    </button>
                  ))}
                </section>
              ) : null;
            })}
            {!data.tables.some((t) =>
              [t.name, t.logicalName, ...t.columns.flatMap((c) => [c.name, c.logicalName])].some(
                (s) => s.toLowerCase().includes(search.toLowerCase()),
              ),
            ) && <p role="status">一致するテーブルはありません。</p>}
          </div>
        </aside>
        <div className="db-canvas">
          <div className="db-canvas-heading">
            <span>
              ER DIAGRAM <small>閲覧専用</small>
            </span>
            <label className="db-checkbox">
              <input
                type="checkbox"
                checked={relatedOnly}
                onChange={(e) => setRelatedOnly(e.target.checked)}
              />
              選択テーブルと直接の関係のみ
            </label>
          </div>
          <Graph
            tables={data.tables}
            visible={visible}
            relationships={data.relationships}
            selected={selected}
            column={column}
            relation={relation}
            nameMode={nameMode}
            onSelect={select}
            onColumn={(name, c) => {
              select(name);
              setColumn(c);
              setTab('columns');
              setFocus(false);
            }}
            onRelation={(r) => {
              select(r.from);
              setRelation(r.id);
              setTab('relations');
              setFocus(false);
            }}
          />
          <p className="db-status">
            {table.logicalName} / {selected}
            {column ? '.' + column : ''} · PK 主キー / FK 外部キー · 線は外部キーの列 → 参照先の列
          </p>
        </div>
        <article className="db-detail" aria-label="選択テーブルの詳細">
          <div className="db-detail-heading">
            <span>プロパティ</span>
            <h2>{selected}</h2>
            <strong>{table.logicalName}</strong>
            <p>{table.description}</p>
          </div>
          <p>
            {table.columns.length} カラム · {relations.length} 関係 · {operations.length} 利用API
          </p>
          <div className="db-tabs" aria-label="詳細表示の切替">
            {Object.entries({
              columns: 'カラム・DDL',
              relations: '関係',
              apis: 'API・CRUD',
              sql: 'SQL一覧',
            }).map(([key, label]) => (
              <button key={key} aria-pressed={tab === key} onClick={() => setTab(key)}>
                {label}
              </button>
            ))}
          </div>
          {column && tab === 'columns' && (
            <section className="db-column-detail" aria-label="選択カラムの詳細">
              <h3>
                {table.columns.find((c) => c.name === column)!.logicalName} <code>{column}</code>
              </h3>
              <p>{table.columns.find((c) => c.name === column)!.description}</p>
              <code>{table.columns.find((c) => c.name === column)!.definition}</code>
              <div className="db-chips">
                {relations
                  .filter(
                    (r) =>
                      (r.from === selected && r.columns.includes(column)) ||
                      (r.to === selected && r.targetColumns.includes(column)),
                  )
                  .map((r) => (
                    <button
                      key={r.id}
                      onClick={() => {
                        setRelation(r.id);
                        setTab('relations');
                      }}
                    >
                      関係: {r.from} → {r.to}
                    </button>
                  ))}
              </div>
              <button onClick={() => setColumn('')}>カラム選択を解除</button>
            </section>
          )}
          {tab === 'columns' && (
            <>
              <label>
                カラムを検索
                <input
                  type="search"
                  value={columnSearch}
                  onChange={(e) => setColumnSearch(e.target.value)}
                />
              </label>
              <div className="db-table-scroll">
                <table>
                  <caption>{selected}のカラム定義</caption>
                  <thead>
                    <tr>
                      <th scope="col">カラム</th>
                      <th scope="col">型</th>
                      <th scope="col">NULL</th>
                      <th scope="col">既定値</th>
                    </tr>
                  </thead>
                  <tbody>
                    {table.columns
                      .filter((c) =>
                        (c.name + c.logicalName).toLowerCase().includes(columnSearch.toLowerCase()),
                      )
                      .map((c) => (
                        <tr key={c.name} className={column === c.name ? 'db-current-column' : ''}>
                          <th scope="row">
                            <button className="db-column-link" onClick={() => setColumn(c.name)}>
                              {c.logicalName}
                              <small>{c.name}</small>
                            </button>
                            {c.primaryKey && <b className="db-key">PK</b>}
                            {relations.some(
                              (r) => r.from === selected && r.columns.includes(c.name),
                            ) && <b className="db-key">FK</b>}
                            <details>
                              <summary>列のDDL</summary>
                              <p>{c.description}</p>
                              <code>{c.definition}</code>
                            </details>
                          </th>
                          <td>{c.type}</td>
                          <td>{c.nullable ? '可' : '不可'}</td>
                          <td>{c.default ?? '指定なし'}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
              <details className="db-sql db-annotated">
                <summary>和名・説明付きDDL</summary>
                <p>論理名と説明をコメントとして付けた閲覧用DDLです。</p>
                <a
                  download={table.name + '-ja.sql'}
                  href={'data:text/plain;charset=utf-8,' + encodeURIComponent(table.annotatedDdl)}
                >
                  説明付きDDLを保存
                </a>
                <pre>
                  <code>{table.annotatedDdl}</code>
                </pre>
              </details>
              <h3>テーブル制約</h3>
              {table.constraints.map((c) => (
                <pre key={c}>{c}</pre>
              ))}
              <details className="db-sql">
                <summary>DDL原文</summary>
                <a href={source(table.source)} target="_blank" rel="noreferrer">
                  {table.source}
                </a>
                <pre>
                  <code>{table.ddl}</code>
                </pre>
              </details>
            </>
          )}
          {tab === 'relations' && (
            <>
              <p>
                子 →
                参照先。複合キーは同じ位置のカラム同士が対応します。DDLにない関係は推測しません。
              </p>
              {relation && <button onClick={() => setRelation('')}>すべての関係を表示</button>}
              {relations
                .filter((r) => !relation || r.id === relation)
                .map((r) => (
                  <section className="db-relation" key={r.id}>
                    <button aria-label={r.from} onClick={() => select(r.from)}>
                      {data.tables.find((t) => t.name === r.from)!.logicalName} / {r.from}
                    </button>{' '}
                    →{' '}
                    <button aria-label={r.to} onClick={() => select(r.to)}>
                      {data.tables.find((t) => t.name === r.to)!.logicalName} / {r.to}
                    </button>
                    <p>{r.from === selected ? '参照先' : 'このテーブルを参照する側'}</p>
                    {r.columns.map((c, i) => (
                      <div key={c}>
                        <button
                          className="db-column-link"
                          onClick={() => {
                            select(r.from);
                            setColumn(c);
                            setTab('columns');
                          }}
                        >
                          {
                            data.tables
                              .find((t) => t.name === r.from)!
                              .columns.find((col) => col.name === c)!.logicalName
                          }
                          <small>{c}</small>
                        </button>{' '}
                        →{' '}
                        <button
                          className="db-column-link"
                          onClick={() => {
                            select(r.to);
                            setColumn(r.targetColumns[i]);
                            setTab('columns');
                          }}
                        >
                          {
                            data.tables
                              .find((t) => t.name === r.to)!
                              .columns.find((col) => col.name === r.targetColumns[i])!.logicalName
                          }
                          <small>{r.targetColumns[i]}</small>
                        </button>
                      </div>
                    ))}
                    <pre>{r.definition}</pre>
                  </section>
                ))}
              {!relations.length && <p>DDLに外部キー関係はありません。</p>}
            </>
          )}
          {tab === 'apis' && (
            <>
              <p>
                SQLは認証・共有処理・条件分岐を含む静的な呼び出し候補です。実行ログではありません。
              </p>
              <div className="db-filters">
                <label>
                  APIを検索
                  <input
                    type="search"
                    value={apiSearch}
                    onChange={(e) => setApiSearch(e.target.value)}
                    placeholder="API名・パス・説明"
                  />
                </label>
                <label>
                  CRUD
                  <select
                    aria-label="CRUD"
                    value={action}
                    onChange={(e) => setAction(e.target.value)}
                  >
                    <option value="">すべて</option>
                    {Object.entries(actions).map(([key, label]) => (
                      <option key={key} value={key}>
                        {key} — {label}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
              <p>
                C=作成 / R=参照 / U=更新 /
                D=削除。条件に応じて実行されるため、毎回全操作を行う意味ではありません。
              </p>
              {operations
                .filter(
                  (op) =>
                    (op.id + op.path + op.summary)
                      .toLowerCase()
                      .includes(apiSearch.toLowerCase()) &&
                    op.queries.some((id) => queryMap.get(id)?.access[selected].includes(action)),
                )
                .map((op) => {
                  const matched = op.queries
                    .map((id) => queryMap.get(id))
                    .filter((q): q is Query => !!q && q.access[selected].includes(action));
                  const crud = Object.keys(actions)
                    .filter((a) =>
                      op.queries.some((id) => queryMap.get(id)?.access[selected].includes(a)),
                    )
                    .join('');
                  return (
                    <section className="db-operation" key={op.id}>
                      <h3>
                        <Crud value={crud} /> {op.summary}
                      </h3>
                      <code>
                        {op.method} {op.path}
                      </code>
                      <p>{op.id}</p>
                      <div className="db-chips">
                        <button onClick={() => onNavigate(op.documents.query)}>
                          APIのクエリ帳票
                        </button>
                        <button onClick={() => onNavigate(op.documents.sequence)}>
                          呼び出し順・条件
                        </button>
                      </div>
                      {matched.map(sqlCard)}
                    </section>
                  );
                })}
              {!operations.some(
                (op) =>
                  (op.id + op.path + op.summary).toLowerCase().includes(apiSearch.toLowerCase()) &&
                  op.queries.some((id) => queryMap.get(id)?.access[selected].includes(action)),
              ) && <p role="status">条件に一致するAPIはありません。</p>}
            </>
          )}
          {tab === 'sql' && (
            <>
              <p>
                静的解析で確認した呼び出し候補です。実行ログではありません。このテーブルにアクセスするSQL{' '}
                {queries.length} 件。SQL内の別テーブルもクリックして移動できます。
              </p>
              {queries.map(sqlCard)}
              {!queries.length && <p>このテーブルを利用するSQLはありません。</p>}
            </>
          )}
        </article>
      </div>
    </div>
  );
}
