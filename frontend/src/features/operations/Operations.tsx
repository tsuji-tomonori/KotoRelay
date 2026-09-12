import { useEffect, useState } from 'react';
import { formatDate, jobLabel, type Api, type Job } from '../../lib/api';
export function Operations({ api, onError }: { api: Api; onError: (message: string) => void }) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [revision, setRevision] = useState(0);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [differences, setDifferences] = useState<{ document_id: string; reason: string }[]>([]);
  useEffect(() => {
    let active = true;
    setLoading(true);
    setFailed(false);
    api<Job[]>('/operations/jobs?details=true')
      .then((value) => {
        if (active) setJobs(value);
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
  }, [api, onError, revision]);
  async function process(job: Job) {
    setBusy(true);
    try {
      await api(`/operations/jobs/${job.id}`, 'POST');
      setRevision(revision + 1);
    } catch (e) {
      onError(String(e));
    } finally {
      setBusy(false);
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
          <h1>反映・削除ジョブ</h1>
          <p>承認と同時に記録された処理を確認し、必要に応じて再実行します。</p>
        </div>
        <button className="secondary" onClick={() => void reconcile()}>
          正本と索引を照合
        </button>
      </div>
      <section className="panel">
        {loading ? (
          <p role="status">ジョブを読み込み中…</p>
        ) : failed ? (
          <div className="alert">
            <p>ジョブを読み込めませんでした。</p>
            <button onClick={() => setRevision((v) => v + 1)}>再試行</button>
          </div>
        ) : jobs.length === 0 ? (
          <p className="muted">ジョブはありません。</p>
        ) : (
          jobs.map((job) => (
            <div className="manage-row" key={job.id}>
              <div>
                <strong>{job.kind === 'purge' ? '削除処理' : '検索への反映'}</strong>
                <p>
                  {job.title} {job.version_number && `· 第${job.version_number}版`}
                </p>
                <small>{job.created_at && `登録：${formatDate(job.created_at)}`}</small>
                <details>
                  <summary>処理の識別情報</summary>
                  <p>{job.document_id}</p>
                  <p>{job.error_code}</p>
                </details>
              </div>
              <span className="badge">{jobLabel(job.kind, job.status)}</span>
              <span>{job.attempts} 回</span>
              {job.status === 'retained' && <span>保持期間後に自動で削除します。</span>}
              <button
                className="secondary"
                disabled={busy || ['done', 'obsolete'].includes(job.status) || job.attempts >= 5}
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
