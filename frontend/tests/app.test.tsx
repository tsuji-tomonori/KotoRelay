import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App, {
  Login,
  Library,
  DocumentPanel,
  ProtectedImage,
  PlacedDocument,
  Images,
  Reviews,
  Chat,
  Groups,
  Operations,
} from '../src/components/App';
import type { Api, Document, Identity, Placement } from '../src/lib/api';
const identity: Identity = {
  user: { id: 'u1', display_name: '架空の執筆者', operator: true },
  departments: [{ id: 'd1', name: '開発部' }],
  memberships: [
    {
      id: 'm1',
      user_id: 'u1',
      department_id: 'd1',
      leader: true,
      can_author: true,
      can_review: true,
      active: true,
    },
  ],
  mode: 'local',
};
const doc: Document = {
  id: 'doc1',
  title: '開発ガイド',
  department_id: 'd1',
  latest_version_id: 'v1',
  revision: 2,
  next_version: 2,
  status: 'active',
  visibility: 'department',
  shared_departments: '[]',
  updated_at: '2026-09-12T00:00:00Z',
};
const version = {
  id: 'v1',
  document_id: 'doc1',
  number: 1,
  title: doc.title,
  manifest_hash: 'a'.repeat(64),
  created_by: 'u2',
  created_at: doc.updated_at,
  manifest: '{"images":[]}',
};
const submission = {
  id: 's1',
  document_id: 'doc1',
  version_id: 'v1',
  status: 'pending',
  manifest_hash: version.manifest_hash,
  reason: '',
  created_at: doc.updated_at,
  decided_at: null,
};
const placement: Placement = {
  id: 'p1',
  asset_id: 'a1',
  ocr_run_id: 'o1',
  offset: 0,
  heading: '画像',
};
const region = { text: '画像の文字', x: 0, y: 0, width: 1, height: 1, confidence: 1, order: 0 };
const answer = {
  id: 'a1',
  conversation_id: 'c1',
  question: '開発フロー',
  answer: '承認します',
  status: 'answered',
  citations: [
    { document_id: 'doc1', version_id: 'v1', chunk_id: 'k1', title: doc.title, heading: '手順' },
  ],
  model: 'local-extractive-v1',
  created_at: doc.updated_at,
};
function mockApi(handler: (path: string, method?: string, data?: unknown) => unknown = () => []) {
  const calls = vi.fn(handler);
  const api: Api = async <T,>(path: string, method?: string, data?: unknown) =>
    (await calls(path, method, data)) as T;
  return { api, calls };
}
function fill(label: string, value: string) {
  fireEvent.change(screen.getByLabelText(label), { target: { value } });
}
const error = () => vi.fn();

describe('ログインと画面切替', () => {
  it('ローカルの役割とAWSトークンを選べる', () => {
    const login = vi.fn();
    render(<Login onLogin={login} error="" loading={false} />);
    fireEvent.change(screen.getByLabelText('サンプルの役割'), { target: { value: 'reader' } });
    fireEvent.click(screen.getByRole('button', { name: 'ローカルで始める' }));
    expect(login).toHaveBeenCalledWith('demo-reader');
    fill('アクセストークン', 'access');
    fireEvent.click(screen.getByRole('button', { name: '接続' }));
    expect(login).toHaveBeenCalledWith('access');
  });
  it('認証エラーと接続中の状態を表示する', () => {
    render(<Login onLogin={vi.fn()} error="認証エラー" loading={true} />);
    expect(screen.getByRole('alert')).toHaveTextContent('認証エラー');
    expect(screen.getByRole('button', { name: '接続中…' })).toBeDisabled();
  });
  it('本人を取得して各画面を切り替えログアウトする', async () => {
    sessionStorage.setItem('kotorelay-token', 'demo-author');
    vi.spyOn(globalThis, 'fetch').mockImplementation(
      async (input) =>
        new Response(
          JSON.stringify(
            String(input).endsWith('/groups/me') ? { ...identity, memberships: [] } : [],
          ),
        ),
    );
    render(<App />);
    await screen.findByRole('navigation');
    for (const label of [
      '執筆ワークスペース',
      '承認・レビュー',
      'ナレッジチャット',
      '部署管理',
      '反映ジョブ',
      'ドキュメント',
    ]) {
      fireEvent.click(screen.getByRole('button', { name: label }));
      await act(async () => {});
    }
    fireEvent.click(screen.getByRole('link', { name: /KotoRelay/ }));
    fireEvent.click(screen.getByRole('button', { name: 'ログアウト' }));
    expect(screen.getByRole('button', { name: 'ローカルで始める' })).toBeVisible();
    expect(sessionStorage.getItem('kotorelay-token')).toBeNull();
  });
  it('未ログインから本人取得失敗を表示する', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('通信失敗'));
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'ローカルで始める' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('通信失敗');
  });
  it('運用者でなければジョブ画面を表示しない', async () => {
    sessionStorage.setItem('kotorelay-token', 'demo-reader');
    vi.spyOn(globalThis, 'fetch').mockImplementation(
      async (input) =>
        new Response(
          JSON.stringify(
            String(input).endsWith('/groups/me')
              ? { ...identity, user: { ...identity.user, operator: false }, mode: 'aws' }
              : [],
          ),
        ),
    );
    render(<App />);
    await screen.findByRole('navigation');
    expect(screen.queryByRole('button', { name: '反映ジョブ' })).toBeNull();
    expect(screen.getByText('AWS WORKSPACE')).toBeVisible();
  });
});

describe('文書一覧', () => {
  it('検索・ページ送り・文書を開く操作を行う', async () => {
    const { api, calls } = mockApi((path) =>
      path.includes('offset=30')
        ? []
        : Array.from({ length: 30 }, (_, i) => ({
            ...doc,
            id: `doc${i}`,
            latest_version_id: i % 2 ? 'v1' : null,
            department_id: i % 2 ? 'd1' : 'shared',
          })),
    );
    const open = vi.fn();
    render(<Library api={api} identity={identity} edit={false} onOpen={open} onError={error()} />);
    await screen.findAllByText('開発ガイド');
    fireEvent.click(screen.getAllByRole('button').find((b) => b.className === 'document-card')!);
    expect(open).toHaveBeenCalledWith('doc0');
    fireEvent.click(screen.getByRole('button', { name: '次へ' }));
    await screen.findByText('知識の最初の一枚を。');
    fireEvent.click(screen.getByRole('button', { name: '前へ' }));
    fill('文書を検索', 'ゼロ');
    await waitFor(() =>
      expect(calls).toHaveBeenCalledWith(
        expect.stringContaining('search=%E3%82%BC%E3%83%AD'),
        undefined,
        undefined,
      ),
    );
  });
  it('新規作成して執筆画面へ進む', async () => {
    const { api, calls } = mockApi((_, method) => (method === 'POST' ? doc : []));
    const open = vi.fn();
    render(<Library api={api} identity={identity} edit onOpen={open} onError={error()} />);
    await screen.findByText('知識の最初の一枚を。');
    fireEvent.click(screen.getByRole('button', { name: '新しい文書' }));
    fill('文書タイトル', '新しい手順');
    fireEvent.change(screen.getByLabelText('所有部署'), { target: { value: 'd1' } });
    fireEvent.click(screen.getByRole('button', { name: /作成して執筆/ }));
    await waitFor(() => expect(open).toHaveBeenCalledWith('doc1'));
    expect(calls).toHaveBeenCalledWith('/documents', 'POST', {
      title: '新しい手順',
      department_id: 'd1',
    });
  });
  it('検索の空結果と作成失敗を表示する', async () => {
    const onError = error();
    const { api } = mockApi((_, method) => {
      if (method === 'POST') throw new Error('作成失敗');
      return [];
    });
    render(<Library api={api} identity={identity} edit onOpen={vi.fn()} onError={onError} />);
    fill('文書を検索', 'なし');
    await screen.findByText('一致する文書がありません');
    fireEvent.click(screen.getByRole('button', { name: '新しい文書' }));
    fill('文書タイトル', '手順');
    fireEvent.click(screen.getByRole('button', { name: /作成して執筆/ }));
    await waitFor(() => expect(onError).toHaveBeenCalledWith('Error: 作成失敗'));
  });
  it('一覧の通信失敗を通知する', async () => {
    const onError = error();
    const { api } = mockApi(() => {
      throw new Error('一覧失敗');
    });
    render(
      <Library
        api={api}
        identity={{ ...identity, departments: [] }}
        edit={false}
        onOpen={vi.fn()}
        onError={onError}
      />,
    );
    await waitFor(() => expect(onError).toHaveBeenCalledWith('Error: 一覧失敗'));
  });
});

describe('文書編集と履歴', () => {
  function editorApi(fail = false) {
    return mockApi((path, method) => {
      if (fail && method) throw new Error('保存競合');
      if (path.endsWith('/draft'))
        return { document: doc, body: '# 本文', revision: 2, placements: [] };
      if (path.endsWith('/submissions')) return version;
      if (path.endsWith('/history'))
        return [
          { version: { ...version, id: 'v2', number: 2 }, submission },
          { version, submission: { ...submission, status: 'rejected', reason: '追記' } },
        ];
      if (path.includes('/diff')) return { diff: '+追記' };
      return [];
    });
  }
  it('編集を保存し申請し履歴差分を表示する', async () => {
    const { api, calls } = editorApi();
    const back = vi.fn();
    render(
      <DocumentPanel
        id="doc1"
        api={api}
        token="t"
        identity={identity}
        edit
        onBack={back}
        onError={error()}
      />,
    );
    await screen.findByDisplayValue('# 本文');
    fill('文書タイトル', '改訂');
    fill('Markdown本文', '# 改訂本文');
    expect(screen.getByRole('button', { name: '承認申請' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: '保存' }));
    await screen.findByText('保存しました。');
    fireEvent.click(screen.getByRole('button', { name: '承認申請' }));
    await screen.findByText('v1 を承認申請しました。');
    fireEvent.click(screen.getByRole('button', { name: '版履歴' }));
    await screen.findByText('v2');
    fireEvent.click(screen.getByRole('button', { name: '前の版と比較' }));
    await screen.findByText('+追記');
    fireEvent.click(screen.getByRole('button', { name: '文書一覧へ' }));
    expect(back).toHaveBeenCalled();
    expect(calls).toHaveBeenCalledWith(
      '/documents/doc1/draft',
      'PUT',
      expect.objectContaining({ body: '# 改訂本文' }),
    );
  });
  it('保存失敗時に入力を保持し離脱を確認する', async () => {
    const { api } = editorApi(true);
    const onError = error(),
      back = vi.fn();
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false);
    render(
      <DocumentPanel
        id="doc1"
        api={api}
        token="t"
        identity={identity}
        edit
        onBack={back}
        onError={onError}
      />,
    );
    await screen.findByDisplayValue('# 本文');
    fill('Markdown本文', '失わない内容');
    const event = new Event('beforeunload', { cancelable: true });
    window.dispatchEvent(event);
    expect(event.defaultPrevented).toBe(true);
    fireEvent.click(screen.getByRole('button', { name: '保存' }));
    await screen.findByText('未保存の変更があります。入力は保持されています。');
    expect(screen.getByLabelText('Markdown本文')).toHaveValue('失わない内容');
    fireEvent.click(screen.getByRole('button', { name: '文書一覧へ' }));
    expect(back).not.toHaveBeenCalled();
    confirm.mockReturnValue(true);
    fireEvent.click(screen.getByRole('button', { name: '文書一覧へ' }));
    expect(back).toHaveBeenCalled();
  });
  it('申請・履歴・比較の失敗を通知する', async () => {
    let fail = 'submit';
    const { api } = mockApi((path) => {
      if (path.endsWith('/draft'))
        return { document: doc, body: '本文', revision: 2, placements: [] };
      if (path.endsWith('/history') && fail !== 'history')
        return [
          { version: { ...version, id: 'v2' }, submission },
          { version, submission },
        ];
      throw new Error(fail);
    });
    const onError = error();
    render(
      <DocumentPanel
        id="doc1"
        api={api}
        token="t"
        identity={identity}
        edit
        onBack={vi.fn()}
        onError={onError}
      />,
    );
    await screen.findByDisplayValue('本文');
    fireEvent.click(screen.getByRole('button', { name: '承認申請' }));
    await waitFor(() => expect(onError).toHaveBeenCalledWith('Error: submit'));
    fail = 'history';
    fireEvent.click(screen.getByRole('button', { name: '版履歴' }));
    await waitFor(() => expect(onError).toHaveBeenCalledWith('Error: history'));
    fail = 'diff';
    fireEvent.click(screen.getByRole('button', { name: '版履歴' }));
    await screen.findByRole('button', { name: '前の版と比較' });
    fireEvent.click(screen.getByRole('button', { name: '前の版と比較' }));
    await waitFor(() => expect(onError).toHaveBeenCalledWith('Error: diff'));
  });
  it.each([true, false])('承認版を読み閲覧イベントを記録する: %s', async (ready) => {
    const { api, calls } = mockApi((path) =>
      path.startsWith('/metrics')
        ? {}
        : { document: doc, version, body: '# 承認本文', index_ready: ready },
    );
    render(
      <DocumentPanel
        id="doc1"
        api={api}
        token="t"
        identity={identity}
        edit={false}
        onBack={vi.fn()}
        onError={error()}
      />,
    );
    await screen.findByRole('heading', { name: '承認本文' });
    expect(calls).toHaveBeenCalledWith(
      '/metrics/views/doc1',
      'POST',
      expect.objectContaining({ department_id: 'd1' }),
    );
    expect(screen.getByText(ready ? /RAGへ反映済み/ : /RAGへの反映待ち/)).toBeVisible();
  });
  it('読込失敗を通知する', async () => {
    const { api } = mockApi(() => {
      throw new Error('読込失敗');
    });
    const onError = error();
    render(
      <DocumentPanel
        id="doc1"
        api={api}
        token="t"
        identity={identity}
        edit={false}
        onBack={vi.fn()}
        onError={onError}
      />,
    );
    await waitFor(() => expect(onError).toHaveBeenCalledWith('Error: 読込失敗'));
  });
});

describe('画像とOCR', () => {
  it('認可付き画像を表示しアンマウントでURLを解放する', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(new Blob(['png'])));
    URL.createObjectURL = vi.fn(() => 'blob:photo');
    URL.revokeObjectURL = vi.fn();
    const { unmount } = render(<ProtectedImage token="t" id="a1" />);
    await screen.findByRole('img');
    unmount();
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:photo');
  });
  it('画像の取得失敗を表示する', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('denied'));
    render(<ProtectedImage token="t" id="a1" version="v1" />);
    await screen.findByText('画像を表示できません。');
  });
  it('添付後に文字を訂正して新runへ切り替え配置を削除する', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(new Blob(['png'])));
    URL.createObjectURL = vi.fn(() => 'blob:image');
    URL.revokeObjectURL = vi.fn();
    const { api, calls } = mockApi((path, method) =>
      method === 'POST'
        ? path.includes('/documents/')
          ? { asset: { id: 'a2' }, ocr_run: { id: 'o2' } }
          : { ocr_run: { id: 'o3' } }
        : { regions: [region], engine: 'tesseract', status: 'ready' },
    );
    const change = vi.fn();
    render(
      <Images
        api={api}
        token="t"
        documentId="doc1"
        edit
        placements={[placement]}
        onChange={change}
        offset={30}
        onError={error()}
      />,
    );
    await screen.findByDisplayValue('画像の文字');
    fill('OCR文字', '訂正した文字\n追加した文字');
    fireEvent.click(screen.getByRole('button', { name: 'OCRを確認して確定' }));
    await waitFor(() => expect(change).toHaveBeenCalledWith([{ ...placement, ocr_run_id: 'o3' }]));
    expect(calls).toHaveBeenCalledWith(
      '/images/a1/ocr',
      'POST',
      expect.objectContaining({ confirmed: true }),
    );
    fireEvent.change(screen.getByLabelText('画像を添付'), {
      target: { files: [new File(['png'], 'image.png', { type: 'image/png' })] },
    });
    await waitFor(() =>
      expect(change).toHaveBeenCalledWith(
        expect.arrayContaining([expect.objectContaining({ asset_id: 'a2', offset: 30 })]),
      ),
    );
    fireEvent.click(screen.getByRole('button', { name: '配置を削除' }));
    expect(change).toHaveBeenCalledWith([]);
  });
  it('OCR失敗と添付失敗と確定失敗を表示する', async () => {
    const onError = error();
    const { api } = mockApi((_, method) => {
      if (method === 'POST') throw new Error('画像処理失敗');
      return { regions: [], status: 'failed', engine: 'tesseract' };
    });
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('image'));
    render(
      <Images
        api={api}
        token="t"
        documentId="doc1"
        edit
        placements={[placement]}
        onChange={vi.fn()}
        offset={0}
        onError={onError}
      />,
    );
    await screen.findByText('OCRに失敗しました。文字を入力して確認してください。');
    fireEvent.click(screen.getByRole('button', { name: 'OCRを確認して確定' }));
    await waitFor(() => expect(onError).toHaveBeenCalled());
    fireEvent.change(screen.getByLabelText('画像を添付'), {
      target: { files: [new File(['bad'], 'bad.png')] },
    });
    await waitFor(() => expect(onError).toHaveBeenCalledTimes(2));
    fireEvent.change(screen.getByLabelText('画像を添付'), { target: { files: [] } });
  });
  it('承認版のOCRを読取専用で表示する', async () => {
    const { api } = mockApi(() => ({ regions: [region], status: 'ready', engine: 'tesseract' }));
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('image'));
    render(
      <Images
        api={api}
        token="t"
        documentId="doc1"
        versionId="v1"
        edit={false}
        placements={[placement]}
        onChange={vi.fn()}
        offset={0}
        onError={error()}
      />,
    );
    await screen.findByText('画像の文字');
    expect(screen.queryByLabelText('OCR文字')).toBeNull();
  });
  it('OCRの取得失敗を通知する', async () => {
    const { api } = mockApi(() => {
      throw new Error('ocr');
    });
    const onError = error();
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('image'));
    render(
      <Images
        api={api}
        token="t"
        documentId="doc1"
        edit
        placements={[placement]}
        onChange={vi.fn()}
        offset={0}
        onError={onError}
      />,
    );
    await waitFor(() => expect(onError).toHaveBeenCalledWith('Error: ocr'));
  });
});

describe('承認画面', () => {
  it.each(['approved', 'rejected'])('本文を確認して審査結果を保存する: %s', async (decision) => {
    const { api, calls } = mockApi((path, method) =>
      method === 'POST'
        ? submission
        : path === '/reviews'
          ? [{ submission, title: doc.title, can_review: true }]
          : { document: doc, version, body: '# 申請本文', index_ready: false },
    );
    render(<Reviews api={api} token="t" onError={error()} />);
    await screen.findByText(doc.title);
    fireEvent.click(screen.getByRole('button', { name: /内容を確認/ }));
    await screen.findByRole('heading', { name: '申請本文' });
    fill('審査コメント（却下時は必須）', '要件を確認');
    fireEvent.click(
      screen.getByRole('button', {
        name: decision === 'approved' ? 'この版を承認' : '理由を残して却下',
      }),
    );
    await screen.findByRole('status');
    expect(calls).toHaveBeenCalledWith(
      '/reviews/s1/decision',
      'POST',
      expect.objectContaining({ decision, reason: '要件を確認' }),
    );
  });
  it('空の審査一覧を表示する', async () => {
    const { api } = mockApi();
    render(<Reviews api={api} token="t" onError={error()} />);
    await screen.findByText('審査対象はありません');
  });
  it('本文取得と承認失敗を通知し一覧へ戻れる', async () => {
    let fail = 'open';
    const { api } = mockApi((path, method) => {
      if (path === '/reviews') return [{ submission, title: doc.title, can_review: true }];
      if (fail === 'open' || method === 'POST') throw new Error(fail);
      return { document: doc, version, body: '本文', index_ready: false };
    });
    const onError = error();
    render(<Reviews api={api} token="t" onError={onError} />);
    await screen.findByText(doc.title);
    fireEvent.click(screen.getByRole('button', { name: /内容を確認/ }));
    await waitFor(() => expect(onError).toHaveBeenCalledWith('Error: open'));
    fail = 'decision';
    fireEvent.click(screen.getByRole('button', { name: /内容を確認/ }));
    await screen.findByText('本文');
    fireEvent.click(screen.getByRole('button', { name: 'この版を承認' }));
    await waitFor(() => expect(onError).toHaveBeenCalledWith('Error: decision'));
    fireEvent.click(screen.getByRole('button', { name: '一覧へ戻る' }));
    expect(screen.getByRole('button', { name: /内容を確認/ })).toBeVisible();
  });
  it('審査一覧の取得失敗を通知する', async () => {
    const { api } = mockApi(() => {
      throw new Error('reviews');
    });
    const onError = error();
    render(<Reviews api={api} token="t" onError={onError} />);
    await waitFor(() => expect(onError).toHaveBeenCalledWith('Error: reviews'));
  });
});

describe('根拠付きチャット', () => {
  it('質問・追質問・引用・履歴の再認可を表示する', async () => {
    const { api, calls } = mockApi((_, method) =>
      method === 'POST'
        ? answer
        : [{ ...answer, status: 'hidden', citations: [], answer: '表示を停止' }],
    );
    const open = vi.fn();
    render(<Chat api={api} identity={identity} onOpen={open} onError={error()} />);
    fill('質問', '開発フロー');
    fireEvent.change(screen.getByLabelText('利用部署'), { target: { value: 'd1' } });
    fireEvent.click(screen.getByRole('button', { name: '質問を送信' }));
    await screen.findByText('承認します');
    fireEvent.click(screen.getByRole('button', { name: /開発ガイド/ }));
    expect(open).toHaveBeenCalledWith('doc1');
    fireEvent.click(screen.getByRole('button', { name: '履歴を再確認' }));
    await screen.findByText('表示を停止');
    fill('質問', '追加の質問');
    fireEvent.click(screen.getByRole('button', { name: '質問を送信' }));
    await waitFor(() =>
      expect(calls).toHaveBeenCalledWith(
        '/chat',
        'POST',
        expect.objectContaining({ conversation_id: 'c1' }),
      ),
    );
  });
  it('質問失敗と履歴再取得失敗を通知する', async () => {
    let fail = true;
    const { api } = mockApi((_, method) => {
      if (fail || method !== 'POST') throw new Error('chat');
      return answer;
    });
    const onError = error();
    render(
      <Chat api={api} identity={{ ...identity, mode: 'aws' }} onOpen={vi.fn()} onError={onError} />,
    );
    fill('質問', '質問');
    fireEvent.click(screen.getByRole('button', { name: '質問を送信' }));
    await waitFor(() => expect(onError).toHaveBeenCalled());
    fail = false;
    fireEvent.click(screen.getByRole('button', { name: '質問を送信' }));
    await screen.findByText('承認します');
    fireEvent.click(screen.getByRole('button', { name: '履歴を再確認' }));
    await waitFor(() => expect(onError).toHaveBeenCalledTimes(2));
  });
});

describe('部署管理', () => {
  function groupApi(handler?: (path: string, method?: string, data?: unknown) => unknown) {
    return mockApi((path, method, data) => {
      if (method) return handler ? handler(path, method, data) : {};
      if (path.startsWith('/documents'))
        return [
          doc,
          { ...doc, id: 'doc2', title: '停止済み', status: 'withdrawn' },
          { ...doc, id: 'doc3', title: '削除済み', status: 'deleted' },
        ];
      if (path.includes('/metrics'))
        return {
          questions: 3,
          views: 5,
          unique_viewers: 2,
          outcomes: { answered: 2, held: 1, failed: 0 },
          generated_at: doc.updated_at,
          timezone: 'Asia/Tokyo',
          documents: [{ id: 'doc1', title: doc.title, views: 5, contributions: 2 }],
        };
      return [
        { membership: { ...identity.memberships[0], user_id: 'u2' }, display_name: '別の担当者' },
        {
          membership: {
            ...identity.memberships[0],
            id: 'm2',
            user_id: 'u3',
            active: false,
            can_author: false,
            can_review: false,
            leader: false,
          },
          display_name: '停止中の担当者',
        },
      ];
    });
  }
  it('リーダーに統計と公開管理と所属管理を表示する', async () => {
    const { api, calls } = groupApi();
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    render(<Groups api={api} identity={identity} onError={error()} />);
    await screen.findByText('別の担当者');
    expect(screen.getByText('3')).toBeVisible();
    fireEvent.change(screen.getByLabelText('管理部署'), { target: { value: 'd1' } });
    fireEvent.change(screen.getByLabelText('開発ガイドの公開範囲'), {
      target: { value: 'organization' },
    });
    await waitFor(() =>
      expect(calls).toHaveBeenCalledWith(
        '/documents/doc1/policy',
        'PUT',
        expect.objectContaining({ visibility: 'organization' }),
      ),
    );
    fireEvent.click(screen.getByRole('button', { name: '公開を再開' }));
    await waitFor(() =>
      expect(calls).toHaveBeenCalledWith(
        '/documents/doc2/policy',
        'PUT',
        expect.objectContaining({ status: 'active' }),
      ),
    );
    fireEvent.click(screen.getAllByRole('button', { name: '公開停止' })[0]!);
    await waitFor(() =>
      expect(calls).toHaveBeenCalledWith(
        '/documents/doc1/policy',
        'PUT',
        expect.objectContaining({ status: 'withdrawn' }),
      ),
    );
    fireEvent.click(screen.getAllByRole('button', { name: '削除' })[0]!);
    await waitFor(() =>
      expect(calls).toHaveBeenCalledWith(
        '/documents/doc1/policy',
        'PUT',
        expect.objectContaining({ status: 'deleted' }),
      ),
    );
    fireEvent.click(screen.getByRole('button', { name: '所属を停止' }));
    await waitFor(() =>
      expect(calls).toHaveBeenCalledWith(
        '/groups/memberships',
        'PUT',
        expect.objectContaining({ active: false }),
      ),
    );
    fireEvent.click(screen.getByRole('button', { name: '所属を再開' }));
    await waitFor(() =>
      expect(calls).toHaveBeenCalledWith(
        '/groups/memberships',
        'PUT',
        expect.objectContaining({ active: true }),
      ),
    );
  });
  it('削除取消と各更新失敗を通知する', async () => {
    const { api, calls } = groupApi(() => {
      throw new Error('groups');
    });
    vi.spyOn(window, 'confirm').mockReturnValue(false);
    const onError = error();
    render(<Groups api={api} identity={identity} onError={onError} />);
    await screen.findByText('別の担当者');
    fireEvent.click(screen.getAllByRole('button', { name: '削除' })[0]!);
    expect(calls.mock.calls.filter((c) => c[1])).toHaveLength(0);
    fireEvent.click(screen.getAllByRole('button', { name: '公開停止' })[0]!);
    await waitFor(() => expect(onError).toHaveBeenCalledTimes(1));
    fireEvent.change(screen.getByLabelText('開発ガイドの公開範囲'), {
      target: { value: 'organization' },
    });
    await waitFor(() => expect(onError).toHaveBeenCalledTimes(2));
    fireEvent.click(screen.getByRole('button', { name: '所属を停止' }));
    await waitFor(() => expect(onError).toHaveBeenCalledTimes(3));
  });
  it('管理対象なしと統計取得失敗を区別する', async () => {
    const { api } = mockApi(() => {
      throw new Error('metrics');
    });
    const onError = error();
    const { rerender } = render(
      <Groups api={api} identity={{ ...identity, memberships: [] }} onError={onError} />,
    );
    expect(screen.getByText('部署リーダー向けの画面です')).toBeVisible();
    rerender(<Groups api={api} identity={identity} onError={onError} />);
    expect(onError).not.toHaveBeenCalled();
  });
  it('統計取得エラーを通知する', async () => {
    const { api } = mockApi(() => {
      throw new Error('metrics');
    });
    const onError = error();
    render(<Groups api={api} identity={identity} onError={onError} />);
    await waitFor(() => expect(onError).toHaveBeenCalledWith('Error: metrics'));
  });
});

describe('反映ジョブ', () => {
  it('未反映ジョブを実行し照合の不一致を表示する', async () => {
    const { api, calls } = mockApi((path, method) =>
      method === 'POST'
        ? {}
        : path.includes('reconcile')
          ? [{ document_id: 'doc1', reason: '旧版残留' }]
          : [
              {
                id: 'j1',
                document_id: 'doc1',
                kind: 'index',
                status: 'pending',
                attempts: 0,
                error_code: '',
              },
              {
                id: 'j2',
                document_id: 'doc2',
                kind: 'purge',
                status: 'failed',
                attempts: 5,
                error_code: 'integrity',
              },
            ],
    );
    render(<Operations api={api} onError={error()} />);
    await screen.findByText('検索への反映');
    fireEvent.click(screen.getAllByRole('button', { name: '実行・再処理' })[0]!);
    await waitFor(() =>
      expect(calls).toHaveBeenCalledWith('/operations/jobs/j1', 'POST', undefined),
    );
    fireEvent.click(screen.getByRole('button', { name: '正本と索引を照合' }));
    await screen.findByText('doc1: 旧版残留');
    expect(screen.getByText('integrity')).toBeVisible();
  });
  it('ジョブ実行と照合の失敗を通知する', async () => {
    const { api } = mockApi((path) => {
      if (path === '/operations/jobs')
        return [
          {
            id: 'j1',
            document_id: 'doc1',
            kind: 'index',
            status: 'pending',
            attempts: 0,
            error_code: '',
          },
        ];
      throw new Error('job');
    });
    const onError = error();
    render(<Operations api={api} onError={onError} />);
    await screen.findByText('検索への反映');
    fireEvent.click(screen.getByRole('button', { name: '実行・再処理' }));
    await waitFor(() => expect(onError).toHaveBeenCalledTimes(1));
    fireEvent.click(screen.getByRole('button', { name: '正本と索引を照合' }));
    await waitFor(() => expect(onError).toHaveBeenCalledTimes(2));
  });
  it('一覧の取得失敗を通知する', async () => {
    const { api } = mockApi(() => {
      throw new Error('jobs');
    });
    const onError = error();
    render(<Operations api={api} onError={onError} />);
    await waitFor(() => expect(onError).toHaveBeenCalledWith('Error: jobs'));
  });
});

it('本文の指定offsetに画像を並べて残りの本文を保つ', async () => {
  vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('image'));
  render(
    <PlacedDocument
      body={'前半\n\n後半'}
      placements={[
        { id: 'p2', asset_id: 'a2', ocr_run_id: 'o2', heading: '後図', offset: 6 },
        { id: 'p1', asset_id: 'a1', ocr_run_id: 'o1', heading: '前図', offset: 2 },
      ]}
      token="t"
    />,
  );
  const captions = document.querySelectorAll('figcaption');
  expect(Array.from(captions, (c) => c.textContent)).toEqual(['前図', '後図']);
  expect(screen.getByText('前半')).toBeVisible();
  await screen.findAllByText('画像を表示できません。');
});
