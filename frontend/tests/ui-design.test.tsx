import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App, {
  DocumentPanel,
  Library,
  Images,
  Reviews,
  Chat,
  Groups,
  Operations,
  PlacedDocument,
  ProtectedImage,
} from '../src/components/App';
import { PolicyEditor } from '../src/features/groups/Groups';
import { documentParts, relocatePlacements } from '../src/features/documents/PlacedDocument';
import { headings } from '../src/components/Markdown';
import { jobLabel, type Identity } from '../src/lib/api';
import {
  identity,
  doc,
  version,
  submission,
  placement,
  region,
  answer,
  mockApi,
  fill,
} from './fixtures';
const snapshot = { document: doc, version, body: '# 手順\n\n本文', index_ready: true };
const draft = { document: doc, body: '# 手順\n\n本文', revision: 2, placements: [] };
const metrics = {
  questions: 1,
  views: 2,
  unique_viewers: 1,
  outcomes: { answered: 1, held: 0, failed: 0 },
  generated_at: doc.updated_at,
  timezone: 'Asia/Tokyo',
  documents: [],
};
const multi: Identity = {
  ...identity,
  directory: [
    { id: 'd1', name: '開発部' },
    { id: 'd2', name: '営業部' },
  ],
  departments: [...identity.departments, { id: 'd2', name: '営業部' }],
  memberships: [
    ...identity.memberships,
    { ...identity.memberships[0]!, id: 'm2', department_id: 'd2' },
  ],
};
function fetchApp(person = identity) {
  sessionStorage.setItem('kotorelay-token', 'demo-author');
  return vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
    const path = String(input);
    return new Response(
      JSON.stringify(
        path.endsWith('/groups/me')
          ? person
          : path.includes('/documents?')
            ? { items: [doc], has_next: false }
            : path.endsWith('/draft')
              ? draft
              : path.includes('/metrics/')
                ? {}
                : init?.method === 'POST'
                  ? answer
                  : snapshot,
      ),
    );
  });
}
async function editInApp() {
  render(<App />);
  await screen.findByRole('navigation', { name: 'メインナビゲーション' });
  fireEvent.click(screen.getByRole('button', { name: '執筆' }));
  fireEvent.click(await screen.findByRole('link', { name: doc.title }));
  await waitFor(() => expect(screen.getByLabelText('Markdown本文')).toHaveValue(draft.body));
  fill('Markdown本文', '未保存の大切な本文');
}

describe('全画面での未保存保護とアカウント', () => {
  it.each(['ナビ', 'ロゴ', '戻る', 'ログアウト'])(
    '%sからの離脱をキャンセルすると編集を保持する',
    async (target) => {
      fetchApp();
      await editInApp();
      const origin =
        target === 'ナビ'
          ? screen.getByRole('button', { name: 'RAGチャット' })
          : target === 'ロゴ'
            ? screen.getByRole('link', { name: /KotoRelay/ })
            : screen.getByRole('button', { name: target === '戻る' ? '文書一覧へ' : 'ログアウト' });
      origin.focus();
      fireEvent.click(origin);
      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveTextContent('未保存の変更');
      fireEvent(dialog, new Event('cancel', { cancelable: true }));
      expect(screen.getByLabelText('Markdown本文')).toHaveValue('未保存の大切な本文');
      expect(origin).toHaveFocus();
      fireEvent.click(origin);
      fireEvent.click(screen.getByRole('button', { name: '変更を破棄して移動' }));
      await waitFor(() => expect(screen.queryByLabelText('Markdown本文')).toBeNull());
    },
  );
  it('閲覧者のナビと開閉メニューと利用部署を明示する', async () => {
    fetchApp({
      ...multi,
      user: { ...multi.user, operator: false },
      memberships: multi.memberships.map((m) => ({
        ...m,
        leader: false,
        can_author: false,
        can_review: false,
      })),
    });
    render(<App />);
    await screen.findByRole('navigation', { name: 'メインナビゲーション' });
    expect(screen.queryByRole('button', { name: '執筆' })).toBeNull();
    expect(screen.queryByRole('button', { name: '審査' })).toBeNull();
    expect(screen.queryByRole('button', { name: '部署管理' })).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'メニュー' }));
    expect(screen.getByRole('button', { name: 'メニュー' })).toHaveAttribute(
      'aria-expanded',
      'true',
    );
    fill('利用部署', 'd2');
    expect(screen.getByLabelText('利用部署')).toHaveValue('d2');
    fireEvent.click(screen.getByRole('button', { name: 'RAGチャット' }));
    expect(screen.getByRole('button', { name: 'メニュー' })).toHaveAttribute(
      'aria-expanded',
      'false',
    );
    expect(screen.getByRole('button', { name: 'ログアウト' })).toBeVisible();
  });
  it('作成中のタイトルも保護し作成済みなら編集へ進める', async () => {
    const fetch = fetchApp();
    fetch.mockImplementation(
      async (input, init) =>
        new Response(
          JSON.stringify(
            String(input).endsWith('/groups/me')
              ? identity
              : String(input).includes('/documents?')
                ? { items: [], has_next: false }
                : init?.method === 'POST'
                  ? doc
                  : draft,
          ),
        ),
    );
    render(<App />);
    await screen.findByRole('navigation', { name: 'メインナビゲーション' });
    fireEvent.click(screen.getByRole('button', { name: '執筆' }));
    fireEvent.click(screen.getByRole('button', { name: '新しい文書' }));
    fill('文書タイトル', '保存するタイトル');
    fireEvent.click(screen.getByRole('button', { name: 'RAGチャット' }));
    fireEvent.click(screen.getByRole('button', { name: 'キャンセル' }));
    fireEvent.click(screen.getByRole('button', { name: '作成して執筆する' }));
    await screen.findByLabelText('Markdown本文');
    expect(screen.queryByRole('dialog')).toBeNull();
  });
});

describe('版と挿入位置の取り違え防止', () => {
  it('旧引用は新版本文を隠し明示操作の後だけ最新承認版を開く', async () => {
    const { api, calls } = mockApi((path) => (path.startsWith('/metrics') ? {} : snapshot));
    render(
      <DocumentPanel
        id="doc1"
        api={api}
        token="t"
        identity={identity}
        edit={false}
        citation={{ ...answer.citations[0]!, version_id: 'old' }}
        onBack={vi.fn()}
        onError={vi.fn()}
      />,
    );
    await screen.findByRole('heading', { name: '引用元が更新されています' });
    expect(screen.queryByText('本文')).toBeNull();
    expect(calls.mock.calls.some((c) => c[0].startsWith('/metrics'))).toBe(false);
    fireEvent.click(screen.getByRole('button', { name: '最新の承認版を開く' }));
    await screen.findByText('本文');
    expect(calls.mock.calls.some((c) => c[0].startsWith('/metrics'))).toBe(true);
  });
  it('引用版が一致する時だけ該当見出しへ移動し選択部署で閲覧記録する', async () => {
    const { api, calls } = mockApi((path) => (path.startsWith('/metrics') ? {} : snapshot));
    render(
      <DocumentPanel
        id="doc1"
        api={api}
        token="t"
        identity={multi}
        department="d2"
        edit={false}
        citation={answer.citations[0]}
        onBack={vi.fn()}
        onError={vi.fn()}
      />,
    );
    const heading = await screen.findByRole('heading', { name: '手順' });
    await waitFor(() => expect(heading).toHaveFocus());
    expect(calls).toHaveBeenCalledWith(
      '/metrics/views/doc1',
      'POST',
      expect.objectContaining({ department_id: 'd2' }),
    );
  });
  it('絵文字と重複見出しでも画像位置と一意の目次が一致する', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('image'));
    const body = '日😀\n\n# 同じ見出し\n\n後半\n\n# 同じ見出し\n';
    const parts = documentParts(body, [{ ...placement, offset: 2 }]);
    expect(parts[0]!.text).toBe('日😀');
    expect(parts[1]!.text).toContain('# 同じ見出し');
    render(
      <PlacedDocument
        body={body}
        placements={[{ ...placement, offset: 2, alt_text: '図の意味', caption: '業務図' }]}
        token="t"
        toc
      />,
    );
    const links = screen.getAllByRole('link', { name: '同じ見出し' });
    expect(links[0]!.getAttribute('href')).not.toBe(links[1]!.getAttribute('href'));
    expect(headings('```md\n# コード内\n```\n# 見出し')).toHaveLength(1);
    expect(screen.getByText('図1 業務図')).toBeVisible();
    await act(async () => {});
  });
  it.each([
    ['ab😀cd', 'ab追加😀cd', 3, 5],
    ['abcde', 'abe', 4, 2],
    ['abcde', 'axde', 2, 2],
    ['abc', 'abc', 2, 2],
  ])('本文編集による配置移動: %s → %s', (before, after, offset, expected) => {
    expect(
      relocatePlacements(String(before), String(after), [
        { ...placement, offset: Number(offset) },
      ])[0]!.offset,
    ).toBe(expected);
  });
  it('文書取得失敗の再試行と編集プレビュー切替で入力を失わない', async () => {
    let fail = true;
    const { api } = mockApi(() => {
      if (fail) throw new Error('load');
      return draft;
    });
    render(
      <DocumentPanel
        id="doc1"
        api={api}
        token="t"
        identity={identity}
        edit
        onBack={vi.fn()}
        onError={vi.fn()}
      />,
    );
    await screen.findByRole('button', { name: '再試行' });
    fail = false;
    fireEvent.click(screen.getByRole('button', { name: '再試行' }));
    await waitFor(() => expect(screen.getByLabelText('Markdown本文')).toHaveValue(draft.body));
    fill('Markdown本文', '# 編集内容');
    fireEvent.click(screen.getByRole('button', { name: 'プレビュー' }));
    expect(screen.getByRole('heading', { name: '編集内容' })).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: '編集' }));
    expect(screen.getByLabelText('Markdown本文')).toHaveValue('# 編集内容');
  });
});

describe('OCRを領域単位で編集する', () => {
  it('複数行の文字訂正後も領域IDと座標を保持し追加削除を区別する', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('image'));
    const second = { ...region, region_id: 'r2', text: '第二領域', x: 0.5, width: 0.2 };
    const { api, calls } = mockApi((_, method) =>
      method === 'POST'
        ? { ocr_run: { id: 'new' } }
        : { regions: [region, second], confirmed: false, status: 'ready', engine: 'tesseract' },
    );
    render(
      <Images
        api={api}
        token="t"
        documentId="doc1"
        edit
        placements={[placement]}
        onChange={vi.fn()}
        offset={0}
        onError={vi.fn()}
      />,
    );
    await screen.findByDisplayValue('第二領域');
    fill('図1・領域2の文字', '第二領域\n複数行の訂正');
    fireEvent.click(screen.getByRole('button', { name: '領域1を削除' }));
    fireEvent.click(screen.getByRole('button', { name: '文字領域を追加' }));
    fill('新しい領域の左位置', '0.3');
    fill('新しい領域の上位置', '0.3');
    fill('新しい領域の幅', '0.2');
    fill('新しい領域の高さ', '0.2');
    fireEvent.click(screen.getByRole('button', { name: 'この範囲で追加' }));
    fill('図1・領域2の文字', '手で追加した文字');
    fireEvent.click(screen.getByRole('button', { name: 'OCRを確認して確定' }));
    await waitFor(() =>
      expect(calls).toHaveBeenCalledWith(
        '/images/a1/ocr',
        'POST',
        expect.objectContaining({
          regions: [
            expect.objectContaining({
              region_id: 'r2',
              text: '第二領域\n複数行の訂正',
              x: 0.5,
              width: 0.2,
              confidence: null,
              order: 0,
            }),
            expect.objectContaining({
              text: '手で追加した文字',
              x: 0.3,
              y: 0.3,
              width: 0.2,
              height: 0.2,
              confidence: null,
              source: 'human',
              order: 1,
            }),
          ],
        }),
      ),
    );
  });
  it('画像の説明と配置を編集し不正な矩形の確定を防ぐ', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('image'));
    const { api } = mockApi(() => ({
      regions: [{ ...region, width: 0.5, height: 0.5 }],
      confirmed: true,
      status: 'ready',
      engine: 'tesseract',
    }));
    const change = vi.fn(),
      pending = vi.fn();
    render(
      <Images
        api={api}
        token="t"
        documentId="doc1"
        edit
        placements={[placement]}
        onChange={change}
        offset={0}
        onError={vi.fn()}
        onPending={pending}
      />,
    );
    await screen.findByDisplayValue('画像の文字');
    await waitFor(() => expect(pending).toHaveBeenLastCalledWith(false));
    fill('図1の代替テキスト', '受付から承認へ進む');
    fill('図1の説明文', '図の説明');
    fill('図1の挿入位置（文字数）', '2');
    expect(change).toHaveBeenCalledWith([expect.objectContaining({ offset: 2 })]);
    fireEvent.click(screen.getByRole('button', { name: '領域1を選択' }));
    expect(screen.getByLabelText('図1・領域1の文字')).toHaveFocus();
    fireEvent.click(screen.getByText('文字領域の位置・サイズ'));
    fill('図1・領域1の左位置', '0.9');
    expect(screen.getByRole('button', { name: 'OCRを確認して確定' })).toBeDisabled();
    for (const [label, value] of [
      ['左位置', '0.1'],
      ['上位置', '0.1'],
      ['幅', '0.2'],
      ['高さ', '0.2'],
    ])
      fill(`図1・領域1の${label}`, value!);
    expect(screen.getByRole('button', { name: 'OCRを確認して確定' })).toBeEnabled();
    fireEvent.click(screen.getByRole('button', { name: '文字領域を追加' }));
    fill('新しい領域の幅', '2');
    expect(screen.getByRole('button', { name: 'この範囲で追加' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: '文字領域を追加' }));
  });
  it('OCR読込失敗から再試行し手動訂正の確信度を未測定で表示する', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('image'));
    let fail = true;
    const { api } = mockApi(() => {
      if (fail) throw new Error('ocr');
      return {
        regions: [{ ...region, source: 'human', confidence: null }],
        status: 'ready',
        confirmed: true,
        engine: 'human',
      };
    });
    render(
      <Images
        api={api}
        token="t"
        documentId="doc1"
        edit={false}
        placements={[placement]}
        onChange={vi.fn()}
        offset={0}
        onError={vi.fn()}
      />,
    );
    await screen.findByRole('button', { name: '再試行' });
    fail = false;
    fireEvent.click(screen.getByRole('button', { name: '再試行' }));
    await screen.findByText('人による訂正・確信度は未測定');
  });
});

describe('管理操作と一覧の状態', () => {
  it('検索は確定後に実行し部署・状態・条件解除を反映する', async () => {
    const { api, calls } = mockApi(() => []);
    render(<Library api={api} identity={multi} edit onOpen={vi.fn()} onError={vi.fn()} />);
    await screen.findByText('担当する文書はまだありません');
    const before = calls.mock.calls.length;
    fill('文書を検索', '単語');
    fill('所有部署', 'd2');
    fill('文書の状態', 'withdrawn');
    expect(calls).toHaveBeenCalledTimes(before);
    fireEvent.click(screen.getByRole('button', { name: '検索する' }));
    await screen.findByText('条件に一致する文書はありません');
    expect(calls).toHaveBeenLastCalledWith(
      expect.stringContaining('department_id=d2'),
      undefined,
      undefined,
    );
    fireEvent.click(screen.getByRole('button', { name: '検索条件を解除' }));
    await screen.findByText('担当する文書はまだありません');
    expect(screen.getByLabelText('文書を検索')).toHaveValue('');
  });
  it('30件ちょうどの最終ページと総件数を混同せず失敗から再試行する', async () => {
    let fail = true;
    const { api } = mockApi(() => {
      if (fail) throw new Error('list');
      return {
        items: Array.from({ length: 30 }, (_, i) => ({
          ...doc,
          id: `d${i}`,
          published_number: 1,
          approved_at: doc.updated_at,
          index_ready: true,
          summary: '概要',
          review_number: 2,
          review_status: 'pending',
        })),
        has_next: false,
      };
    });
    render(<Library api={api} identity={identity} edit onOpen={vi.fn()} onError={vi.fn()} />);
    await screen.findByRole('button', { name: '再試行' });
    expect(screen.queryByText('担当する文書はまだありません')).toBeNull();
    fail = false;
    fireEvent.click(screen.getByRole('button', { name: '再試行' }));
    await screen.findByText('このページ 30件');
    expect(screen.getByRole('button', { name: '次へ' })).toBeDisabled();
  });
  it('部署と期間を切り替えると文書・統計・所属を同じ部署へ更新する', async () => {
    const { api, calls } = mockApi((path) =>
      path.startsWith('/documents')
        ? {
            items: [{ ...doc, title: path.includes('d2') ? '営業文書' : '開発文書' }],
            has_next: path.includes('offset=0'),
          }
        : path.startsWith('/metrics')
          ? metrics
          : [],
    );
    render(<Groups api={api} identity={multi} onError={vi.fn()} />);
    await screen.findByText('開発文書');
    fill('管理部署', 'd2');
    await screen.findByText('営業文書');
    expect(screen.queryByText('開発文書')).toBeNull();
    expect(calls.mock.calls.some((c) => c[0] === '/groups/d2/members')).toBe(true);
    fill('集計期間', '7');
    await waitFor(() => expect(screen.getAllByText(/過去7日間 · 営業部/)).toHaveLength(3));
    fireEvent.click(screen.getByRole('button', { name: '次へ' }));
    await waitFor(() =>
      expect(calls.mock.calls.some((c) => c[0].includes('offset=30'))).toBe(true),
    );
    fireEvent.click(screen.getByRole('button', { name: '前へ' }));
  });
  it('指定部署の公開先選択と公開停止を明示保存し取消できる', async () => {
    const { api, calls } = mockApi(() => ({}));
    const saved = vi.fn(),
      cancel = vi.fn();
    render(
      <PolicyEditor
        api={api}
        doc={doc}
        departmentName="開発部"
        identity={multi}
        onError={vi.fn()}
        onSaved={saved}
        onCancel={cancel}
      />,
    );
    fill('公開範囲', 'selected');
    expect(screen.getByRole('button', { name: '変更内容を確認' })).toBeDisabled();
    fireEvent.click(screen.getByRole('checkbox', { name: '営業部' }));
    fireEvent.click(screen.getByRole('checkbox', { name: '開発部' }));
    fireEvent.click(screen.getByRole('checkbox', { name: '開発部' }));
    fill('公開状態', 'withdrawn');
    fireEvent.click(screen.getByRole('button', { name: '変更内容を確認' }));
    expect(screen.getByRole('dialog')).toHaveTextContent('営業部');
    fireEvent.click(screen.getByRole('button', { name: '保存する' }));
    await waitFor(() => expect(saved).toHaveBeenCalled());
    expect(calls).toHaveBeenCalledWith(
      '/documents/doc1/policy',
      'PUT',
      expect.objectContaining({
        visibility: 'selected',
        shared_departments: ['d2'],
        status: 'withdrawn',
      }),
    );
    fireEvent.click(screen.getByRole('button', { name: '変更をキャンセル' }));
    expect(cancel).toHaveBeenCalled();
  });
  it('削除理由は監査用として送り公開設定の競合でも編集値を残す', async () => {
    let fail = true;
    const { api, calls } = mockApi(() => {
      if (fail) throw new Error('conflict');
      return {};
    });
    const saved = vi.fn();
    render(
      <PolicyEditor
        api={api}
        doc={doc}
        departmentName="開発部"
        identity={identity}
        onError={vi.fn()}
        onSaved={saved}
        onCancel={vi.fn()}
      />,
    );
    fill('公開範囲', 'organization');
    fireEvent.click(screen.getByRole('button', { name: '変更内容を確認' }));
    fireEvent.click(screen.getByRole('button', { name: '保存する' }));
    await screen.findByRole('alert');
    expect(screen.getByLabelText('公開範囲')).toHaveValue('organization');
    fill('公開範囲', 'department');
    fill('削除理由（必須）', '利用終了');
    fail = false;
    fireEvent.click(screen.getByRole('button', { name: '削除内容を確認' }));
    fireEvent.click(screen.getByRole('button', { name: '削除する' }));
    await waitFor(() => expect(saved).toHaveBeenCalled());
    expect(calls).toHaveBeenCalledWith(
      '/documents/doc1/policy',
      'PUT',
      expect.objectContaining({ reason: '利用終了', status: 'deleted' }),
    );
  });
  it('管理情報とジョブの読込失敗を0件に読み替えない', async () => {
    let fail = true;
    const { api } = mockApi((path) => {
      if (fail) throw new Error('load');
      return path.startsWith('/documents')
        ? { items: [], has_next: false }
        : path.startsWith('/metrics')
          ? metrics
          : [];
    });
    const { unmount } = render(<Groups api={api} identity={identity} onError={vi.fn()} />);
    await screen.findByRole('button', { name: '再試行' });
    fail = false;
    fireEvent.click(screen.getByRole('button', { name: '再試行' }));
    await screen.findByText('管理部署の文書はありません。');
    unmount();
    fail = true;
    render(<Operations api={api} onError={vi.fn()} />);
    await screen.findByRole('button', { name: '再試行' });
    fail = false;
    fireEvent.click(screen.getByRole('button', { name: '再試行' }));
    await screen.findByText('ジョブはありません。');
  });
  it.each([
    ['purge', 'pending', '削除待ち'],
    ['purge', 'retained', '保持期間中'],
    ['purge', 'done', '削除完了'],
    ['purge', 'failed', '削除失敗'],
    ['index', 'pending', '反映待ち'],
    ['index', 'done', '反映済み'],
    ['index', 'running', '反映中'],
    ['index', 'failed', '反映失敗'],
  ])('処理種別に合う状態を示す: %s %s', (kind, status, label) =>
    expect(jobLabel(kind!, status!)).toBe(label),
  );
});

it('引用を開いて戻っても回答を保持する', async () => {
  fetchApp();
  render(<App />);
  await screen.findByRole('navigation', { name: 'メインナビゲーション' });
  fireEvent.click(screen.getByRole('button', { name: 'RAGチャット' }));
  fill('質問', '開発フロー');
  fireEvent.click(screen.getByRole('button', { name: '質問を送信' }));
  await screen.findByText('承認します');
  fireEvent.click(screen.getByRole('button', { name: /開発ガイド.*手順/ }));
  await screen.findByRole('heading', { name: '手順' });
  fireEvent.click(screen.getByRole('button', { name: '文書一覧へ' }));
  expect(screen.getByText('承認します')).toBeVisible();
});
it('審査は申請版の本文と画像を配置し差分を表示する', async () => {
  vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('image'));
  const { api } = mockApi((path) =>
    path === '/reviews'
      ? [
          {
            submission,
            title: doc.title,
            version_number: 1,
            requested_by: '申請者',
            department_name: '開発部',
            can_review: true,
          },
        ]
      : path.includes('/diff')
        ? { diff: '-旧本文\n+新本文' }
        : path.startsWith('/images')
          ? { regions: [], status: 'ready', engine: 'human' }
          : {
              ...snapshot,
              document: { ...doc, latest_version_id: 'v0' },
              version: {
                ...version,
                manifest: JSON.stringify({
                  images: [{ placement: { ...placement, offset: 2, caption: '審査の図' } }],
                }),
              },
              body: '前半\n\n後半',
            },
  );
  render(<Reviews api={api} token="t" onError={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: /内容を確認/ }));
  await screen.findByText(/旧本文/);
  expect(screen.getByText('図1 審査の図')).toBeVisible();
  fireEvent.click(screen.getByRole('button', { name: 'この版を承認' }));
  fireEvent.click(screen.getByRole('button', { name: 'キャンセル' }));
  expect(screen.getByText('図1 審査の図')).toBeVisible();
  fireEvent.click(screen.getByRole('button', { name: '一覧へ戻る' }));
});
it('審査取得を再試行し自己申請の操作を提供しない', async () => {
  let fail = true;
  const { api } = mockApi(() => {
    if (fail) throw new Error('review');
    return [{ submission, title: doc.title, self_requested: true, can_review: true }];
  });
  render(<Reviews api={api} token="t" onError={vi.fn()} />);
  await screen.findByRole('button', { name: '再試行' });
  fail = false;
  fireEvent.click(screen.getByRole('button', { name: '再試行' }));
  await screen.findByText('自己申請のため審査できません');
  expect(screen.queryByRole('button', { name: /内容を確認/ })).toBeNull();
});
it('チャットの部署変更は会話を新規にし保留完了を短く通知する', async () => {
  const { api, calls } = mockApi(() => ({ ...answer, status: 'held', citations: [] }));
  render(<Chat api={api} identity={multi} onOpen={vi.fn()} onError={vi.fn()} />);
  fill('質問', '不足する質問');
  fireEvent.click(screen.getByRole('button', { name: '質問を送信' }));
  await screen.findByText(/質問を具体化してください/);
  fill('利用部署', 'd2');
  expect(screen.queryByText('不足する質問')).toBeNull();
  fill('質問', '別部署の質問');
  fireEvent.click(screen.getByRole('button', { name: '質問を送信' }));
  await waitFor(() =>
    expect(calls).toHaveBeenLastCalledWith(
      '/chat',
      'POST',
      expect.objectContaining({ department_id: 'd2', conversation_id: null }),
    ),
  );
});
it('画像の認証対象が切り替わったら古いBlobを表示しない', async () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(new Blob(['img'])));
  URL.createObjectURL = vi.fn(() => 'blob:old');
  URL.revokeObjectURL = vi.fn();
  const { rerender } = render(<ProtectedImage id="a1" token="t" alt="旧画像" />);
  await screen.findByAltText('旧画像');
  vi.mocked(globalThis.fetch).mockRejectedValue(new Error('denied'));
  rerender(<ProtectedImage id="a2" token="t" alt="新画像" />);
  await screen.findByText('画像を表示できません。');
  expect(screen.queryByAltText('旧画像')).toBeNull();
  expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:old');
});

it('OCR確定の通信中に変更した代替テキストと配置を上書きしない', async () => {
  vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('image'));
  let finish: (value: unknown) => void = () => {};
  const { api } = mockApi((_, method) =>
    method === 'POST'
      ? new Promise((resolve) => {
          finish = resolve;
        })
      : { regions: [region], status: 'ready', engine: 'tesseract' },
  );
  const change = vi.fn();
  const props = {
    api,
    token: 't',
    documentId: 'doc1',
    edit: true,
    onChange: change,
    offset: 0,
    onError: vi.fn(),
  };
  const { rerender } = render(<Images {...props} placements={[placement]} />);
  await screen.findByDisplayValue('画像の文字');
  fireEvent.click(screen.getByRole('button', { name: 'OCRを確認して確定' }));
  const updated = { ...placement, offset: 5, alt_text: '通信中に入力した説明' };
  rerender(<Images {...props} placements={[updated]} />);
  await act(async () => finish({ ocr_run: { id: 'corrected' } }));
  expect(change).toHaveBeenCalledWith([{ ...updated, ocr_run_id: 'corrected' }]);
});
