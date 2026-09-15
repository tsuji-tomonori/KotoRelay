/** 実アプリと実DBをPlaywrightで操作し、導入動画用の録画・静止画を収録する。 */
import { chromium, request, expect } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const output = path.resolve('artifacts/intro-capture');
const baseURL = process.env.KOTORELAY_CAPTURE_URL ?? 'http://localhost:4321';
const title = '出張申請ガイド';
const body = '# 出張の申請期限\n\n出張の5営業日前までに、申請フォームを提出してください。\n\n## 申請に必要な情報\n\n行き先・目的・日程・費用の見込みを記入します。';
const entries = [];
await mkdir(output, { recursive: true });
const client = await request.newContext({ baseURL });

async function api(persona, route, method = 'GET', data) {
  const response = await client.fetch('/api' + route, {
    method,
    headers: { Authorization: `Bearer demo-${persona}`, 'Idempotency-Key': crypto.randomUUID() },
    data,
  });
  if (!response.ok()) throw new Error(`${route}: ${response.status()} ${await response.text()}`);
  return response.json();
}
const identity = await api('author', '/groups/me');
const department = identity.departments[0].id;
async function indexPending() {
  const jobs = await api('operator', '/operations/jobs');
  for (const job of jobs.filter((job) => job.status === 'pending'))
    await api('operator', `/operations/jobs/${job.id}`, 'POST');
}
async function addPublished(title, body) {
  const doc = await api('author', '/documents', 'POST', { title, department_id: department });
  const draft = await api('author', `/documents/${doc.id}/draft`);
  await api('author', `/documents/${doc.id}/draft`, 'PUT', { title, body, revision: draft.revision });
  const saved = await api('author', `/documents/${doc.id}/draft`);
  const version = await api('author', `/documents/${doc.id}/submissions`, 'POST', { revision: saved.revision });
  const reviews = await api('reviewer', '/reviews');
  const item = reviews.find((r) => r.submission.version_id === version.id);
  await api('reviewer', `/reviews/${item.submission.id}/decision`, 'POST', { decision: 'approved', manifest_hash: version.manifest_hash });
  await indexPending();
}
// 実在人物や業務情報を使わず、実API経由で収録専用の文書を準備する。
await addPublished('入社初日のチェックリスト', '# 初日の準備\n\nPCを受け取り、チームの案内を確認しましょう。');
await addPublished('経費精算ガイド', '# 経費の精算\n\n領収書を添付して月末までに精算申請します。');
const browser = await chromium.launch();
async function actor(name, role) {
  const context = await browser.newContext({ baseURL, viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1,
    locale: 'ja-JP', reducedMotion: 'reduce', recordVideo: { dir: path.join(output, 'raw'), size: { width: 1600, height: 900 } } });
  const page = await context.newPage();
  const origin = Date.now();
  const marks = [];
  page.on('pageerror', (error) => { throw error; });
  await page.goto('/');
  await page.getByLabel('サンプルの役割').selectOption(role);
  await page.getByRole('button', { name: 'ローカルで始める' }).click();
  await expect(page.getByRole('button', { name: 'ログアウト' })).toBeVisible();
  async function shot(id) {
    await page.screenshot({ path: path.join(output, `${name}-${id}.png`) });
  }
  async function mark(id) { marks.push({ id, seconds: (Date.now() - origin) / 1000 }); }
  async function hold(ms) { await page.waitForTimeout(ms); }
  async function click(locator) {
    await locator.scrollIntoViewIfNeeded();
    const box = await locator.boundingBox();
    if (box) await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 15 });
    await hold(350);
    await locator.click();
  }
  async function finish() {
    await mark('end');
    const video = page.video();
    await context.close();
    await video.saveAs(path.join(output, `${name}.webm`));
    entries.push({ name, marks, video: `${name}.webm`, viewport: { width: 1600, height: 900 } });
  }
  return { page, mark, shot, hold, click, finish };
}

try {
  const author = await actor('author', 'author');
  await author.click(author.page.getByRole('button', { name: '執筆', exact: true }));
  await expect(author.page.getByRole('heading', { name: '執筆', exact: true })).toBeVisible();
  await author.mark('create'); await author.shot('workspace'); await author.hold(900);
  await author.click(author.page.getByRole('button', { name: '新しい文書', exact: true }));
  await author.page.getByLabel('文書タイトル').pressSequentially(title, { delay: 90 });
  await author.shot('new-document'); await author.hold(650);
  await author.click(author.page.getByRole('button', { name: '作成して執筆する' }));
  await expect(author.page.getByLabel('Markdown本文')).toBeEnabled();
  await author.mark('write');
  await author.page.getByLabel('Markdown本文').fill('');
  await author.page.getByLabel('Markdown本文').pressSequentially(body, { delay: 28 });
  await author.shot('preview'); await author.hold(1400);
  await author.click(author.page.getByRole('button', { name: '保存', exact: true }));
  await expect(author.page.getByText('保存しました。', { exact: true })).toBeVisible();
  await author.shot('saved'); await author.mark('submit'); await author.hold(700);
  await author.click(author.page.getByRole('button', { name: '承認申請', exact: true }));
  await expect(author.page.getByText(/第1版を承認申請しました/)).toBeVisible();
  await author.shot('submitted'); await author.hold(1900); await author.finish();

  const reviewer = await actor('reviewer', 'reviewer');
  await reviewer.click(reviewer.page.getByRole('button', { name: '審査', exact: true }));
  await expect(reviewer.page.locator('.review-row').filter({ hasText: title })).toBeVisible();
  await reviewer.mark('review'); await reviewer.shot('inbox'); await reviewer.hold(1200);
  await reviewer.click(reviewer.page.locator('.review-row').filter({ hasText: title }).getByRole('button', { name: '内容を確認' }));
  await expect(reviewer.page.getByRole('heading', { name: '出張の申請期限', exact: true })).toBeVisible();
  await reviewer.shot('content'); await reviewer.hold(1500);
  await reviewer.click(reviewer.page.getByRole('button', { name: 'この版を承認', exact: true }));
  await expect(reviewer.page.getByRole('dialog')).toBeVisible();
  await reviewer.shot('confirm'); await reviewer.hold(1100);
  await reviewer.click(reviewer.page.getByRole('button', { name: '承認する', exact: true }));
  await expect(reviewer.page.getByText(/第1版を承認しました/)).toBeVisible();
  await reviewer.shot('approved'); await reviewer.hold(1800); await reviewer.finish();
  // 承認と検索反映は別処理。実装の運用APIで検索へ反映してから閲覧者へ切り替える。
  await indexPending();

  const reader = await actor('reader', 'reader');
  await expect(reader.page.getByText(title, { exact: true })).toBeVisible();
  await reader.mark('library'); await reader.shot('library'); await reader.hold(1600);
  await reader.page.getByPlaceholder('タイトルを入力').pressSequentially('出張', { delay: 220 });
  await reader.click(reader.page.getByRole('button', { name: '検索する', exact: true }));
  await expect(reader.page.getByText('経費精算ガイド', { exact: true })).toHaveCount(0);
  await reader.shot('filtered'); await reader.hold(1800);
  await reader.mark('chat');
  await reader.click(reader.page.getByRole('button', { name: 'RAGチャット', exact: true }));
  await expect(reader.page.getByRole('heading', { name: '知りたいことを、聞いてみましょう。' })).toBeVisible();
  await reader.shot('welcome'); await reader.hold(1100);
  await reader.page.getByRole('textbox', { name: '質問', exact: true }).pressSequentially('出張の申請期限は？', { delay: 110 });
  await reader.shot('question'); await reader.hold(700);
  await reader.click(reader.page.getByRole('button', { name: '質問を送信' }));
  await expect(reader.page.getByText('回答済み', { exact: true })).toBeVisible();
  await expect(reader.page.locator('.answer-bubble')).toContainText('5営業日前');
  await reader.mark('answer'); await reader.shot('answer'); await reader.hold(2800);
  await reader.mark('citation');
  await reader.click(reader.page.locator('.citations').getByRole('button').filter({ hasText: title }).first());
  await expect(reader.page.getByRole('heading', { name: title, exact: true })).toBeVisible();
  await expect(reader.page.getByText('第1版 · RAGへ反映済み')).toBeVisible();
  await reader.shot('citation'); await reader.hold(3200); await reader.finish();
} finally {
  await browser.close(); await client.dispose();
  await writeFile(path.join(output, 'capture-manifest.json'), JSON.stringify({ sourceCommit: process.env.GITHUB_SHA ?? null, baseURL, mode: 'local', note: '実アプリを実API・実PostgreSQLで操作。画面改変・通信モックなし。ローカル回答は文書の根拠抜粋。', recordings: entries }, null, 2));
}
