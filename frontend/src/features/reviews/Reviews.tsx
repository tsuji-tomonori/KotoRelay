import { useEffect, useState } from 'react';
import { ArrowRight, CheckCircle2, FileText, ShieldCheck } from 'lucide-react';
import {
  formatDate,
  statusLabel,
  type Api,
  type Review,
  type ReadDocument,
  type Placement,
} from '../../lib/api';
import { Images } from '../images/Images';
import { PlacedDocument } from '../documents/PlacedDocument';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';
import { useUnsaved } from '../../components/layout/Workspace';
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
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [retry, setRetry] = useState(0);
  const [confirmation, setConfirmation] = useState('');
  const [diff, setDiff] = useState('');
  const guard = useUnsaved(!!reason || busy);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setFailed(false);
    api<Review[]>('/reviews')
      .then((value) => {
        if (active) setItems(value);
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
  }, [api, onError, message, retry]);
  async function open(item: Review) {
    try {
      const value = await api<ReadDocument>(
        `/documents/${item.submission.document_id}?version_id=${item.submission.version_id}`,
      );
      setRead(value);
      setDiff('');
      if (
        value.document.latest_version_id &&
        value.document.latest_version_id !== value.version.id
      ) {
        const compared = await api<{ diff: string }>(
          `/documents/${value.document.id}/diff?left=${value.document.latest_version_id}&right=${value.version.id}`,
        );
        setDiff(compared.diff);
      }
      setSelected(item);
      setReason('');
    } catch (e) {
      onError(String(e));
    }
  }
  async function decide(decision: string) {
    if (!selected) return;
    setBusy(true);
    setConfirmation('');
    try {
      await api(
        `/reviews/${selected.submission.id}/decision`,
        'POST',
        { manifest_hash: selected.submission.manifest_hash, decision, reason },
        crypto.randomUUID(),
      );
      setMessage(
        `第${read!.version.number}版を${decision === 'approved' ? '承認' : '却下'}しました。${decision === 'approved' ? '公開状況とRAG反映状況は文書一覧で確認できます。' : ''}`,
      );
      setReason('');
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
          <h1>審査</h1>
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
          <button
            className="back"
            onClick={() => {
              const back = () => {
                setSelected(null);
                setReason('');
              };
              if (guard.navigate) guard.navigate(back);
              else back();
            }}
          >
            一覧へ戻る
          </button>
          <h2>
            {read.version.title} · v{read.version.number}
          </h2>
          <p className="notice">
            審査対象：第{read.version.number}版 · 公開中：
            {read.document.latest_version_id ? '承認版あり' : '公開版なし'}
          </p>
          <details>
            <summary>審査対象の識別情報</summary>
            <p className="hash">manifest: {selected.submission.manifest_hash}</p>
          </details>
          <details open>
            <summary>変更点（+ 追加 / - 削除）</summary>
            <pre className="diff">{diff || '初回申請、または比較対象の公開版がありません。'}</pre>
          </details>
          <PlacedDocument
            body={read.body}
            placements={(
              JSON.parse(read.version.manifest) as { images: { placement: Placement }[] }
            ).images.map((i) => i.placement)}
            token={token}
            version={read.version.id}
            toc
          />
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
              aria-describedby="review-reason-help"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              maxLength={2000}
            />
          </label>
          <p id="review-reason-help">却下する場合は、修正に必要な理由を入力してください。</p>
          <div className="actions">
            <button className="primary" disabled={busy} onClick={() => setConfirmation('approved')}>
              この版を承認
            </button>
            <button
              className="danger"
              disabled={busy || !reason.trim()}
              onClick={() => setConfirmation('rejected')}
            >
              理由を残して却下
            </button>
          </div>
        </section>
      ) : (
        <section className="panel">
          {loading ? (
            <p role="status">審査対象を読み込み中…</p>
          ) : failed ? (
            <div className="alert">
              <p>審査対象を読み込めませんでした。</p>
              <button onClick={() => setRetry(retry + 1)}>再試行</button>
            </div>
          ) : items.length === 0 ? (
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
                  <strong>
                    {item.title} · 第{item.version_number}版
                  </strong>
                  <p>
                    {item.department_name} · 申請者：{item.requested_by}
                  </p>
                  <small>
                    {formatDate(item.submission.created_at)}
                    {item.submission.reason && ` · ${item.submission.reason}`}
                  </small>
                </div>
                <span className="badge">{statusLabel(item.submission.status)}</span>
                {item.self_requested && <span>自己申請のため審査できません</span>}
                {item.can_review &&
                  !item.self_requested &&
                  item.submission.status === 'pending' && (
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
      <ConfirmDialog
        open={!!confirmation}
        title={`第${read?.version.number ?? ''}版を${confirmation === 'approved' ? '承認' : '却下'}しますか`}
        confirmLabel={confirmation === 'approved' ? '承認する' : '却下する'}
        onCancel={() => setConfirmation('')}
        onConfirm={() => void decide(confirmation)}
      >
        <p>{selected?.title} の確認した版に対して判定を確定します。</p>
      </ConfirmDialog>
    </>
  );
}
