import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import mermaid from 'mermaid';
import './style.css';

type Item = {
  id: string;
  name: string;
  status: string;
  group?: string;
  command?: string;
  detail?: string;
  expected?: string;
  actual?: string;
  covered?: number;
  total?: number;
  metric?: string;
  tool?: string;
  body?: string;
  steps?: { phase: string; text: string; image?: string }[];
  database?: object[];
};
type Category = { items: Item[] };
type Evidence = {
  revision: string;
  runId: string;
  generatedAt: string;
  tests: Category;
  e2e: Category;
  static: Category;
  coverage: Category;
  design: Category;
};
const labels = {
  overview: '概要',
  design: '設計書',
  static: '静的解析',
  coverage: 'カバレッジ',
  tests: '単体テスト',
  e2e: 'E2Eテスト',
};
const statusNames: Record<string, string> = {
  passed: '成功',
  failed: '失敗',
  skipped: 'スキップ',
  'not-run': '未実行',
  flaky: '再試行で成功',
  missing: '証拠不足',
};
mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'neutral' });
function Diagram({ code }: { code: string }) {
  const target = useRef<HTMLDivElement>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    const id = 'diagram-' + crypto.randomUUID();
    void mermaid
      .render(id, code)
      .then(({ svg }) => {
        if (active && target.current) target.current.innerHTML = svg;
      })
      .catch(() => {
        if (active) setError('図の描画に失敗しました。定義を確認してください。');
      });
    return () => {
      active = false;
    };
  }, [code]);
  return (
    <figure>
      <div ref={target} aria-label="設計図" />
      {error && <p role="alert">{error}</p>}
      <details>
        <summary>図の定義</summary>
        <pre>{code}</pre>
      </details>
    </figure>
  );
}
function Documentation({ body }: { body: string }) {
  const headings = Array.from(body.matchAll(/^#{1,3} (.+)$/gm), (m) => m[1]);
  function anchor(value: string) {
    return 'heading-' + encodeURIComponent(value);
  }
  return (
    <>
      <details className="toc" open>
        <summary>この設計書の目次</summary>
        {headings.map((h, i) => (
          <a key={i} href={'#' + anchor(h)}>
            {h}
          </a>
        ))}
      </details>
      <div className="markdown">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children }) => <h2 id={anchor(String(children))}>{children}</h2>,
            h2: ({ children }) => <h3 id={anchor(String(children))}>{children}</h3>,
            h3: ({ children }) => <h4 id={anchor(String(children))}>{children}</h4>,
            code: ({ className, children }) =>
              className === 'language-mermaid' ? (
                <Diagram code={String(children).trim()} />
              ) : (
                <code className={className}>{children}</code>
              ),
            a: ({ href, children }) => (
              <a href={href?.startsWith('https://') ? href : undefined} rel="noopener noreferrer">
                {children}
              </a>
            ),
          }}
        >
          {body}
        </ReactMarkdown>
      </div>
    </>
  );
}
function Portal() {
  const [data, setData] = useState<Evidence | null>(null);
  const [error, setError] = useState('');
  const [category, setCategory] = useState<keyof typeof labels>('overview');
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState('');
  const [zoom, setZoom] = useState('');
  const modal = useRef<HTMLDialogElement>(null);
  const origin = useRef<HTMLButtonElement | null>(null);
  useEffect(() => {
    void fetch('./evidence.json', { cache: 'no-store' })
      .then((r) => {
        if (!r.ok) throw Error('データ取得失敗');
        return r.json();
      })
      .then(setData)
      .catch(() => setError('検証データを読み込めませんでした。'));
  }, []);
  useEffect(() => {
    if (zoom) modal.current?.showModal();
  }, [zoom]);
  if (error)
    return (
      <main>
        <h1>KotoRelay 設計と品質</h1>
        <p role="alert">{error}</p>
      </main>
    );
  if (!data)
    return (
      <main>
        <p role="status">検証データを読み込み中…</p>
      </main>
    );
  const items =
    category === 'overview'
      ? []
      : data[category].items.filter((i) =>
          (i.name + ' ' + i.group + ' ' + (i.body ?? '') + ' ' + i.id)
            .toLowerCase()
            .includes(query.toLowerCase()),
        );
  const current = items.find((i) => i.id === selected) ?? items[0];
  function navigate(value: keyof typeof labels) {
    setCategory(value);
    setQuery('');
    setSelected('');
    window.scrollTo(0, 0);
  }
  const groups = Array.from(new Set(items.map((i) => i.group ?? labels[category])));
  return (
    <>
      <aside className="navigation">
        <a className="brand" href="#" onClick={() => navigate('overview')}>
          <span className="mark">K</span>
          <span>
            KotoRelay<small>設計と品質</small>
          </span>
        </a>
        <p className="eyebrow">PROJECT EVIDENCE</p>
        <nav aria-label="品質ナビゲーション">
          {Object.entries(labels).map(([key, label]) => (
            <button
              key={key}
              aria-current={category === key ? 'page' : undefined}
              onClick={() => navigate(key as keyof typeof labels)}
            >
              {label}
              {key !== 'overview' && (
                <span>
                  {
                    data[key as keyof Omit<Evidence, 'revision' | 'runId' | 'generatedAt'>].items
                      .length
                  }
                </span>
              )}
            </button>
          ))}
        </nav>
        <div className="provenance">
          <span>検証対象のコミット</span>
          <a href={'https://github.com/tsuji-tomonori/KotoRelay/commit/' + data.revision}>
            {data.revision.slice(0, 12)}
          </a>
          <span>{data.runId}</span>
          <time>{new Date(data.generatedAt).toLocaleString('ja-JP')}</time>
        </div>
      </aside>
      <main className="content">
        <header>
          <p className="eyebrow">KOTORELAY / ENGINEERING</p>
          <h1>{labels[category]}</h1>
          <p>実装から生成した設計と、実際に実行した検証の記録。</p>
        </header>
        {category === 'overview' ? (
          <>
            <section className="hero">
              <span className="eyebrow">TRUST THROUGH EVIDENCE</span>
              <h2>
                知識をつなぐ。
                <br />
                確かめたことを、見える形に。
              </h2>
              <p>
                文書の執筆・承認から、現行権限で保護された根拠付きチャットまで。設計、検査、実行結果をひとつの場所で確認できます。
              </p>
            </section>
            <div className="cards">
              {(['tests', 'e2e', 'static', 'coverage'] as const).map((k) => (
                <button className="card" key={k} onClick={() => navigate(k)}>
                  <span>{labels[k]}</span>
                  <strong>
                    {data[k].items.filter((i) => i.status === 'passed').length}
                    <small> / {data[k].items.length}</small>
                  </strong>
                  <span>成功 / 計測項目</span>
                  {data[k].items.some((i) => i.status !== 'passed') && (
                    <b className="status failed">未達の項目があります</b>
                  )}
                </button>
              ))}
            </div>
            <section className="panel">
              <h2>検証の範囲</h2>
              <p>
                Docker
                ComposeのPostgreSQL・FastAPI・AstroをPlaywrightから操作しています。AWS構成はCDK
                synth・cdk-nag・アサーション・スナップショットで検査します。
              </p>
              <p>
                AWSへの実デプロイ、実DSQL・Bedrockの疎通は未実行です。ローカルの回答は抽出型検索であり、Bedrockの生成品質とは区別します。固定の待機計算費用を避ける構成ですが、利用量・保存量によるAWS料金は発生し得ます。
              </p>
            </section>
          </>
        ) : (
          <>
            <label className="search">
              {labels[category]}を検索
              <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="ケース名・キーワードで検索…"
              />
            </label>
            <div className="workspace">
              <aside className="inventory" aria-label="項目一覧">
                {groups.map((group) => (
                  <details open key={group}>
                    <summary>{group}</summary>
                    {items
                      .filter((i) => (i.group ?? labels[category]) === group)
                      .map((item) => (
                        <button
                          key={item.id}
                          aria-current={current?.id === item.id ? 'true' : undefined}
                          onClick={() => setSelected(item.id)}
                        >
                          <span className={'dot ' + item.status} />
                          {item.name}
                        </button>
                      ))}
                  </details>
                ))}
                {!items.length && <p>一致する項目はありません。</p>}
              </aside>
              {current && (
                <article className="panel detail" key={current.id}>
                  <div className="detail-heading">
                    <h2>{current.name}</h2>
                    <span className={'status ' + current.status}>
                      {statusNames[current.status]}
                    </span>
                  </div>
                  {current.command && <pre className="command">{current.command}</pre>}
                  {current.detail && <p>{current.detail}</p>}
                  {current.covered !== undefined && current.total !== undefined && (
                    <div className="coverage">
                      <strong>
                        {current.total ? ((current.covered / current.total) * 100).toFixed(2) : '—'}
                        <small>%</small>
                      </strong>
                      <p>
                        {current.covered} / {current.total} · {current.metric} · {current.tool}
                      </p>
                      <progress max={current.total || 1} value={current.covered} />
                    </div>
                  )}
                  {current.expected && (
                    <p>
                      <b>期待結果: </b>
                      {current.expected}
                    </p>
                  )}
                  {current.actual && (
                    <p>
                      <b>実測結果: </b>
                      {current.actual}
                    </p>
                  )}
                  {current.body && <Documentation body={current.body} />}
                  <div className="steps">
                    {current.steps?.map((step, i) => (
                      <section className="step" key={i}>
                        <div className="phase">{step.phase}</div>
                        <p>{step.text}</p>
                        {step.image && (
                          <button
                            className="screenshot"
                            aria-label={step.phase + 'のスクリーンショットを拡大'}
                            onClick={(e) => {
                              origin.current = e.currentTarget;
                              setZoom(step.image!);
                            }}
                          >
                            <img
                              src={step.image}
                              alt={step.phase + ': ' + step.text}
                              loading="lazy"
                            />
                          </button>
                        )}
                      </section>
                    ))}
                  </div>
                  {current.database?.map((state, i) => (
                    <details className="database" key={i} open>
                      <summary>DB状態（架空のテスト文書のみ）</summary>
                      <pre>{JSON.stringify(state, null, 2)}</pre>
                    </details>
                  ))}
                  <details className="identifier">
                    <summary>検証ID</summary>
                    <code>{current.id}</code>
                  </details>
                </article>
              )}
            </div>
          </>
        )}
        <footer>KotoRelay · 実行結果は同一runのcollectorと照合して公開しています。</footer>
      </main>
      <dialog
        ref={modal}
        onClose={() => {
          setZoom('');
          origin.current?.focus();
        }}
        aria-label="スクリーンショット拡大"
      >
        <button onClick={() => modal.current?.close()} autoFocus>
          閉じる（Esc）
        </button>
        <img src={zoom || undefined} alt="検証スクリーンショットの拡大" />
      </dialog>
    </>
  );
}
createRoot(document.getElementById('root')!).render(<Portal />);
