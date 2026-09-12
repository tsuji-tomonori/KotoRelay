import { useState } from 'react';
import { FileText, ArrowRight, RefreshCw, Send, Sparkles } from 'lucide-react';
import {
  formatDate,
  statusLabel,
  type Api,
  type Identity,
  type Answer,
  type Citation,
} from '../../lib/api';
import Markdown from '../../components/Markdown';
import { useUnsaved } from '../../components/layout/Workspace';
export function Chat({
  api,
  identity,
  onOpen,
  onError,
  department: usageDepartment,
}: {
  api: Api;
  identity: Identity;
  onOpen: (id: string, citation?: Citation) => void;
  department?: string;
  onError: (message: string) => void;
}) {
  const [question, setQuestion] = useState('');
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [conversation, setConversation] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [department, setDepartment] = useState(
    usageDepartment ?? identity.departments[0]?.id ?? '',
  );
  const [notice, setNotice] = useState('');
  useUnsaved(!!question || busy);
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
      setNotice(
        answer.status === 'answered'
          ? '回答を受け取りました。'
          : '確認できる文書からは回答できませんでした。質問を具体化してください。',
      );
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
        setAnswers([]);
        onError(String(e));
      }
  }
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="section-label">ASK YOUR KNOWLEDGE</span>
          <h1>RAGチャット</h1>
          <p>あなたが閲覧できる最新承認版から、根拠をたどれる回答を。</p>
        </div>
        <button className="secondary" disabled={!conversation} onClick={() => void refresh()}>
          <RefreshCw size={16} />
          履歴を再確認
        </button>
      </div>
      <p className="notice">利用部署を変更すると、新しい会話を開始します。</p>
      <p role="status">{busy ? '回答しています…' : notice}</p>
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
          <div className="messages">
            {answers.map((answer) => (
              <article key={answer.id}>
                <div className="question-bubble">{answer.question}</div>
                <div className="answer-bubble">
                  <span className="answer-title">
                    <Sparkles size={17} /> KotoRelay{' '}
                    <span className="badge">{statusLabel(answer.status)}</span>
                  </span>
                  <Markdown body={answer.answer} prefix={`answer-${answer.id}`} />
                  {answer.citations.length > 0 && (
                    <div className="citations">
                      <small>参照した承認版</small>
                      {answer.citations.map((c) => (
                        <button key={c.chunk_id} onClick={() => onOpen(c.document_id, c)}>
                          <FileText size={14} />
                          {c.title} · {c.version_number ? `第${c.version_number}版` : '引用版'} ·{' '}
                          {c.heading}
                          {c.has_images && ' · 画像を参照'}
                          <ArrowRight size={13} />
                        </button>
                      ))}
                    </div>
                  )}
                  <small className="muted">{formatDate(answer.created_at)}</small>
                  <details>
                    <summary>回答の詳細</summary>
                    {answer.model}
                  </details>
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
          {usageDepartment === undefined && (
            <label className="department-selector">
              利用部署
              <select
                value={department}
                disabled={busy}
                onChange={(e) => {
                  setDepartment(e.target.value);
                  setConversation(null);
                  setAnswers([]);
                  setNotice('利用部署を変更し、新しい会話を開始しました。');
                }}
              >
                {identity.departments.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </label>
          )}
          <div className="composer-input">
            <label className="question-field">
              質問（2000文字まで）
              <textarea
                disabled={busy}
                aria-label="質問"
                placeholder="例: 開発フローについて教えてください"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                maxLength={2000}
              />
            </label>
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
