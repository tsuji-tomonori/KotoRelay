import { useState } from 'react';
import { Layers, ArrowRight, ShieldCheck } from 'lucide-react';
import { personaNames } from '../../lib/api';
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
