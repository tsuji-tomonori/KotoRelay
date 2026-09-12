import { test, expect, type Page, type APIRequestContext, type TestInfo } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';

async function step(
  page: Page,
  info: TestInfo,
  phase: 'Given' | 'When' | 'Then',
  description: string,
  action: () => Promise<void>,
) {
  await test.step(`${phase}: ${description}`, async () => {
    await action();
    await page.screenshot({ path: info.outputPath(`${phase}.png`), fullPage: true });
    await info.attach(`${phase}: ${description}`, {
      path: info.outputPath(`${phase}.png`),
      contentType: 'image/png',
    });
  });
}
async function login(page: Page, persona: string) {
  await page.goto('/');
  await page.evaluate(
    (value) => sessionStorage.setItem('kotorelay-token', `demo-${value}`),
    persona,
  );
  await page.reload();
  await expect(page.getByRole('navigation', { name: 'メインナビゲーション' })).toBeVisible();
}
async function api(
  request: APIRequestContext,
  persona: string,
  path: string,
  method = 'GET',
  data?: unknown,
) {
  const response = await request.fetch(`/api${path}`, {
    method,
    headers: { Authorization: `Bearer demo-${persona}`, 'Idempotency-Key': randomUUID() },
    data,
  });
  expect(response.ok(), await response.text()).toBeTruthy();
  return response.json();
}
async function fixture(request: APIRequestContext, title: string) {
  const me = await api(request, 'author', '/groups/me');
  const dept = me.departments[0].id as string;
  const doc = await api(request, 'author', '/documents', 'POST', { title, department_id: dept });
  await api(request, 'author', `/documents/${doc.id}/draft`, 'PUT', {
    title,
    body: `# 開発フロー\n\n${doc.id}\n\nレビューが完了したら、承認者がリリースを許可します。\n\n| 手順 | 担当 |\n| --- | --- |\n| 申請 | 執筆者 |\n| 承認 | 承認者 |`,
    revision: 1,
  });
  return { doc, dept };
}
async function publish(request: APIRequestContext, docId: string) {
  const draft = await api(request, 'author', `/documents/${docId}/draft`);
  const version = await api(request, 'author', `/documents/${docId}/submissions`, 'POST', {
    revision: draft.revision,
  });
  const reviews = await api(request, 'reviewer', '/reviews');
  const review = reviews.find(
    (r: { submission: { version_id: string } }) => r.submission.version_id === version.id,
  ).submission;
  await api(request, 'reviewer', `/reviews/${review.id}/decision`, 'POST', {
    decision: 'approved',
    manifest_hash: version.manifest_hash,
  });
  const jobs = await api(request, 'operator', '/operations/jobs');
  for (const job of jobs.filter(
    (j: { document_id: string; status: string }) =>
      j.document_id === docId && j.status === 'pending',
  ))
    await api(request, 'operator', `/operations/jobs/${job.id}`, 'POST');
  return version;
}
async function databaseEvidence(info: TestInfo, documentId: string) {
  if (!/^[0-9a-f-]{36}$/.test(documentId)) throw new Error('invalid fixture id');
  const sql = `SELECT json_build_object('document_id', d.id, 'status', d.status, 'latest_version_id', d.latest_version_id, 'version_count', (SELECT count(*) FROM versions v WHERE v.document_id=d.id), 'submission_count',(SELECT count(*) FROM submissions s WHERE s.document_id=d.id), 'ready_chunks',(SELECT count(*) FROM chunks c WHERE c.document_id=d.id AND c.ready)) FROM documents d WHERE d.id='${documentId}';`;
  const body = execFileSync(
    'docker',
    ['compose', 'exec', '-T', 'db', 'psql', '-U', 'kotorelay', '-d', 'kotorelay', '-At', '-c', sql],
    { encoding: 'utf8' },
  );
  await info.attach('DB状態（架空のE2E文書のみ）', { body, contentType: 'application/json' });
  return JSON.parse(body);
}

test('文書の執筆・保存・承認申請', async ({ page }, info) => {
  const title = `E2E執筆 ${Date.now()}`;
  await step(page, info, 'Given', '執筆者がワークスペースを開いている', async () => {
    await login(page, 'author');
    await page.getByRole('button', { name: '執筆ワークスペース', exact: true }).click();
    await page.getByRole('button', { name: '新しい文書' }).click();
  });
  await step(page, info, 'When', 'Markdownを保存してプレビューする', async () => {
    await page.getByLabel('文書タイトル').fill(title);
    await page.getByRole('button', { name: '作成して執筆する' }).click();
    await page.getByLabel('Markdown本文').fill('# 開発フロー\n\n申請後にレビューを行います。');
    await page.getByRole('button', { name: '保存', exact: true }).click();
    await expect(page.getByText('保存しました。')).toBeVisible();
    await expect(page.getByRole('heading', { name: '開発フロー', exact: true })).toBeVisible();
  });
  await step(page, info, 'Then', '保存された版を承認申請できる', async () => {
    await page.getByRole('button', { name: '承認申請', exact: true }).click();
    await expect(page.getByText('v1 を承認申請しました。')).toBeVisible();
  });
});

test('承認者がmanifestを確認して承認する', async ({ page, request }, info) => {
  const { doc } = await fixture(request, `E2E承認 ${Date.now()}`);
  await api(request, 'author', `/documents/${doc.id}/submissions`, 'POST', { revision: 2 });
  await step(page, info, 'Given', '対象版の承認申請が届いている', async () => {
    await login(page, 'reviewer');
    await page.getByRole('button', { name: '承認・レビュー', exact: true }).click();
    await expect(page.getByText(doc.title, { exact: true })).toBeVisible();
  });
  await step(page, info, 'When', '申請版の本文とmanifestを確認する', async () => {
    await page
      .locator('.review-row')
      .filter({ hasText: doc.title })
      .getByRole('button', { name: '内容を確認' })
      .click();
    await expect(page.getByText(/manifest:/)).toBeVisible();
    await expect(page.getByRole('heading', { name: '開発フロー' })).toBeVisible();
  });
  await step(page, info, 'Then', '承認済みとなり公開版が一つ確定する', async () => {
    await page.getByRole('button', { name: 'この版を承認' }).click();
    await expect(page.getByText(`${doc.title} を承認しました。`)).toBeVisible();
    const state = await databaseEvidence(info, doc.id);
    expect(state.version_count).toBe(1);
    expect(state.latest_version_id).not.toBeNull();
  });
});

test('根拠付きチャットと公開停止による履歴失効', async ({ page, request }, info) => {
  const { doc, dept } = await fixture(request, `E2Eチャット ${Date.now()}`);
  await publish(request, doc.id);
  await step(page, info, 'Given', '閲覧者に公開された承認版が検索できる', async () => {
    await login(page, 'reader');
    await page.getByRole('button', { name: 'ナレッジチャット', exact: true }).click();
  });
  await step(page, info, 'When', '開発フローについて質問する', async () => {
    await page
      .getByLabel('質問', { exact: true })
      .fill(doc.id);
    await page.getByRole('button', { name: '質問を送信' }).click();
    await expect(page.getByText('回答済み', { exact: true })).toBeVisible();
    await expect(page.getByText('参照した承認版')).toBeVisible();
  });
  await step(page, info, 'Then', '公開停止後に履歴を再取得すると古い回答を隠す', async () => {
    const docs = await api(request, 'leader', '/documents?scope=manage');
    for (const d of docs.filter(
      (d: { id: string; status: string; latest_version_id: string | null }) =>
        d.id === doc.id,
    ))
      await api(request, 'leader', `/documents/${d.id}/policy`, 'PUT', {
        revision: d.revision,
        visibility: 'department',
        shared_departments: [],
        status: 'withdrawn',
      });
    await page.getByRole('button', { name: '履歴を再確認' }).click();
    await expect(page.getByText('非表示', { exact: true })).toBeVisible();
    await expect(
      page.getByText('権限または公開版が変更されたため、この回答は表示できません。'),
    ).toBeVisible();
    const state = await databaseEvidence(info, doc.id);
    expect(state.status).toBe('withdrawn');
    expect(dept).toBeTruthy();
  });
});

test('他部署の直接URLと下書きアクセスを拒否する', async ({ page, request }, info) => {
  const { doc } = await fixture(request, `E2E非公開 ${Date.now()}`);
  await step(page, info, 'Given', '別部署の利用者としてログインしている', async () => {
    await login(page, 'other');
  });
  await step(page, info, 'When', '文書一覧で権限外のタイトルを検索する', async () => {
    await page.getByRole('textbox', { name: '文書を検索' }).fill(doc.title);
    await expect(page.getByText('一致する文書がありません')).toBeVisible();
  });
  await step(page, info, 'Then', '直接APIも404となり存在や本文を返さない', async () => {
    const result = await request.get(`/api/documents/${doc.id}/draft`, {
      headers: { Authorization: 'Bearer demo-other' },
    });
    expect(result.status()).toBe(404);
    expect(await result.text()).not.toContain(doc.title);
    await databaseEvidence(info, doc.id);
  });
});

test('保存競合でも編集中のMarkdownを失わない', async ({ page, request }, info) => {
  const { doc } = await fixture(request, `E2E競合 ${Date.now()}`);
  await step(page, info, 'Given', '執筆者が文書を編集している', async () => {
    await login(page, 'author');
    await page.getByRole('button', { name: '執筆ワークスペース', exact: true }).click();
    await page.getByRole('textbox', { name: '文書を検索' }).fill(doc.title);
    await page
      .getByRole('button')
      .filter({ has: page.getByRole('heading', { name: doc.title }) })
      .click();
    await page.getByLabel('Markdown本文').fill('この入力は失わない');
  });
  await step(page, info, 'When', '別の保存が先に確定した状態で保存する', async () => {
    await api(request, 'author', `/documents/${doc.id}/draft`, 'PUT', {
      title: doc.title,
      body: '先行保存',
      revision: 2,
    });
    await page.getByRole('button', { name: '保存', exact: true }).click();
    await expect(page.getByRole('alert')).toContainText('更新');
  });
  await step(page, info, 'Then', '競合を表示し入力を保持する', async () => {
    await expect(page.getByLabel('Markdown本文')).toHaveValue('この入力は失わない');
    await expect(page.getByText('未保存の変更があります。入力は保持されています。')).toBeVisible();
  });
});

test('モバイルでナビゲーションと文書を閲覧できる', async ({ page, request }, info) => {
  const { doc } = await fixture(request, `E2Eモバイル ${Date.now()}`);
  await publish(request, doc.id);
  await page.setViewportSize({ width: 390, height: 844 });
  await step(page, info, 'Given', 'スマートフォン幅でログインしている', async () => {
    await login(page, 'reader');
  });
  await step(page, info, 'When', '文書を検索して開く', async () => {
    await page.getByRole('textbox', { name: '文書を検索' }).fill(doc.title);
    await page
      .getByRole('button')
      .filter({ has: page.getByRole('heading', { name: doc.title }) })
      .click();
  });
  await step(page, info, 'Then', '本文と表が表示されページ全体は横にはみ出さない', async () => {
    await expect(page.getByRole('heading', { name: '開発フロー' })).toBeVisible();
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBe(true);
  });
});
