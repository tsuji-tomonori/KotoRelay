import { useEffect, useRef, useState } from 'react';
import { ChevronLeft, GitBranch, Send } from 'lucide-react';
import {
  formatDate,
  statusLabel,
  visibilityLabel,
  type Api,
  type Identity,
  type Draft,
  type ReadDocument,
  type Version,
  type Submission,
  type Placement,
  type Citation,
} from '../../lib/api';
import { useUnsaved } from '../../components/layout/Workspace';
import { PlacedDocument, relocatePlacements } from './PlacedDocument';
import { Images } from '../images/Images';
export function DocumentPanel({
  id,
  api,
  token,
  identity,
  edit,
  onBack,
  onError,
  department,
  citation,
}: {
  id: string;
  api: Api;
  token: string;
  identity: Identity;
  edit: boolean;
  department?: string;
  citation?: Citation;
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
  const [ocrPending, setOcrPending] = useState(false);
  const [failed, setFailed] = useState(false);
  const [reload, setReload] = useState(0);
  const [showLatest, setShowLatest] = useState(false);
  const [cursor, setCursor] = useState(0);
  const [view, setView] = useState('both');
  const titleHeading = useRef<HTMLHeadingElement>(null);
  useUnsaved(dirty || busy);
  const usageDepartment = department ?? identity.departments[0]?.id ?? '';
  const citationUpdated =
    !!citation && !!read && citation.version_id !== read.version.id && !showLatest;

  useEffect(() => {
    let active = true;
    setFailed(false);
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
        }
      })
      .catch((e) => {
        if (active) {
          setFailed(true);
          onError(String(e));
        }
      });
    return () => {
      active = false;
    };
  }, [api, id, edit, onError, reload]);
  useEffect(() => {
    if (read && !citationUpdated && usageDepartment)
      void api(`/metrics/views/${id}`, 'POST', {
        id: crypto.randomUUID(),
        department_id: usageDepartment,
      }).catch((e) => onError(String(e)));
  }, [read, citationUpdated, usageDepartment, api, id, onError]);
  useEffect(() => {
    if (title) {
      document.title = `${title} | KotoRelay`;
      titleHeading.current?.focus();
    }
  }, [title]);
  useEffect(() => {
    if (citation && read && !citationUpdated) {
      const node = Array.from(
        document.querySelectorAll<HTMLElement>('.article .markdown [id]'),
      ).find((h) => h.textContent === citation.heading);
      node?.scrollIntoView();
      node?.focus();
    }
  }, [citation, read, citationUpdated]);
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
      setMessage(
        `第${version.number}版を承認申請しました。${draft.document.latest_version_id ? '一般閲覧では現在の承認版が引き続き公開されます。' : '承認後に閲覧へ公開されます。'}`,
      );
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
      <button className="back" onClick={onBack}>
        <ChevronLeft size={16} />
        文書一覧へ
      </button>
      <div className="page-heading">
        <div>
          <span className="section-label">{edit ? 'DOCUMENT EDITOR' : 'APPROVED DOCUMENT'}</span>
          <h1 ref={titleHeading} tabIndex={-1}>
            {citationUpdated ? '引用元が更新されています' : title || '読み込み中…'}
          </h1>
          <p>
            {edit
              ? 'Markdownで執筆し、保存してから承認を申請します。'
              : read
                ? `第${read.version.number}版 · ${read.index_ready ? 'RAGへ反映済み' : 'RAGへの反映は未完了です'}`
                : ''}
          </p>
        </div>
        {edit && (
          <div className="actions">
            <button className="secondary" onClick={() => void loadHistory()}>
              <GitBranch size={16} />
              版履歴
            </button>
            <button
              className="secondary"
              disabled={busy || !draft || ocrPending}
              onClick={() => void save()}
            >
              保存
            </button>
            <button
              className="primary"
              disabled={
                busy || dirty || !draft || ocrPending || placements.some((p) => !p.alt_text?.trim())
              }
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
            {busy ? '保存・申請しています…' : dirty ? '未保存の変更があります' : '下書き保存済み'}
          </span>
          {message && <span>{message}</span>}
        </div>
      )}
      {failed && (
        <div className="alert">
          <p>文書を読み込めませんでした。権限が変更された可能性があります。</p>
          <button onClick={() => setReload(reload + 1)}>再試行</button>
        </div>
      )}
      {citationUpdated && (
        <div className="panel">
          <p>
            回答で参照した版とは異なる版が公開されています。当時の引用として新版を表示することはできません。
          </p>
          <button className="primary" onClick={() => setShowLatest(true)}>
            最新の承認版を開く
          </button>
          <button onClick={onBack}>回答へ戻る</button>
        </div>
      )}
      {read && !citationUpdated && (
        <p className="document-meta">
          所有部署：
          {
            (identity.directory ?? identity.departments).find(
              (d) => d.id === read.document.department_id,
            )?.name
          }{' '}
          · {visibilityLabel[read.document.visibility]} · {formatDate(read.version.created_at)}
        </p>
      )}
      {edit && (
        <div className="editor-help">
          {dirty && <p>承認申請の前に下書きを保存してください。</p>}
          {ocrPending && <p>画像のOCRを確認してください。未確定の訂正は文書保存へ含まれません。</p>}
          {placements.some((p) => !p.alt_text?.trim()) && (
            <p>各画像の代替テキストを入力してください。</p>
          )}
          <div className="tabs" aria-label="編集画面の表示">
            {[
              ['both', '編集とプレビュー'],
              ['edit', '編集'],
              ['preview', 'プレビュー'],
            ].map(([key, label]) => (
              <button key={key} aria-pressed={view === key} onClick={() => setView(key!)}>
                {label}
              </button>
            ))}
          </div>
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
          <div className={`editor-columns mode-${view}`}>
            <div>
              <div className="editor-label">MARKDOWN</div>
              <textarea
                onSelect={(e) =>
                  setCursor(Array.from(body.slice(0, e.currentTarget.selectionStart)).length)
                }
                aria-label="Markdown本文"
                disabled={!draft || busy}
                value={body}
                onChange={(e) => {
                  setPlacements(relocatePlacements(body, e.target.value, placements));
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
      ) : !citationUpdated && !failed ? (
        <section className="panel article">
          <PlacedDocument
            body={body}
            placements={placements}
            token={token}
            version={read?.version.id}
            toc
          />
        </section>
      ) : null}
      {!citationUpdated && !failed && (
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
          offset={cursor}
          onPending={setOcrPending}
          onError={onError}
        />
      )}
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
          <p>差分の「+」は追加、「-」は削除です。</p>
          {diff && <pre className="diff">{diff}</pre>}
          <button
            onClick={() => {
              const blob = new Blob([body], { type: 'text/markdown' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = 'draft.md';
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            編集中の本文を退避
          </button>
        </section>
      )}
    </>
  );
}
