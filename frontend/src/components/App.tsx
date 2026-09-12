import { useEffect, useMemo, useState } from 'react';
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronLeft,
  FileText,
  GitBranch,
  Layers,
  LogOut,
  MessageSquare,
  PenLine,
  Plus,
  RefreshCw,
  Search,
  Send,
  Settings2,
  ShieldCheck,
  Sparkles,
  Users,
} from 'lucide-react';
import {
  createApi,
  formatDate,
  getImage,
  personaNames,
  statusLabel,
  type Api,
  type Document,
  type Identity,
  type Draft,
  type ReadDocument,
  type Version,
  type Submission,
  type Review,
  type Placement,
  type Ocr,
  type Region,
  type Answer,
  type Job,
  type Metrics,
} from '../lib/api';
import Markdown from './Markdown';

type Screen = 'library' | 'work' | 'reviews' | 'chat' | 'groups' | 'operations';
const navigation = [
  { id: 'library', label: 'ドキュメント', icon: BookOpen },
  { id: 'work', label: '執筆ワークスペース', icon: PenLine },
  { id: 'reviews', label: '承認・レビュー', icon: ShieldCheck },
  { id: 'chat', label: 'ナレッジチャット', icon: MessageSquare },
  { id: 'groups', label: '部署管理', icon: Users },
  { id: 'operations', label: '反映ジョブ', icon: Settings2 },
] as const;

export default function App() {
  const [token, setToken] = useState(sessionStorage.getItem('kotorelay-token') ?? '');
  const [identity, setIdentity] = useState<Identity | null>(null);
  const [screen, setScreen] = useState<Screen>('library');
  const [error, setError] = useState('');
  const [selected, setSelected] = useState<string | null>(null);
  const api = useMemo(() => createApi(token), [token]);
  useEffect(() => {
    if (!token) return;
    let active = true;
    api<Identity>('/groups/me')
      .then((value) => {
        if (active) {
          setIdentity(value);
          setError('');
        }
      })
      .catch((e) => {
        if (active) {
          setError(String(e));
          setIdentity(null);
        }
      });
    return () => {
      active = false;
    };
  }, [api, token]);
  function login(value: string) {
    sessionStorage.setItem('kotorelay-token', value);
    setIdentity(null);
    setToken(value);
    setSelected(null);
  }
  function logout() {
    sessionStorage.removeItem('kotorelay-token');
    setToken('');
    setIdentity(null);
    setSelected(null);
  }
  if (!token || !identity)
    return <Login onLogin={login} error={error} loading={!!token && !error} />;
  const visible = navigation.filter((item) => item.id !== 'operations' || identity.user.operator);
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a
          href="#"
          className="brand"
          onClick={() => {
            setScreen('library');
            setSelected(null);
          }}
        >
          <span className="brand-icon">
            <Layers size={25} />
          </span>
          <span>
            KotoRelay<small>知識を、つなぐ。</small>
          </span>
        </a>
        <div className="workspace-label">KNOWLEDGE WORKSPACE</div>
        <nav aria-label="メインナビゲーション">
          {visible.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={`nav-item ${screen === id ? 'active' : ''}`}
              onClick={() => {
                setScreen(id);
                setSelected(null);
                setError('');
              }}
            >
              <Icon size={19} />
              {label}
              {screen === id && <span className="nav-dot" />}
            </button>
          ))}
        </nav>
        <div className="sidebar-note">
          <GitBranch size={19} />
          <strong>信頼できる知識の循環</strong>
          <p>
            書く、レビューする、共有する。
            <br />
            承認済みの知識だけをAIへ。
          </p>
        </div>
        <div className="user-card">
          <span className="avatar">{identity.user.display_name.slice(0, 1)}</span>
          <span>
            <strong>{identity.user.display_name}</strong>
            <small>{identity.departments.map((d) => d.name).join('・')}</small>
          </span>
          <button aria-label="ログアウト" onClick={logout}>
            <LogOut size={17} />
          </button>
        </div>
      </aside>
      <main className="main">
        <header className="topbar">
          <span>
            KotoRelay{' '}
            <span className="crumb">/ {navigation.find((n) => n.id === screen)?.label}</span>
          </span>
          <span className="environment">
            <span />
            {identity.mode === 'local' ? 'LOCAL WORKSPACE' : 'AWS WORKSPACE'}
          </span>
        </header>
        <div className="content">
          {error && (
            <div role="alert" className="alert">
              <span>{error}</span>
              <button onClick={() => setError('')}>閉じる</button>
            </div>
          )}
          {selected ? (
            <DocumentPanel
              key={selected}
              id={selected}
              api={api}
              token={token}
              identity={identity}
              edit={screen === 'work'}
              onBack={() => setSelected(null)}
              onError={setError}
            />
          ) : screen === 'library' || screen === 'work' ? (
            <Library
              api={api}
              identity={identity}
              edit={screen === 'work'}
              onOpen={setSelected}
              onError={setError}
            />
          ) : screen === 'reviews' ? (
            <Reviews api={api} token={token} onError={setError} />
          ) : screen === 'chat' ? (
            <Chat api={api} identity={identity} onOpen={setSelected} onError={setError} />
          ) : screen === 'groups' ? (
            <Groups api={api} identity={identity} onError={setError} />
          ) : (
            <Operations api={api} onError={setError} />
          )}
        </div>
        <footer>
          © KotoRelay <span>承認された知識を、次の一歩へ。</span>
        </footer>
      </main>
    </div>
  );
}

export function Login({
  onLogin,
  error,
  loading,
}: {
  onLogin: (token: string) => void;
  error: string;
  loading: boolean;
}) {
  const [persona, setPersona] = useState('author');
  const [accessToken, setAccessToken] = useState('');
  return (
    <div className="login-page">
      <div className="login-intro">
        <span className="brand light">
          <Layers /> KotoRelay
        </span>
        <p className="eyebrow">YOUR TEAM'S LIVING KNOWLEDGE</p>
        <h1>
          書いた知識が、
          <br />
          次の誰かの
          <br />
          <em>力になる。</em>
        </h1>
        <p>
          人のレビューを経た確かな知識を、
          <br />
          チームとAIへ引き継ぐワークスペース。
        </p>
        <div className="flow-pills">
          <span>01 執筆</span>
          <ArrowRight />
          <span>02 承認</span>
          <ArrowRight />
          <span>03 活用</span>
        </div>
      </div>
      <section className="login-card">
        <span className="section-label">WELCOME TO KOTORELAY</span>
        <h2>ワークスペースを開く</h2>
        <p className="muted">ローカルでは架空の利用者で業務フローを確認できます。</p>
        {error && (
          <p className="alert" role="alert">
            {error}
          </p>
        )}
        <label>
          サンプルの役割
          <select value={persona} onChange={(e) => setPersona(e.target.value)}>
            {Object.entries(personaNames).map(([key, value]) => (
              <option value={key} key={key}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <button
          className="primary full"
          onClick={() => onLogin(`demo-${persona}`)}
          disabled={loading}
        >
          {loading ? '接続中…' : 'ローカルで始める'}
          <ArrowRight size={18} />
        </button>
        <details>
          <summary>AWS環境のアクセストークンで接続</summary>
          <label>
            アクセストークン
            <input
              type="password"
              value={accessToken}
              onChange={(e) => setAccessToken(e.target.value)}
              autoComplete="off"
            />
          </label>
          <button
            className="secondary"
            disabled={!accessToken}
            onClick={() => onLogin(accessToken)}
          >
            接続
          </button>
        </details>
        <p className="login-caption">
          <ShieldCheck size={16} />
          すべての操作で現在の所属と権限を確認します。
        </p>
      </section>
    </div>
  );
}

export function Library({
  api,
  identity,
  edit,
  onOpen,
  onError,
}: {
  api: Api;
  identity: Identity;
  edit: boolean;
  onOpen: (id: string) => void;
  onError: (message: string) => void;
}) {
  const [docs, setDocs] = useState<Document[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [title, setTitle] = useState('');
  const [dept, setDept] = useState(identity.departments[0]?.id ?? '');
  const [page, setPage] = useState(0);
  useEffect(() => {
    let active = true;
    setLoading(true);
    api<Document[]>(
      `/documents?scope=${edit ? 'work' : 'read'}&search=${encodeURIComponent(search)}&offset=${page * 30}`,
    )
      .then((value) => {
        if (active) setDocs(value);
      })
      .catch((e) => onError(String(e)))
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [api, edit, search, page, onError]);
  async function create() {
    try {
      const doc = await api<Document>('/documents', 'POST', { title, department_id: dept });
      onOpen(doc.id);
    } catch (e) {
      onError(String(e));
    }
  }
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="section-label">{edit ? 'WRITE & REFINE' : 'TEAM KNOWLEDGE'}</span>
          <h1>{edit ? '執筆ワークスペース' : 'ドキュメント'}</h1>
          <p>
            {edit
              ? 'アイデアを言葉にして、チームの知識に育てましょう。'
              : 'レビューを経た、チームの確かな知識を見つける。'}
          </p>
        </div>
        {edit && (
          <button className="primary" onClick={() => setCreating(!creating)}>
            <Plus size={18} />
            新しい文書
          </button>
        )}
      </div>
      {!edit && (
        <div className="knowledge-banner">
          <div className="banner-icon">
            <Sparkles size={28} />
          </div>
          <div>
            <strong>知識は、つながるともっと役に立つ。</strong>
            <p>ここに並ぶのは、あなたが閲覧できる最新の承認版です。</p>
          </div>
          <span className="banner-tag">
            <ShieldCheck size={15} />
            REVIEWED KNOWLEDGE
          </span>
        </div>
      )}
      {creating && (
        <section className="panel create-panel">
          <h2>新しい文書を作成</h2>
          <label>
            文書タイトル
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              maxLength={200}
              placeholder="例: チームの開発ガイド"
            />
          </label>
          <label>
            所有部署
            <select value={dept} onChange={(e) => setDept(e.target.value)}>
              {identity.departments
                .filter((d) =>
                  identity.memberships.some((m) => m.department_id === d.id && m.can_author),
                )
                .map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
            </select>
          </label>
          <button
            className="primary"
            disabled={!title.trim() || !dept}
            onClick={() => void create()}
          >
            作成して執筆する
            <ArrowRight size={16} />
          </button>
        </section>
      )}
      <div className="list-toolbar">
        <div className="tabs">
          <span className="selected">{edit ? '担当する文書' : 'すべての文書'}</span>
          <span className="count">{docs.length}</span>
        </div>
        <label className="search-box">
          <Search size={18} />
          <input
            aria-label="文書を検索"
            placeholder="タイトルで検索…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
          />
        </label>
      </div>
      {loading ? (
        <p role="status">読み込み中…</p>
      ) : docs.length === 0 ? (
        <div className="empty">
          <BookOpen size={42} />
          <h2>{search ? '一致する文書がありません' : '知識の最初の一枚を。'}</h2>
          <p>
            {edit
              ? '「新しい文書」から、チームの知識を書き始めましょう。'
              : '承認された文書が、ここに並びます。'}
          </p>
        </div>
      ) : (
        <div className="document-grid">
          {docs.map((doc) => (
            <button className="document-card" key={doc.id} onClick={() => onOpen(doc.id)}>
              <div className="card-top">
                <span className="document-icon">
                  <FileText size={24} />
                </span>
                <span className={`badge ${doc.latest_version_id ? 'green' : 'amber'}`}>
                  {doc.latest_version_id ? '承認版あり' : '下書き'}
                </span>
              </div>
              <h2>{doc.title}</h2>
              <p>
                {identity.departments.find((d) => d.id === doc.department_id)?.name ??
                  '共有された文書'}
              </p>
              <div className="card-bottom">
                <span>{formatDate(doc.updated_at)}</span>
                <ArrowRight size={18} />
              </div>
            </button>
          ))}
        </div>
      )}
      <div className="pagination">
        <button disabled={page === 0} onClick={() => setPage(page - 1)}>
          前へ
        </button>
        <span>{page + 1} ページ</span>
        <button disabled={docs.length < 30} onClick={() => setPage(page + 1)}>
          次へ
        </button>
      </div>
    </>
  );
}

export function DocumentPanel({
  id,
  api,
  token,
  identity,
  edit,
  onBack,
  onError,
}: {
  id: string;
  api: Api;
  token: string;
  identity: Identity;
  edit: boolean;
  onBack: () => void;
  onError: (message: string) => void;
}) {
  const [draft, setDraft] = useState<Draft | null>(null);
  const [read, setRead] = useState<ReadDocument | null>(null);
  const [body, setBody] = useState('');
  const [title, setTitle] = useState('');
  const [dirty, setDirty] = useState(false);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [history, setHistory] = useState<{ version: Version; submission: Submission }[]>([]);
  const [diff, setDiff] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [placements, setPlacements] = useState<Placement[]>([]);
  useEffect(() => {
    let active = true;
    (edit ? api<Draft>(`/documents/${id}/draft`) : api<ReadDocument>(`/documents/${id}`))
      .then((value) => {
        if (!active) return;
        if (edit) {
          const d = value as Draft;
          setDraft(d);
          setBody(d.body);
          setTitle(d.document.title);
          setPlacements(d.placements);
        } else {
          const d = value as ReadDocument;
          setRead(d);
          setBody(d.body);
          setTitle(d.version.title);
          const manifest = JSON.parse(d.version.manifest) as { images: { placement: Placement }[] };
          setPlacements(manifest.images.map((i) => i.placement));
          if (identity.departments[0])
            void api(`/metrics/views/${id}`, 'POST', {
              id: crypto.randomUUID(),
              department_id: identity.departments[0].id,
            }).catch((e) => onError(String(e)));
        }
      })
      .catch((e) => onError(String(e)));
    return () => {
      active = false;
    };
  }, [api, id, edit, identity, onError]);
  useEffect(() => {
    const prevent = (event: BeforeUnloadEvent) => {
      if (dirty) event.preventDefault();
    };
    window.addEventListener('beforeunload', prevent);
    return () => window.removeEventListener('beforeunload', prevent);
  }, [dirty]);
  async function save() {
    if (!draft) return;
    setBusy(true);
    try {
      const d = await api<Draft>(`/documents/${id}/draft`, 'PUT', {
        title,
        body,
        revision: draft.revision,
        placements,
      });
      setDraft(d);
      setDirty(false);
      setMessage('保存しました。');
    } catch (e) {
      setMessage('未保存の変更があります。入力は保持されています。');
      onError(String(e));
    } finally {
      setBusy(false);
    }
  }
  async function submit() {
    if (!draft) return;
    setBusy(true);
    try {
      const version = await api<Version>(
        `/documents/${id}/submissions`,
        'POST',
        { revision: draft.revision },
        crypto.randomUUID(),
      );
      setMessage(`v${version.number} を承認申請しました。`);
    } catch (e) {
      onError(String(e));
    } finally {
      setBusy(false);
    }
  }
  async function loadHistory() {
    try {
      setHistory(await api(`/documents/${id}/history`));
      setShowHistory(true);
    } catch (e) {
      onError(String(e));
    }
  }
  async function compare(left: string, right: string) {
    try {
      const result = await api<{ diff: string }>(
        `/documents/${id}/diff?left=${left}&right=${right}`,
      );
      setDiff(result.diff);
    } catch (e) {
      onError(String(e));
    }
  }
  return (
    <>
      <button
        className="back"
        onClick={() => {
          if (!dirty || window.confirm('未保存の変更があります。戻りますか。')) onBack();
        }}
      >
        <ChevronLeft size={16} />
        文書一覧へ
      </button>
      <div className="page-heading">
        <div>
          <span className="section-label">{edit ? 'DOCUMENT EDITOR' : 'APPROVED DOCUMENT'}</span>
          <h1>{title || '読み込み中…'}</h1>
          <p>
            {edit
              ? 'Markdownで執筆し、保存してから承認を申請します。'
              : read
                ? `v${read.version.number} · ${read.index_ready ? 'RAGへ反映済み' : 'RAGへの反映待ち'}`
                : ''}
          </p>
        </div>
        {edit && (
          <div className="actions">
            <button className="secondary" onClick={() => void loadHistory()}>
              <GitBranch size={16} />
              版履歴
            </button>
            <button className="secondary" disabled={busy || !draft} onClick={() => void save()}>
              保存
            </button>
            <button
              className="primary"
              disabled={busy || dirty || !draft}
              onClick={() => void submit()}
            >
              <Send size={16} />
              承認申請
            </button>
          </div>
        )}
      </div>
      {edit && (
        <div className="save-status" role="status">
          <span className={dirty ? 'amber-text' : 'green-text'}>
            {dirty ? '● 未保存の変更' : '✓ 保存済み'}
          </span>
          {message && <span>{message}</span>}
        </div>
      )}
      {edit ? (
        <section className="editor panel">
          <label className="editor-title">
            タイトル
            <input
              aria-label="文書タイトル"
              value={title}
              maxLength={200}
              onChange={(e) => {
                setTitle(e.target.value);
                setDirty(true);
              }}
            />
          </label>
          <div className="editor-columns">
            <div>
              <div className="editor-label">MARKDOWN</div>
              <textarea
                aria-label="Markdown本文"
                disabled={!draft || busy}
                value={body}
                onChange={(e) => {
                  setBody(e.target.value);
                  setDirty(true);
                }}
                placeholder="# はじめに&#10;&#10;チームに伝えたいことを書きましょう。"
              />
            </div>
            <div className="preview">
              <div className="editor-label">PREVIEW</div>
              <PlacedDocument
                body={body}
                placements={placements}
                token={token}
                version={read?.version.id}
              />
            </div>
          </div>
        </section>
      ) : (
        <section className="panel article">
          <PlacedDocument
            body={body}
            placements={placements}
            token={token}
            version={read?.version.id}
          />
        </section>
      )}
      <Images
        api={api}
        token={token}
        documentId={id}
        versionId={read?.version.id}
        edit={edit}
        placements={placements}
        onChange={(next) => {
          setPlacements(next);
          setDirty(true);
        }}
        offset={body.length}
        onError={onError}
      />
      {showHistory && (
        <section className="panel">
          <h2>版履歴</h2>
          {history.map((item, index) => (
            <div className="history-row" key={item.version.id}>
              <span>v{item.version.number}</span>
              <span className="badge">{statusLabel(item.submission.status)}</span>
              <span>{formatDate(item.version.created_at)}</span>
              <span>{item.submission.reason}</span>
              {index < history.length - 1 && (
                <button
                  onClick={() => void compare(history[index + 1]!.version.id, item.version.id)}
                >
                  前の版と比較
                </button>
              )}
            </div>
          ))}
          {diff && <pre className="diff">{diff}</pre>}
        </section>
      )}
    </>
  );
}

export function PlacedDocument({
  body,
  placements,
  token,
  version,
}: {
  body: string;
  placements: Placement[];
  token: string;
  version?: string;
}) {
  const sorted = [...placements].sort((a, b) => a.offset - b.offset);
  let offset = 0;
  const parts = sorted.map((p) => {
    const end = Math.min(body.length, Math.max(offset, p.offset));
    const text = body.slice(offset, end);
    offset = end;
    return (
      <div key={p.id}>
        <Markdown body={text} />
        <figure>
          <ProtectedImage token={token} id={p.asset_id} version={version} />
          <figcaption>{p.heading}</figcaption>
        </figure>
      </div>
    );
  });
  return (
    <>
      {parts}
      <Markdown body={body.slice(offset)} />
    </>
  );
}

export function ProtectedImage({
  token,
  id,
  version,
}: {
  token: string;
  id: string;
  version?: string;
}) {
  const [url, setUrl] = useState('');
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    let active = true;
    let objectUrl = '';
    getImage(token, id, version)
      .then((value) => {
        objectUrl = value;
        if (active) setUrl(value);
        else URL.revokeObjectURL(value);
      })
      .catch(() => setFailed(true));
    return () => {
      active = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [token, id, version]);
  return failed ? (
    <p>画像を表示できません。</p>
  ) : url ? (
    <img src={url} alt="文書の添付画像" />
  ) : (
    <span>画像を読み込み中…</span>
  );
}

export function Images({
  api,
  token,
  documentId,
  versionId,
  edit,
  placements,
  onChange,
  offset,
  onError,
}: {
  api: Api;
  token: string;
  documentId: string;
  versionId?: string;
  edit: boolean;
  placements: Placement[];
  onChange: (p: Placement[]) => void;
  offset: number;
  onError: (message: string) => void;
}) {
  const [ocr, setOcr] = useState<Record<string, Ocr>>({});
  const [text, setText] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  useEffect(() => {
    let active = true;
    Promise.all(
      placements.map(
        async (p) =>
          [
            p.id,
            await api<Ocr>(
              `/images/ocr/${p.ocr_run_id}${versionId ? `?version_id=${versionId}` : ''}`,
            ),
          ] as const,
      ),
    )
      .then((results) => {
        if (active) {
          setOcr(Object.fromEntries(results));
          setText(
            Object.fromEntries(
              results.map(([key, value]) => [key, value.regions.map((r) => r.text).join('\n')]),
            ),
          );
        }
      })
      .catch((e) => onError(String(e)));
    return () => {
      active = false;
    };
  }, [api, placements, versionId, onError]);
  async function upload(file: File) {
    setBusy(true);
    try {
      const form = new FormData();
      form.append('file', file);
      const result = await api<{ asset: { id: string }; ocr_run: { id: string }; ocr: Ocr }>(
        `/images/documents/${documentId}`,
        'POST',
        form,
      );
      onChange([
        ...placements,
        {
          id: crypto.randomUUID(),
          asset_id: result.asset.id,
          ocr_run_id: result.ocr_run.id,
          offset,
          heading: '添付画像',
        },
      ]);
    } catch (e) {
      onError(String(e));
    } finally {
      setBusy(false);
    }
  }
  async function confirm(p: Placement) {
    try {
      const existing = ocr[p.id]?.regions ?? [];
      const lines = (text[p.id] ?? '').split('\n').filter(Boolean);
      const regions: Region[] = lines.map((line, index) => ({
        ...(existing[index] ?? { x: 0, y: 0, width: 1, height: 1, confidence: 1 }),
        text: line,
        order: index,
      }));
      const result = await api<{ ocr_run: { id: string } }>(`/images/${p.asset_id}/ocr`, 'POST', {
        regions,
        confirmed: true,
      });
      onChange(
        placements.map((value) =>
          value.id === p.id ? { ...value, ocr_run_id: result.ocr_run.id } : value,
        ),
      );
      setNotice('OCRを確認しました。文書を保存してください。');
    } catch (e) {
      onError(String(e));
    }
  }
  return (
    <section className="panel images-panel">
      {notice && <p role="status">{notice}</p>}
      <div className="section-heading">
        <h2>
          添付画像・OCR <span className="count">{placements.length}</span>
        </h2>
        {edit && (
          <label className="upload-button">
            {busy ? '処理中…' : '画像を添付'}
            <input
              aria-label="画像を添付"
              type="file"
              accept="image/png,image/jpeg"
              disabled={busy}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) void upload(file);
              }}
            />
          </label>
        )}
      </div>
      {placements.length === 0 ? (
        <p className="muted">
          {edit
            ? 'PNG / JPEG · 5 MBまで · OCRの文字と位置を確認して申請できます。'
            : '添付画像はありません。'}
        </p>
      ) : (
        placements.map((p) => (
          <div className="image-review" key={p.id}>
            <div className="image-frame">
              <ProtectedImage token={token} id={p.asset_id} version={versionId} />
              <div className="ocr-overlay">
                {ocr[p.id]?.regions.map((r, i) => (
                  <span
                    key={i}
                    title={r.text}
                    style={{
                      left: `${r.x * 100}%`,
                      top: `${r.y * 100}%`,
                      width: `${r.width * 100}%`,
                      height: `${r.height * 100}%`,
                    }}
                  />
                ))}
              </div>
            </div>
            <div>
              <p className="muted">
                挿入位置: {p.offset}文字目 · {p.heading}
              </p>
              {edit ? (
                <>
                  <label>
                    OCR文字
                    <textarea
                      aria-label="OCR文字"
                      value={text[p.id] ?? ''}
                      onChange={(e) => setText({ ...text, [p.id]: e.target.value })}
                    />
                  </label>
                  <p className="muted">
                    {ocr[p.id]?.status === 'failed'
                      ? 'OCRに失敗しました。文字を入力して確認してください。'
                      : '画像上の枠が文字の検出位置です。'}
                  </p>
                  <div className="actions">
                    <button className="secondary" onClick={() => void confirm(p)}>
                      OCRを確認して確定
                    </button>
                    <button
                      onClick={() => onChange(placements.filter((value) => value.id !== p.id))}
                    >
                      配置を削除
                    </button>
                  </div>
                </>
              ) : (
                <p>{ocr[p.id]?.regions.map((r) => r.text).join(' ')}</p>
              )}
            </div>
          </div>
        ))
      )}
    </section>
  );
}

export function Reviews({
  api,
  token,
  onError,
}: {
  api: Api;
  token: string;
  onError: (message: string) => void;
}) {
  const [items, setItems] = useState<Review[]>([]);
  const [selected, setSelected] = useState<Review | null>(null);
  const [read, setRead] = useState<ReadDocument | null>(null);
  const [reason, setReason] = useState('');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    api<Review[]>('/reviews')
      .then(setItems)
      .catch((e) => onError(String(e)));
  }, [api, onError, message]);
  async function open(item: Review) {
    try {
      setRead(
        await api(
          `/documents/${item.submission.document_id}?version_id=${item.submission.version_id}`,
        ),
      );
      setSelected(item);
      setReason('');
    } catch (e) {
      onError(String(e));
    }
  }
  async function decide(decision: string) {
    if (!selected) return;
    setBusy(true);
    try {
      await api(
        `/reviews/${selected.submission.id}/decision`,
        'POST',
        { manifest_hash: selected.submission.manifest_hash, decision, reason },
        crypto.randomUUID(),
      );
      setMessage(`${selected.title} を${decision === 'approved' ? '承認' : '却下'}しました。`);
      setSelected(null);
      setRead(null);
    } catch (e) {
      onError(String(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="section-label">HUMAN REVIEW</span>
          <h1>承認・レビュー</h1>
          <p>特定の版と画像・OCRを確認して、知識をチームへ届けます。</p>
        </div>
        <ShieldCheck className="heading-icon" size={42} />
      </div>
      {message && (
        <p className="success" role="status">
          {message}
        </p>
      )}
      {selected && read ? (
        <section className="panel">
          <button className="back" onClick={() => setSelected(null)}>
            一覧へ戻る
          </button>
          <h2>
            {read.version.title} · v{read.version.number}
          </h2>
          <p className="hash">manifest: {selected.submission.manifest_hash}</p>
          <Markdown body={read.body} />
          <Images
            api={api}
            token={token}
            documentId={read.document.id}
            versionId={read.version.id}
            edit={false}
            placements={(
              JSON.parse(read.version.manifest) as { images: { placement: Placement }[] }
            ).images.map((i) => i.placement)}
            onChange={() => {}}
            offset={0}
            onError={onError}
          />
          <label>
            審査コメント（却下時は必須）
            <textarea
              aria-label="審査コメント"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              maxLength={2000}
            />
          </label>
          <div className="actions">
            <button className="primary" disabled={busy} onClick={() => void decide('approved')}>
              この版を承認
            </button>
            <button
              className="danger"
              disabled={busy || !reason.trim()}
              onClick={() => void decide('rejected')}
            >
              理由を残して却下
            </button>
          </div>
        </section>
      ) : (
        <section className="panel">
          {items.length === 0 ? (
            <div className="empty">
              <CheckCircle2 size={38} />
              <h2>審査対象はありません</h2>
              <p>申請された文書がここに表示されます。</p>
            </div>
          ) : (
            items.map((item) => (
              <div className="review-row" key={item.submission.id}>
                <FileText size={22} />
                <div>
                  <strong>{item.title}</strong>
                  <small>
                    {formatDate(item.submission.created_at)}
                    {item.submission.reason && ` · ${item.submission.reason}`}
                  </small>
                </div>
                <span className="badge">{statusLabel(item.submission.status)}</span>
                {item.can_review && item.submission.status === 'pending' && (
                  <button className="secondary" onClick={() => void open(item)}>
                    内容を確認
                    <ArrowRight size={15} />
                  </button>
                )}
              </div>
            ))
          )}
        </section>
      )}
    </>
  );
}

export function Chat({
  api,
  identity,
  onOpen,
  onError,
}: {
  api: Api;
  identity: Identity;
  onOpen: (id: string) => void;
  onError: (message: string) => void;
}) {
  const [question, setQuestion] = useState('');
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [conversation, setConversation] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [department, setDepartment] = useState(identity.departments[0]?.id ?? '');
  async function ask() {
    setBusy(true);
    try {
      const answer = await api<Answer>(
        '/chat',
        'POST',
        { question, department_id: department, conversation_id: conversation },
        crypto.randomUUID(),
      );
      setConversation(answer.conversation_id);
      setAnswers([...answers, answer]);
      setQuestion('');
    } catch (e) {
      onError(String(e));
    } finally {
      setBusy(false);
    }
  }
  async function refresh() {
    if (conversation)
      try {
        setAnswers(await api(`/chat/${conversation}`));
      } catch (e) {
        onError(String(e));
      }
  }
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="section-label">ASK YOUR KNOWLEDGE</span>
          <h1>ナレッジチャット</h1>
          <p>あなたが閲覧できる最新承認版から、根拠をたどれる回答を。</p>
        </div>
        <button className="secondary" disabled={!conversation} onClick={() => void refresh()}>
          <RefreshCw size={16} />
          履歴を再確認
        </button>
      </div>
      <div className="chat-panel panel">
        {answers.length === 0 ? (
          <div className="chat-welcome">
            <span className="chat-spark">
              <Sparkles size={32} />
            </span>
            <h2>知りたいことを、聞いてみましょう。</h2>
            <p>
              根拠が足りない場合は、回答を保留します。
              <br />
              権限外の文書や未承認版は使いません。
            </p>
          </div>
        ) : (
          <div aria-live="polite" className="messages">
            {answers.map((answer) => (
              <article key={answer.id}>
                <div className="question-bubble">{answer.question}</div>
                <div className="answer-bubble">
                  <span className="answer-title">
                    <Sparkles size={17} /> KotoRelay{' '}
                    <span className="badge">{statusLabel(answer.status)}</span>
                  </span>
                  <Markdown body={answer.answer} />
                  {answer.citations.length > 0 && (
                    <div className="citations">
                      <small>参照した承認版</small>
                      {answer.citations.map((c) => (
                        <button key={c.chunk_id} onClick={() => onOpen(c.document_id)}>
                          <FileText size={14} />
                          {c.title} · {c.heading}
                          <ArrowRight size={13} />
                        </button>
                      ))}
                    </div>
                  )}
                  <small className="muted">{answer.model}</small>
                </div>
              </article>
            ))}
          </div>
        )}
        <form
          className="chat-composer"
          onSubmit={(e) => {
            e.preventDefault();
            void ask();
          }}
        >
          <label className="department-selector">
            利用部署
            <select value={department} onChange={(e) => setDepartment(e.target.value)}>
              {identity.departments.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </label>
          <div className="composer-input">
            <textarea
              aria-label="質問"
              placeholder="例: 開発フローについて教えてください"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              maxLength={2000}
            />
            <button aria-label="質問を送信" className="primary" disabled={busy || !question.trim()}>
              {busy ? '回答中…' : <Send size={19} />}
            </button>
          </div>
          <small>
            {identity.mode === 'local'
              ? 'ローカルでは検索した資料の抜粋を表示します。画像の意味理解はAWS接続時に利用できます。'
              : 'Bedrockによる回答です。引用元もあわせて確認してください。'}
          </small>
        </form>
      </div>
    </>
  );
}

export function Groups({
  api,
  identity,
  onError,
}: {
  api: Api;
  identity: Identity;
  onError: (message: string) => void;
}) {
  const allowed = identity.departments.filter((d) =>
    identity.memberships.some((m) => m.department_id === d.id && m.leader),
  );
  const [department, setDepartment] = useState(allowed[0]?.id ?? '');
  const [docs, setDocs] = useState<Document[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [members, setMembers] = useState<
    { membership: Identity['memberships'][number]; display_name: string }[]
  >([]);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    if (!department) return;
    const start = new Date();
    start.setDate(start.getDate() - 30);
    Promise.all([
      api<Document[]>('/documents?scope=manage'),
      api<Metrics>(
        `/metrics/${department}?start=${start.toISOString()}&end=${new Date().toISOString()}`,
      ),
      api<typeof members>(`/groups/${department}/members`),
    ])
      .then(([d, m, u]) => {
        setDocs(d);
        setMetrics(m);
        setMembers(u);
      })
      .catch((e) => onError(String(e)));
  }, [api, department, onError, revision]);
  async function policy(doc: Document, status: string) {
    if (status === 'deleted' && !window.confirm(`「${doc.title}」を削除し、配信を停止しますか。`))
      return;
    try {
      await api(`/documents/${doc.id}/policy`, 'PUT', {
        revision: doc.revision,
        visibility: doc.visibility,
        shared_departments: JSON.parse(doc.shared_departments),
        status,
      });
      setRevision(revision + 1);
    } catch (e) {
      onError(String(e));
    }
  }
  async function share(doc: Document, visibility: string, departments: string[] = []) {
    try {
      await api(`/documents/${doc.id}/policy`, 'PUT', {
        revision: doc.revision,
        visibility,
        shared_departments: departments,
        status: doc.status,
      });
      setRevision(revision + 1);
    } catch (e) {
      onError(String(e));
    }
  }
  async function revoke(member: (typeof members)[number]) {
    try {
      const m = member.membership;
      await api('/groups/memberships', 'PUT', {
        user_id: m.user_id,
        department_id: m.department_id,
        leader: m.leader,
        can_author: m.can_author,
        can_review: m.can_review,
        active: !m.active,
      });
      setRevision(revision + 1);
    } catch (e) {
      onError(String(e));
    }
  }
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="section-label">TEAM ADMINISTRATION</span>
          <h1>部署管理</h1>
          <p>所有する文書、所属、知識の利用状況を確認します。</p>
        </div>
      </div>
      {!department ? (
        <div className="empty">
          <Users size={36} />
          <h2>部署リーダー向けの画面です</h2>
          <p>管理権限のある部署がありません。</p>
        </div>
      ) : (
        <>
          <label>
            管理部署
            <select value={department} onChange={(e) => setDepartment(e.target.value)}>
              {allowed.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </label>
          {metrics && (
            <>
              <div className="stats-grid">
                {[
                  ['質問受付数', metrics.questions],
                  ['文書閲覧数', metrics.views],
                  ['ユニーク閲覧者', metrics.unique_viewers],
                ].map(([label, value]) => (
                  <div className="stat panel" key={label}>
                    <span>{label}</span>
                    <strong>{value}</strong>
                    <small>過去30日間</small>
                  </div>
                ))}
              </div>
              <p className="muted">
                集計時刻: {formatDate(metrics.generated_at)} · {metrics.timezone} · 回答{' '}
                {metrics.outcomes.answered} / 保留 {metrics.outcomes.held} / 失敗{' '}
                {metrics.outcomes.failed}
              </p>
            </>
          )}
          <section className="panel">
            <h2>所有文書</h2>
            {docs.map((doc) => (
              <div className="manage-row" key={doc.id}>
                <div>
                  <strong>{doc.title}</strong>
                  <small>{statusLabel(doc.status)}</small>
                </div>
                <label>
                  公開範囲
                  <select
                    aria-label={`${doc.title}の公開範囲`}
                    value={doc.visibility}
                    disabled={doc.status === 'deleted'}
                    onChange={(e) => void share(doc, e.target.value)}
                  >
                    <option value="department">所有部署</option>
                    <option value="organization">全組織</option>
                    <option value="selected">指定部署</option>
                  </select>
                </label>
                {doc.visibility === 'selected' && (
                  <fieldset>
                    <legend>共有先部署</legend>
                    {(identity.directory ?? identity.departments).map((dept) => (
                      <label key={dept.id}>
                        <input
                          type="checkbox"
                          aria-label={`${doc.title}を${dept.name}に共有`}
                          checked={(JSON.parse(doc.shared_departments) as string[]).includes(
                            dept.id,
                          )}
                          disabled={doc.status === 'deleted'}
                          onChange={(e) => {
                            const current = JSON.parse(doc.shared_departments) as string[];
                            void share(
                              doc,
                              'selected',
                              e.target.checked
                                ? [...current, dept.id]
                                : current.filter((id) => id !== dept.id),
                            );
                          }}
                        />
                        {dept.name}
                      </label>
                    ))}
                  </fieldset>
                )}
                <span>
                  閲覧 {metrics?.documents.find((d) => d.id === doc.id)?.views ?? 0} / 回答貢献{' '}
                  {metrics?.documents.find((d) => d.id === doc.id)?.contributions ?? 0}
                </span>
                <button
                  disabled={doc.status === 'deleted'}
                  onClick={() =>
                    void policy(doc, doc.status === 'withdrawn' ? 'active' : 'withdrawn')
                  }
                >
                  {doc.status === 'withdrawn' ? '公開を再開' : '公開停止'}
                </button>
                <button
                  className="danger"
                  disabled={doc.status === 'deleted'}
                  onClick={() => void policy(doc, 'deleted')}
                >
                  削除
                </button>
              </div>
            ))}
          </section>
          <section className="panel">
            <h2>部署の所属</h2>
            {members.map((member) => (
              <div className="manage-row" key={member.membership.id}>
                <strong>{member.display_name}</strong>
                <span>
                  {member.membership.can_author ? '執筆 ' : ''}
                  {member.membership.can_review ? '審査 ' : ''}
                  {member.membership.leader ? 'リーダー' : ''}
                </span>
                <button
                  disabled={member.membership.user_id === identity.user.id}
                  onClick={() => void revoke(member)}
                >
                  {member.membership.active ? '所属を停止' : '所属を再開'}
                </button>
              </div>
            ))}
          </section>
        </>
      )}
    </>
  );
}

export function Operations({ api, onError }: { api: Api; onError: (message: string) => void }) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [revision, setRevision] = useState(0);
  const [differences, setDifferences] = useState<{ document_id: string; reason: string }[]>([]);
  useEffect(() => {
    api<Job[]>('/operations/jobs')
      .then(setJobs)
      .catch((e) => onError(String(e)));
  }, [api, onError, revision]);
  async function process(job: Job) {
    try {
      await api(`/operations/jobs/${job.id}`, 'POST');
      setRevision(revision + 1);
    } catch (e) {
      onError(String(e));
    }
  }
  async function reconcile() {
    try {
      setDifferences(await api('/operations/reconcile'));
    } catch (e) {
      onError(String(e));
    }
  }
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="section-label">OPERATIONS</span>
          <h1>反映ジョブ</h1>
          <p>承認と同時に記録された処理を確認し、必要に応じて再実行します。</p>
        </div>
        <button className="secondary" onClick={() => void reconcile()}>
          正本と索引を照合
        </button>
      </div>
      <section className="panel">
        {jobs.length === 0 ? (
          <p className="muted">ジョブはありません。</p>
        ) : (
          jobs.map((job) => (
            <div className="manage-row" key={job.id}>
              <div>
                <strong>{job.kind === 'purge' ? '削除処理' : '検索への反映'}</strong>
                <small>{job.document_id}</small>
              </div>
              <span className="badge">{statusLabel(job.status)}</span>
              <span>{job.attempts} 回</span>
              {job.error_code && <span>{job.error_code}</span>}
              <button
                className="secondary"
                disabled={['done', 'obsolete'].includes(job.status) || job.attempts >= 5}
                onClick={() => void process(job)}
              >
                実行・再処理
              </button>
            </div>
          ))
        )}
      </section>
      {differences.length > 0 && (
        <section className="panel">
          <h2>検出した不一致</h2>
          {differences.map((d, i) => (
            <p key={i}>
              {d.document_id}: {d.reason}
            </p>
          ))}
        </section>
      )}
    </>
  );
}
