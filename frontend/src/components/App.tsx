import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  BookOpen,
  Layers,
  LogOut,
  Menu,
  MessageSquare,
  PenLine,
  Settings2,
  ShieldCheck,
  Users,
} from 'lucide-react';
import { createApi, type Citation, type Identity } from '../lib/api';
import { Login } from './layout/Login';
import { Workspace } from './layout/Workspace';
import { ConfirmDialog } from './ui/ConfirmDialog';
import { Library } from '../features/documents/Library';
import { DocumentPanel } from '../features/documents/DocumentPanel';
import { Reviews } from '../features/reviews/Reviews';
import { Chat } from '../features/chat/Chat';
import { Groups } from '../features/groups/Groups';
import { Operations } from '../features/operations/Operations';
export { Login, Library, DocumentPanel, Reviews, Chat, Groups, Operations };
export { PlacedDocument } from '../features/documents/PlacedDocument';
export { ProtectedImage } from '../features/images/ProtectedImage';
export { Images } from '../features/images/Images';

type Screen = 'library' | 'work' | 'reviews' | 'chat' | 'groups' | 'operations';
const navigation = [
  { id: 'library', label: 'ドキュメント', icon: BookOpen },
  { id: 'chat', label: 'RAGチャット', icon: MessageSquare },
  { id: 'work', label: '執筆', icon: PenLine },
  { id: 'reviews', label: '審査', icon: ShieldCheck },
  { id: 'groups', label: '部署管理', icon: Users },
  { id: 'operations', label: '反映・削除ジョブ', icon: Settings2 },
] as const;
export default function App() {
  const [token, setToken] = useState(sessionStorage.getItem('kotorelay-token') ?? '');
  const [identity, setIdentity] = useState<Identity | null>(null);
  const [screen, setScreen] = useState<Screen>('library');
  const [error, setError] = useState('');
  const [selected, setSelected] = useState<{ id: string; citation?: Citation } | null>(null);
  const [department, setDepartment] = useState('');
  const [menu, setMenu] = useState(false);
  const [pending, setPending] = useState<(() => void) | null>(null);
  const dirtyKeys = useRef(new Set<string>());
  const api = useMemo(() => createApi(token), [token]);
  const dirty = useCallback((key: string, value: boolean) => {
    if (value) dirtyKeys.current.add(key);
    else dirtyKeys.current.delete(key);
  }, []);
  const navigate = useCallback((action: () => void) => {
    if (dirtyKeys.current.size) setPending(() => action);
    else action();
  }, []);
  const workspace = useMemo(() => ({ dirty, navigate }), [dirty, navigate]);
  useEffect(() => {
    if (!token) return;
    let active = true;
    api<Identity>('/groups/me')
      .then((value) => {
        if (active) {
          setIdentity(value);
          setDepartment(value.departments[0]?.id ?? '');
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
  useEffect(() => {
    const heading = document.querySelector<HTMLElement>('main h1');
    if (heading) {
      document.title = `${heading.textContent} | KotoRelay`;
      heading.tabIndex = -1;
      heading.focus();
    }
  }, [screen, selected, identity]);
  function move(next: Screen) {
    navigate(() => {
      setScreen(next);
      setSelected(null);
      setError('');
      setMenu(false);
    });
  }
  function logout() {
    navigate(() => {
      sessionStorage.removeItem('kotorelay-token');
      setToken('');
      setIdentity(null);
      setSelected(null);
      setScreen('library');
    });
  }
  function open(id: string, citation?: Citation) {
    navigate(() => {
      setSelected({ id, citation });
      setError('');
    });
  }
  if (!token || !identity)
    return (
      <Login
        error={error}
        loading={!!token && !error}
        onLogin={(value) => {
          sessionStorage.setItem('kotorelay-token', value);
          setIdentity(null);
          setToken(value);
          setSelected(null);
        }}
      />
    );
  const has = (role: 'can_author' | 'can_review' | 'leader') =>
    identity.memberships.some((m) => m.active && m[role]);
  const visible = navigation.filter((n) =>
    n.id === 'work'
      ? has('can_author')
      : n.id === 'reviews'
        ? has('can_review')
        : n.id === 'groups'
          ? has('leader')
          : n.id === 'operations'
            ? identity.user.operator
            : true,
  );
  return (
    <Workspace.Provider value={workspace}>
      <a className="skip-link" href="#main-content">
        本文へ移動
      </a>
      <div className="app-shell">
        <header className="app-header">
          <a
            href="#"
            className="brand"
            onClick={(e) => {
              e.preventDefault();
              move('library');
            }}
          >
            <span className="brand-icon">
              <Layers size={26} />
            </span>
            <span>
              KotoRelay<small>承認された知識を、次の人へ。</small>
            </span>
          </a>
          <button
            className="menu-toggle secondary"
            aria-expanded={menu}
            aria-controls="main-navigation"
            onClick={() => setMenu(!menu)}
          >
            <Menu size={20} />
            メニュー
          </button>
          <label className="usage-department">
            利用部署
            <select
              value={department}
              onChange={(e) => {
                const value = e.target.value;
                navigate(() => setDepartment(value));
              }}
            >
              {identity.departments.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </label>
          <div className="account">
            <span>{identity.user.display_name}</span>
            <button className="text-button" onClick={logout}>
              <LogOut size={18} />
              ログアウト
            </button>
          </div>
        </header>
        <aside className={`sidebar ${menu ? 'is-open' : ''}`} id="main-navigation">
          <nav aria-label="メインナビゲーション">
            {visible.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                className={`nav-item ${screen === id ? 'active' : ''}`}
                aria-current={screen === id ? 'page' : undefined}
                onClick={() => move(id)}
              >
                <Icon size={20} />
                {label}
              </button>
            ))}
          </nav>
          <p className="sidebar-note">
            書く、確認する、共有する。
            <br />
            承認済みの知識をチームとAIへ。
          </p>
        </aside>
        <main className="main" id="main-content" tabIndex={-1}>
          <div className="content">
            {error && (
              <div role="alert" className="alert">
                <span>{error}</span>
                <button onClick={() => setError('')}>閉じる</button>
              </div>
            )}
            {selected ? (
              <DocumentPanel
                key={selected.id}
                id={selected.id}
                citation={selected.citation}
                api={api}
                token={token}
                identity={identity}
                department={department}
                edit={screen === 'work'}
                onBack={() => navigate(() => setSelected(null))}
                onError={setError}
              />
            ) : screen === 'library' || screen === 'work' ? (
              <Library
                api={api}
                identity={identity}
                edit={screen === 'work'}
                onOpen={open}
                onError={setError}
              />
            ) : screen === 'reviews' ? (
              <Reviews api={api} token={token} onError={setError} />
            ) : screen === 'chat' ? null : screen === 'groups' ? (
              <Groups api={api} identity={identity} onError={setError} />
            ) : (
              <Operations api={api} onError={setError} />
            )}
            {screen === 'chat' && (
              <div hidden={!!selected}>
                <Chat
                  key={department}
                  department={department}
                  api={api}
                  identity={identity}
                  onOpen={open}
                  onError={setError}
                />
              </div>
            )}
          </div>
          <footer>
            KotoRelay · 承認された知識を、次の一歩へ。
            <span>{identity.mode === 'local' ? 'ローカル環境' : 'AWS環境'}</span>
          </footer>
        </main>
      </div>
      <ConfirmDialog
        open={!!pending}
        title="未保存の変更があります"
        confirmLabel="変更を破棄して移動"
        onCancel={() => setPending(null)}
        onConfirm={() => {
          const action = pending;
          dirtyKeys.current.clear();
          setPending(null);
          action?.();
        }}
      >
        <p>入力した変更は保存されていません。キャンセルすると編集を続けられます。</p>
      </ConfirmDialog>
    </Workspace.Provider>
  );
}
