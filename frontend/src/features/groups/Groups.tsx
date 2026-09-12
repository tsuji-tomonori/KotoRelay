import { useEffect, useRef, useState } from 'react';
import {
  type Api,
  type Document,
  type DocumentPage,
  type Identity,
  type Metrics,
  formatDate,
  publicationLabel,
  statusLabel,
  visibilityLabel,
} from '../../lib/api';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';
import { useUnsaved } from '../../components/layout/Workspace';
type Member = { membership: Identity['memberships'][number]; display_name: string };
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
    identity.memberships.some((m) => m.department_id === d.id && m.leader && m.active),
  );
  const [department, setDepartment] = useState(allowed[0]?.id ?? '');
  const [period, setPeriod] = useState(30);
  const [docs, setDocs] = useState<Document[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [revision, setRevision] = useState(0);
  const [loading, setLoading] = useState(false);
  const [failed, setFailed] = useState(false);
  const [page, setPage] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [selected, setSelected] = useState<Document | null>(null);
  const [member, setMember] = useState<Member | null>(null);
  const [busy, setBusy] = useState(false);
  const guard = useUnsaved(busy);
  const heading = useRef<HTMLHeadingElement>(null);
  const [notice, setNotice] = useState('');
  useEffect(() => {
    if (!department) return;
    let active = true;
    setLoading(true);
    setFailed(false);
    setMetrics(null);
    setDocs([]);
    setMembers([]);
    const end = new Date(),
      start = new Date(end.getTime() - period * 86400000);
    Promise.all([
      api<DocumentPage>(
        `/documents?scope=manage&page=true&department_id=${department}&offset=${page * 30}`,
      ),
      api<Metrics>(`/metrics/${department}?start=${start.toISOString()}&end=${end.toISOString()}`),
      api<Member[]>(`/groups/${department}/members`),
    ])
      .then(([d, m, u]) => {
        if (active) {
          setDocs(d.items);
          setHasNext(d.has_next);
          setMetrics(m);
          setMembers(u);
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
  }, [api, department, period, page, revision, onError]);
  function move(action: () => void) {
    if (guard.navigate) guard.navigate(action);
    else action();
  }
  async function revoke() {
    setBusy(true);
    setMember(null);
    try {
      const m = member!.membership;
      await api('/groups/memberships', 'PUT', {
        user_id: m.user_id,
        department_id: m.department_id,
        leader: m.leader,
        can_author: m.can_author,
        can_review: m.can_review,
        active: !m.active,
      });
      setRevision((v) => v + 1);
    } catch (e) {
      onError(String(e));
    } finally {
      setBusy(false);
    }
  }
  const deptName = allowed.find((d) => d.id === department)?.name ?? '';
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="section-label">TEAM ADMINISTRATION</span>
          <h1 ref={heading} tabIndex={-1}>
            部署管理
          </h1>
          <p>管理部署の文書・所属・利用状況を確認します。</p>
        </div>
      </div>
      {notice && (
        <p role="status" className="success">
          {notice}
        </p>
      )}
      {!department ? (
        <div className="empty panel">
          <h2>管理権限のある部署がありません</h2>
          <p>部署リーダー向けの画面です。</p>
        </div>
      ) : (
        <>
          <div className="panel management-filters">
            <label>
              管理部署
              <select
                value={department}
                onChange={(e) => {
                  const value = e.target.value;
                  move(() => {
                    setDepartment(value);
                    setPage(0);
                    setSelected(null);
                  });
                }}
              >
                {allowed.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              集計期間
              <select value={period} onChange={(e) => setPeriod(Number(e.target.value))}>
                <option value={7}>過去7日間</option>
                <option value={30}>過去30日間</option>
                <option value={90}>過去90日間</option>
              </select>
            </label>
          </div>
          {loading && <p role="status">部署の情報を読み込み中…</p>}
          {failed && (
            <div className="alert">
              <p>部署の情報を読み込めませんでした。</p>
              <button onClick={() => setRevision((v) => v + 1)}>再試行</button>
            </div>
          )}
          {metrics && (
            <>
              <div className="stats-grid">
                {[
                  ['RAG質問受付数', metrics.questions],
                  ['文書閲覧数（利用部署）', metrics.views],
                  ['ユニーク閲覧者', metrics.unique_viewers],
                ].map(([label, value]) => (
                  <div className="stat panel" key={label}>
                    <span>{label}</span>
                    <strong>{value}</strong>
                    <small>
                      過去{period}日間 · {deptName}
                    </small>
                  </div>
                ))}
              </div>
              <p className="muted">
                集計時刻：{formatDate(metrics.generated_at)} · {metrics.timezone}（日本時間） · 回答{' '}
                {metrics.outcomes.answered} / 保留 {metrics.outcomes.held} / 失敗{' '}
                {metrics.outcomes.failed}
              </p>
            </>
          )}
          <section className="panel">
            <div className="section-heading">
              <h2>文書管理</h2>
              <span>このページ {docs.length}件</span>
            </div>
            <div className="table-scroll" role="region" aria-label="管理部署の文書" tabIndex={0}>
              <table>
                <thead>
                  <tr>
                    {['文書名', '公開版', '審査', 'RAG反映', '公開範囲', '更新日', '操作'].map(
                      (h) => (
                        <th key={h} scope="col">
                          {h}
                        </th>
                      ),
                    )}
                  </tr>
                </thead>
                <tbody>
                  {docs.map((doc) => (
                    <tr key={doc.id}>
                      <th scope="row">
                        {doc.title}
                        <small>{publicationLabel(doc)}</small>
                      </th>
                      <td>{doc.published_number ? `第${doc.published_number}版` : 'なし'}</td>
                      <td>
                        {doc.review_status
                          ? `第${doc.review_number}版・${statusLabel(doc.review_status)}`
                          : '未申請'}
                      </td>
                      <td>
                        {doc.latest_version_id
                          ? doc.index_ready
                            ? '反映済み'
                            : '未完了'
                          : '対象外'}
                      </td>
                      <td>{visibilityLabel[doc.visibility]}</td>
                      <td>{formatDate(doc.updated_at)}</td>
                      <td>
                        <button
                          className="secondary"
                          disabled={doc.status === 'deleted'}
                          onClick={() => move(() => setSelected(doc))}
                        >
                          管理<span className="sr-only">：{doc.title}</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {!loading && !failed && docs.length === 0 && <p>管理部署の文書はありません。</p>}
            <nav className="pagination" aria-label="管理文書のページ">
              <button disabled={page === 0 || loading} onClick={() => setPage(page - 1)}>
                前へ
              </button>
              <span>{page + 1} ページ</span>
              <button disabled={!hasNext || loading} onClick={() => setPage(page + 1)}>
                次へ
              </button>
            </nav>
          </section>
          {selected && (
            <PolicyEditor
              key={selected.id + selected.revision}
              api={api}
              doc={selected}
              departmentName={deptName}
              identity={identity}
              onError={onError}
              onCancel={() => setSelected(null)}
              onSaved={(message) => {
                setNotice(message);
                heading.current?.focus();
                setSelected(null);
                setRevision((v) => v + 1);
              }}
            />
          )}
          <section className="panel">
            <h2>メンバー管理 · {deptName}</h2>
            {members.map((m) => (
              <div className="manage-row" key={m.membership.id}>
                <strong>{m.display_name}</strong>
                <span>
                  {m.membership.can_author ? '執筆 ' : ''}
                  {m.membership.can_review ? '審査 ' : ''}
                  {m.membership.leader ? 'リーダー' : ''}
                </span>
                <button
                  disabled={busy || m.membership.user_id === identity.user.id}
                  onClick={() => setMember(m)}
                >
                  {m.membership.active ? '所属を停止' : '所属を再開'}
                </button>
              </div>
            ))}
          </section>
        </>
      )}
      <ConfirmDialog
        open={!!member}
        title="所属を変更しますか"
        confirmLabel="所属を変更する"
        onCancel={() => setMember(null)}
        onConfirm={() => void revoke()}
      >
        <p>
          {deptName} · {member?.display_name} の所属を{member?.membership.active ? '停止' : '再開'}
          します。
        </p>
      </ConfirmDialog>
    </>
  );
}
export function PolicyEditor({
  api,
  doc,
  departmentName,
  identity,
  onError,
  onSaved,
  onCancel,
}: {
  api: Api;
  doc: Document;
  departmentName: string;
  identity: Identity;
  onError: (message: string) => void;
  onSaved: (message: string) => void;
  onCancel: () => void;
}) {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    heading.current?.focus();
    heading.current?.scrollIntoView({ block: 'start' });
  }, []);
  const [visibility, setVisibility] = useState(doc.visibility);
  const [shared, setShared] = useState<string[]>(JSON.parse(doc.shared_departments));
  const [status, setStatus] = useState(doc.status);
  const [reason, setReason] = useState('');
  const [confirm, setConfirm] = useState('');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const changed =
    visibility !== doc.visibility ||
    status !== doc.status ||
    JSON.stringify([...shared].sort()) !==
      JSON.stringify((JSON.parse(doc.shared_departments) as string[]).sort());
  useUnsaved(changed || !!reason || busy);
  async function save() {
    const deleting = confirm === 'delete';
    setConfirm('');
    setBusy(true);
    try {
      await api(`/documents/${doc.id}/policy`, 'PUT', {
        revision: doc.revision,
        visibility,
        shared_departments: visibility === 'selected' ? shared : [],
        status: deleting ? 'deleted' : status,
        reason: deleting ? reason : '',
      });
      onSaved(deleting ? '文書を削除しました。' : '公開設定を保存しました。');
    } catch (e) {
      setNotice(
        '保存できませんでした。入力を保持しています。競合の場合は現在の設定を確認してください。',
      );
      onError(String(e));
    } finally {
      setBusy(false);
    }
  }
  const names = (ids: string[]) =>
    ids
      .map(
        (id) =>
          (identity.directory ?? identity.departments).find((d) => d.id === id)?.name ?? '部署',
      )
      .join('、');
  return (
    <section className="panel policy-editor">
      <h2 ref={heading} tabIndex={-1}>
        {doc.title} の公開設定
      </h2>
      <p className="notice">管理部署：{departmentName}</p>
      {notice && <p role="alert">{notice}</p>}
      <label>
        公開範囲
        <select value={visibility} onChange={(e) => setVisibility(e.target.value)}>
          <option value="department">所有部署</option>
          <option value="selected">指定部署</option>
          <option value="organization">全組織</option>
        </select>
      </label>
      {visibility === 'selected' && (
        <fieldset>
          <legend>共有先部署</legend>
          {(identity.directory ?? identity.departments).map((d) => (
            <label className="checkbox-label" key={d.id}>
              <input
                type="checkbox"
                checked={shared.includes(d.id)}
                onChange={(e) =>
                  setShared(
                    e.target.checked ? [...shared, d.id] : shared.filter((id) => id !== d.id),
                  )
                }
              />
              {d.name}
            </label>
          ))}
        </fieldset>
      )}
      <label>
        公開状態
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="active">公開する（承認版がある場合）</option>
          <option value="withdrawn">公開停止</option>
        </select>
      </label>
      <p>
        変更前：{visibilityLabel[doc.visibility]} {names(JSON.parse(doc.shared_departments))} ·{' '}
        {publicationLabel(doc)}
      </p>
      <p>
        変更後：{visibilityLabel[visibility]} {visibility === 'selected' ? names(shared) : ''} ·{' '}
        {publicationLabel({ ...doc, status })}
      </p>
      <div className="actions">
        <button
          className="primary"
          disabled={!changed || busy || (visibility === 'selected' && shared.length === 0)}
          onClick={() => setConfirm('policy')}
        >
          変更内容を確認
        </button>
        <button className="secondary" disabled={busy} onClick={onCancel}>
          変更をキャンセル
        </button>
      </div>
      <div className="delete-section">
        <h3>文書を削除</h3>
        <p>公開停止とは異なり、文書を削除対象にします。この画面から元に戻すことはできません。</p>
        <label>
          削除理由（必須）
          <textarea
            value={reason}
            maxLength={2000}
            onChange={(e) => setReason(e.target.value)}
            aria-describedby="delete-reason-help"
          />
        </label>
        <p id="delete-reason-help">理由は監査記録に保存します。</p>
        <button
          className="danger"
          disabled={!reason.trim() || busy || changed}
          onClick={() => setConfirm('delete')}
        >
          削除内容を確認
        </button>
        {changed && <p>公開設定の変更を先に保存するか、キャンセルしてください。</p>}
      </div>
      <ConfirmDialog
        open={!!confirm}
        title={confirm === 'delete' ? '文書を削除しますか' : '公開設定を保存しますか'}
        confirmLabel={confirm === 'delete' ? '削除する' : '保存する'}
        onCancel={() => setConfirm('')}
        onConfirm={() => void save()}
      >
        <p>
          {departmentName} · {doc.title}
        </p>
        {confirm === 'delete' ? (
          <p>配信と検索を停止し、保持期間後に削除します。</p>
        ) : (
          <>
            <p>
              変更前：{visibilityLabel[doc.visibility]} {names(JSON.parse(doc.shared_departments))}{' '}
              · {publicationLabel(doc)}
            </p>
            <p>
              変更後：{visibilityLabel[visibility]} {visibility === 'selected' ? names(shared) : ''}{' '}
              · {publicationLabel({ ...doc, status })}
            </p>
          </>
        )}
      </ConfirmDialog>
    </section>
  );
}
