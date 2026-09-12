import { describe, it, expect, vi } from 'vitest';
import { ApiError, createApi, formatDate, getImage, statusLabel } from '../src/lib/api';
import { safeLink } from '../src/components/Markdown';
describe('APIの認証とエラー処理', () => {
  it('GET要求にBearerとno-storeを付ける', async () => {
    const fetcher = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(new Response(JSON.stringify({ id: '1' })));
    expect(await createApi('token')('/documents')).toEqual({ id: '1' });
    expect(fetcher).toHaveBeenCalledWith(
      '/api/documents',
      expect.objectContaining({
        cache: 'no-store',
        method: 'GET',
        headers: { Authorization: 'Bearer token' },
      }),
    );
  });
  it('JSONと冪等キーを送る', async () => {
    const fetcher = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('{}'));
    await createApi('t')('/reviews', 'POST', { decision: 'approved' }, 'key');
    expect(fetcher).toHaveBeenCalledWith(
      '/api/reviews',
      expect.objectContaining({
        body: '{"decision":"approved"}',
        headers: {
          Authorization: 'Bearer t',
          'Content-Type': 'application/json',
          'Idempotency-Key': 'key',
        },
      }),
    );
  });
  it('FormDataの境界をブラウザに委ねる', async () => {
    const f = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('{}'));
    const data = new FormData();
    data.append('file', new Blob(['image']));
    await createApi('t')('/images', 'POST', data);
    expect(f).toHaveBeenCalledWith(
      '/api/images',
      expect.objectContaining({ body: data, headers: { Authorization: 'Bearer t' } }),
    );
  });
  it('入力を含めず業務エラーを返す', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('{"code":"conflict","message":"競合"}', { status: 409 }),
    );
    await expect(createApi('t')('/draft')).rejects.toEqual(new ApiError(409, 'conflict', '競合'));
  });
  it('ネットワーク失敗を上位へ伝える', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('offline'));
    await expect(createApi('t')('/draft')).rejects.toThrow('offline');
  });
  it('画像に認証を付けてBlob URLを作る', async () => {
    const f = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(new Blob(['png'])));
    URL.createObjectURL = vi.fn(() => 'blob:image');
    expect(await getImage('t', 'id', 'v1')).toBe('blob:image');
    expect(f).toHaveBeenCalledWith(
      '/api/images/id?version_id=v1',
      expect.objectContaining({ headers: { Authorization: 'Bearer t' } }),
    );
  });
  it('下書き画像と拒否応答を扱う', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 404 }));
    await expect(getImage('t', 'id')).rejects.toThrow('画像を取得できません。');
  });
  it('日本時間と未知状態を表示する', () => {
    expect(formatDate('2026-09-12T00:00:00Z')).toContain('9:00');
    expect(statusLabel('approved')).toBe('承認済み');
    expect(statusLabel('new')).toBe('new');
  });
});
describe('Markdownのリンク安全性', () => {
  it.each([
    'javascript:alert(1)',
    'data:text/html,test',
    '//evil.example',
    'file:///etc/passwd',
    'not a url',
  ])('危険または不明なURLを拒否する: %s', (url) => {
    expect(safeLink(url)).toBeUndefined();
  });
  it.each(['https://example.com', 'http://example.com', '#heading', '/document'])(
    '許可したURLを維持する: %s',
    (url) => {
      expect(safeLink(url)).toBe(url);
    },
  );
});
