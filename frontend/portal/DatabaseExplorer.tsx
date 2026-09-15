import { useEffect, useMemo, useRef, useState } from 'react';
import './database.css';

type Column = {
  name: string;
  type: string;
  nullable: boolean;
  primaryKey: boolean;
  default: string | null;
  definition: string;
};
type Table = {
  name: string;
  columns: Column[];
  primaryKey: string[];
  constraints: string[];
  source: string;
  ddl: string;
};
type Relationship = {
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
type View = { x: number; y: number; scale: number };
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

function Graph({
  tables,
  relationships,
  selected,
  onSelect,
}: {
  tables: Table[];
  relationships: Relationship[];
  selected: string;
  onSelect: (name: string) => void;
}) {
  const viewport = useRef<HTMLDivElement>(null);
  const [view, setView] = useState<View>({ x: 20, y: 20, scale: 1 });
  const points = useRef(new Map<number, { x: number; y: number }>());
  const positions = useMemo(
    () =>
      new Map(
        tables.map((table, i) => [
          table.name,
          { x: (i % 3) * 300 + 25, y: Math.floor(i / 3) * 140 + 25 },
        ]),
      ),
    [tables],
  );
  const width = Math.min(tables.length, 3) * 300 + 20;
  const height = Math.ceil(tables.length / 3) * 140 + 20;
  function fit() {
    const box = viewport.current;
    if (!box) return;
    const scale = Math.min((box.clientWidth - 32) / width, (box.clientHeight - 32) / height, 1);
    setView({
      x: (box.clientWidth - width * scale) / 2,
      y: (box.clientHeight - height * scale) / 2,
      scale,
    });
  }
  useEffect(() => {
    const box = viewport.current;
    if (!box) return;
    const observer = new ResizeObserver(() => {
      const scale = Math.min((box.clientWidth - 32) / width, (box.clientHeight - 32) / height, 1);
      setView({
        x: (box.clientWidth - width * scale) / 2,
        y: (box.clientHeight - height * scale) / 2,
        scale,
      });
    });
    observer.observe(box);
    return () => observer.disconnect();
  }, [width, height]);
  function zoom(factor: number, x?: number, y?: number) {
    const cx = x ?? (viewport.current?.clientWidth ?? 0) / 2;
    const cy = y ?? (viewport.current?.clientHeight ?? 0) / 2;
    setView((v) => {
      const scale = Math.max(0.15, Math.min(3, v.scale * factor));
      return {
        x: cx - ((cx - v.x) * scale) / v.scale,
        y: cy - ((cy - v.y) * scale) / v.scale,
        scale,
      };
    });
  }
  useEffect(() => {
    const box = viewport.current;
    if (!box) return;
    const wheel = (event: WheelEvent) => {
      event.preventDefault();
      const rect = box.getBoundingClientRect();
      zoom(Math.exp(-event.deltaY * 0.002), event.clientX - rect.left, event.clientY - rect.top);
    };
    box.addEventListener('wheel', wheel, { passive: false });
    return () => box.removeEventListener('wheel', wheel);
  }, []);
  function center() {
    const p = positions.get(selected);
    const box = viewport.current;
    if (p && box)
      setView({ scale: 1, x: box.clientWidth / 2 - p.x - 125, y: box.clientHeight / 2 - p.y - 48 });
  }
  return (
    <section className="db-graph-panel" aria-label="テーブル関係図">
      <div className="db-toolbar">
        <button onClick={() => zoom(1.25)} aria-label="ER図を拡大">
          ＋
        </button>
        <button onClick={() => zoom(0.8)} aria-label="ER図を縮小">
          −
        </button>
        <output aria-label="ER図の倍率">{Math.round(view.scale * 100)}%</output>
        <button onClick={fit}>全体表示</button>
        <button onClick={center}>選択テーブルへ</button>
      </div>
      <p id="db-graph-help">
        ドラッグで移動・ホイール／ピンチで拡大縮小。キーボードは矢印・＋・−・Home。矢印は参照先へ向かいます。
      </p>
      <div
        ref={viewport}
        className="db-viewport"
        tabIndex={0}
        role="region"
        aria-label="操作できるER図"
        aria-describedby="db-graph-help"
        onKeyDown={(e) => {
          if (e.target !== e.currentTarget) return;
          if (
            ['+', '=', '-', 'Home', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(
              e.key,
            )
          )
            e.preventDefault();
          if (['+', '='].includes(e.key)) zoom(1.25);
          if (e.key === '-') zoom(0.8);
          if (e.key === 'Home') fit();
          const delta: Record<string, [number, number]> = {
            ArrowLeft: [50, 0],
            ArrowRight: [-50, 0],
            ArrowUp: [0, 50],
            ArrowDown: [0, -50],
          };
          if (delta[e.key])
            setView((v) => ({ ...v, x: v.x + delta[e.key][0], y: v.y + delta[e.key][1] }));
        }}
        onPointerDown={(e) => {
          if ((e.target as HTMLElement).closest('button') || e.button > 0) return;
          points.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
          e.currentTarget.setPointerCapture(e.pointerId);
        }}
        onPointerMove={(e) => {
          const old = points.current.get(e.pointerId);
          if (!old) return;
          const before = [...points.current.values()];
          points.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
          const after = [...points.current.values()];
          if (before.length === 2) {
            const distance = (p: typeof before) => Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y);
            const rect = e.currentTarget.getBoundingClientRect();
            const bx = (before[0].x + before[1].x) / 2 - rect.left;
            const by = (before[0].y + before[1].y) / 2 - rect.top;
            const ax = (after[0].x + after[1].x) / 2 - rect.left;
            const ay = (after[0].y + after[1].y) / 2 - rect.top;
            setView((v) => {
              const scale = Math.max(
                0.15,
                Math.min(3, (v.scale * distance(after)) / Math.max(1, distance(before))),
              );
              return {
                scale,
                x: ax - ((bx - v.x) * scale) / v.scale,
                y: ay - ((by - v.y) * scale) / v.scale,
              };
            });
          } else setView((v) => ({ ...v, x: v.x + e.clientX - old.x, y: v.y + e.clientY - old.y }));
        }}
        onPointerUp={(e) => points.current.delete(e.pointerId)}
        onPointerCancel={(e) => points.current.delete(e.pointerId)}
        onLostPointerCapture={(e) => points.current.delete(e.pointerId)}
      >
        <div
          className="db-world"
          style={{
            width,
            height,
            transform: `translate(${view.x}px, ${view.y}px) scale(${view.scale})`,
          }}
        >
          <svg width={width} height={height} aria-hidden="true">
            <defs>
              <marker
                id="db-arrow"
                viewBox="0 0 10 10"
                refX="9"
                refY="5"
                markerWidth="7"
                markerHeight="7"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke" />
              </marker>
            </defs>
            {relationships.map((r, i) => {
              const from = positions.get(r.from),
                to = positions.get(r.to);
              if (!from || !to) return null;
              const sx = from.x + 125,
                sy = from.y + 96,
                tx = to.x + 125,
                ty = to.y;
              const bend = 30 + (i % 4) * 12;
              return (
                <path
                  key={r.id}
                  d={`M ${sx} ${sy} C ${sx} ${sy + bend}, ${tx - 60} ${ty - bend}, ${tx} ${ty}`}
                  className={r.from === selected || r.to === selected ? 'selected' : ''}
                  markerEnd="url(#db-arrow)"
                />
              );
            })}
          </svg>
          {tables.map((t) => (
            <button
              key={t.name}
              className="db-node"
              aria-label={'テーブル ' + t.name}
              aria-pressed={selected === t.name}
              style={{ left: positions.get(t.name)!.x, top: positions.get(t.name)!.y }}
              onClick={() => onSelect(t.name)}
            >
              <strong>{t.name}</strong>
              <span>PK {t.primaryKey.join(', ') || 'なし'}</span>
              <small>{t.columns.length} カラム</small>
            </button>
          ))}
        </div>
      </div>
    </section>
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
  useEffect(() => {
    const controller = new AbortController();
    void fetch('./design-data/DATABASE.gen.json', { signal: controller.signal })
      .then((r) => {
        if (!r.ok) throw Error();
        return r.json();
      })
      .then((value: Database) => {
        if (
          value.schemaVersion !== 1 ||
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
    <div className="db-explorer">
      <p className="db-intro">
        {data.tables.length}テーブル · {data.relationships.length}外部キー ·{' '}
        {data.operations.length} API
        <br />
        DDL・API別CRUD・SQL正本をつないで確認できます。SQLは条件分岐・認証・共有処理を含む呼び出し候補です。実行ログではありません。
      </p>
      <div className="db-filters">
        <label>
          テーブル・カラムを検索
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="documents / organization_id"
          />
        </label>
        <label className="db-checkbox">
          <input
            type="checkbox"
            checked={relatedOnly}
            onChange={(e) => setRelatedOnly(e.target.checked)}
          />
          選択テーブルと直接の関係のみ
        </label>
      </div>
      <div className="db-chips" aria-label="テーブル一覧">
        {data.tables
          .filter((t) =>
            [t.name, ...t.columns.map((c) => c.name)].some((s) =>
              s.toLowerCase().includes(search.toLowerCase()),
            ),
          )
          .map((t) => (
            <button key={t.name} aria-pressed={selected === t.name} onClick={() => select(t.name)}>
              {t.name}
            </button>
          ))}
        {!data.tables.some((t) =>
          [t.name, ...t.columns.map((c) => c.name)].some((s) =>
            s.toLowerCase().includes(search.toLowerCase()),
          ),
        ) && <p role="status">一致するテーブルはありません。</p>}
      </div>
      <div className="db-workspace">
        <Graph
          tables={visible}
          relationships={data.relationships}
          selected={selected}
          onSelect={select}
        />
        <article className="db-detail" aria-label="選択テーブルの詳細">
          <h2>{selected}</h2>
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
                      .filter((c) => c.name.toLowerCase().includes(columnSearch.toLowerCase()))
                      .map((c) => (
                        <tr key={c.name}>
                          <th scope="row">
                            {c.name}
                            {c.primaryKey && <b className="db-key">PK</b>}
                            {relations.some(
                              (r) => r.from === selected && r.columns.includes(c.name),
                            ) && <b className="db-key">FK</b>}
                            <details>
                              <summary>列のDDL</summary>
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
              {relations.map((r) => (
                <section className="db-relation" key={r.id}>
                  <button onClick={() => select(r.from)}>{r.from}</button> →{' '}
                  <button onClick={() => select(r.to)}>{r.to}</button>
                  <p>{r.from === selected ? '参照先' : 'このテーブルを参照する側'}</p>
                  {r.columns.map((c, i) => (
                    <div key={c}>
                      <code>{c}</code> → <code>{r.targetColumns[i]}</code>
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
                このテーブルにアクセスするSQL {queries.length}{' '}
                件。SQL内の別テーブルもクリックして移動できます。
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
