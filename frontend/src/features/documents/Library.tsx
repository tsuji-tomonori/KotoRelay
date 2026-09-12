import { useEffect, useState } from 'react';
import { Plus, ArrowRight, BookOpen } from 'lucide-react';
import {
  formatDate,
  publicationLabel,
  statusLabel,
  visibilityLabel,
  type Api,
  type Document,
  type DocumentPage,
  type Identity,
} from '../../lib/api';
import { useUnsaved } from '../../components/layout/Workspace';
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
  const [hasNext, setHasNext] = useState(false);
  const [search, setSearch] = useState('');
  const [department, setDepartment] = useState('');
  const [status, setStatus] = useState('');
  const [filter, setFilter] = useState({ search: '', department: '', status: '' });
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [reload, setReload] = useState(0);
  const [creating, setCreating] = useState(false);
  const [busy, setBusy] = useState(false);
  const [title, setTitle] = useState('');
  const authors = identity.departments.filter((d) =>
    identity.memberships.some((m) => m.department_id === d.id && m.active && m.can_author),
  );
  const [dept, setDept] = useState(authors[0]?.id ?? '');
  const [page, setPage] = useState(0);
  const guard = useUnsaved(creating && !!title);
  useEffect(() => {
    let active = true;
    setLoading(true);
    setFailed(false);
    const params = new URLSearchParams({
      scope: edit ? 'work' : 'read',
      search: filter.search,
      offset: String(page * 30),
      page: 'true',
      status: filter.status,
    });
    if (filter.department) params.set('department_id', filter.department);
    api<DocumentPage>(`/documents?${params}`)
      .then((value) => {
        if (active) {
          setDocs(value.items);
          setHasNext(value.has_next);
        }
      })
      .catch((e) => {
        if (active) {
          setFailed(true);
          onError(String(e));
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [api, edit, filter, page, onError, reload]);
  async function create() {
    setBusy(true);
    try {
      const doc = await api<Document>('/documents', 'POST', { title, department_id: dept });
      guard.markSaved();
      setTitle('');
      setCreating(false);
      onOpen(doc.id);
    } catch (e) {
      onError(String(e));
    } finally {
      setBusy(false);
    }
  }
  function reset() {
    setSearch('');
    setDepartment('');
    setStatus('');
    setFilter({ search: '', department: '', status: '' });
    setPage(0);
  }
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="section-label">{edit ? 'DOCUMENT WORKSPACE' : 'KNOWLEDGE LIBRARY'}</span>
          <h1>{edit ? '執筆' : 'ドキュメント'}</h1>
          <p>
            {edit
              ? '下書きを整えて、確認できる一つの版として申請します。'
              : 'あなたが閲覧できる、最新の承認済み文書を探せます。'}
          </p>
        </div>
        {edit && (
          <button className="primary" onClick={() => setCreating(!creating)}>
            <Plus size={18} />
            新しい文書
          </button>
        )}
      </div>
      {creating && (
        <section className="panel create-panel">
          <h2>新しい文書を作成</h2>
          <label>
            文書タイトル
            <input value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} />
          </label>
          <label>
            所有部署
            <select value={dept} onChange={(e) => setDept(e.target.value)}>
              {authors.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </label>
          <button
            className="primary"
            disabled={busy || !title.trim() || !dept}
            onClick={() => void create()}
          >
            作成して執筆する
            <ArrowRight size={16} />
          </button>
        </section>
      )}
      <form
        className="panel search-form"
        onSubmit={(e) => {
          e.preventDefault();
          setFilter({ search, department, status });
          setPage(0);
        }}
      >
        <label className="search-field">
          文書を検索
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="タイトルを入力"
            maxLength={200}
          />
        </label>
        <label>
          所有部署
          <select value={department} onChange={(e) => setDepartment(e.target.value)}>
            <option value="">すべての部署</option>
            {(edit ? authors : (identity.directory ?? identity.departments)).map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </label>
        {edit && (
          <label>
            文書の状態
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="">すべての状態</option>
              <option value="active">有効</option>
              <option value="withdrawn">公開停止</option>
            </select>
          </label>
        )}
        <button className="primary">検索する</button>
      </form>
      <div className="section-heading">
        <h2>{edit ? '担当する文書' : '閲覧できる文書'}</h2>
        {!loading && !failed && <span className="muted">このページ {docs.length}件</span>}
      </div>
      {loading ? (
        <p role="status">文書を読み込み中…</p>
      ) : failed ? (
        <div className="alert">
          <p>文書を読み込めませんでした。</p>
          <button className="secondary" onClick={() => setReload(reload + 1)}>
            再試行
          </button>
        </div>
      ) : docs.length === 0 ? (
        <div className="empty panel">
          <BookOpen size={36} />
          <h2>
            {filter.search || filter.department || filter.status
              ? '条件に一致する文書はありません'
              : edit
                ? '担当する文書はまだありません'
                : '閲覧できる文書はまだありません'}
          </h2>
          <button className="secondary" onClick={reset}>
            検索条件を解除
          </button>
        </div>
      ) : (
        <div className="resource-list panel">
          {docs.map((doc) => (
            <article className="resource-item" key={doc.id}>
              <div className="badges">
                <span className="badge green">
                  {doc.published_number
                    ? `承認済み・第${doc.published_number}版`
                    : publicationLabel(doc)}
                </span>
                <span className="badge">{visibilityLabel[doc.visibility]}</span>
                {doc.latest_version_id && !doc.index_ready && (
                  <span className="badge amber">RAG反映未完了</span>
                )}
                {edit && doc.review_status && (
                  <span className="badge">
                    第{doc.review_number}版・{statusLabel(doc.review_status)}
                  </span>
                )}
              </div>
              <h3>
                <a
                  href={`#document-${doc.id}`}
                  onClick={(e) => {
                    e.preventDefault();
                    onOpen(doc.id);
                  }}
                >
                  {doc.title}
                </a>
              </h3>
              {doc.summary && (
                <p className="document-summary">{doc.summary.replace(/^#+\s*/gm, '')}</p>
              )}
              <p className="resource-meta">
                <span>
                  所有部署：
                  {(identity.directory ?? identity.departments).find(
                    (d) => d.id === doc.department_id,
                  )?.name ?? '共有部署'}
                </span>
                <span>
                  {doc.approved_at
                    ? `承認日：${formatDate(doc.approved_at)}`
                    : `更新日：${formatDate(doc.updated_at)}`}
                </span>
              </p>
            </article>
          ))}
        </div>
      )}
      <nav className="pagination" aria-label="文書のページ">
        <button disabled={loading || page === 0} onClick={() => setPage(page - 1)}>
          前へ
        </button>
        <span>{page + 1} ページ</span>
        <button disabled={loading || failed || !hasNext} onClick={() => setPage(page + 1)}>
          次へ
        </button>
      </nav>
    </>
  );
}
