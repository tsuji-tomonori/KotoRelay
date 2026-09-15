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
    // 読み込み後に一覧が伸びても、操作中の画面を等倍で残す。
    await page.screenshot({ path: info.outputPath(`${phase}.png`), fullPage: false });
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
  await expect(page.getByRole('button', { name: 'ログアウト' })).toBeVisible();
  if (await page.getByRole('button', { name: 'メニュー' }).isVisible())
    await page.getByRole('button', { name: 'メニュー' }).click();
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
    await page.getByRole('button', { name: '執筆', exact: true }).click();
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
    await expect(page.getByText(/第1版を承認申請しました/)).toBeVisible();
  });
});

test('承認者がmanifestを確認して承認する', async ({ page, request }, info) => {
  const { doc } = await fixture(request, `E2E承認 ${Date.now()}`);
  await api(request, 'author', `/documents/${doc.id}/submissions`, 'POST', { revision: 2 });
  await step(page, info, 'Given', '対象版の承認申請が届いている', async () => {
    await login(page, 'reviewer');
    await page.getByRole('button', { name: '審査', exact: true }).click();
    await expect(page.locator('.review-row').filter({ hasText: doc.title })).toBeVisible();
  });
  await step(page, info, 'When', '申請版の本文とmanifestを確認する', async () => {
    await page
      .locator('.review-row')
      .filter({ hasText: doc.title })
      .getByRole('button', { name: '内容を確認' })
      .click();
    await page.getByText('審査対象の識別情報').click();
    await expect(page.getByText(/manifest:/)).toBeVisible();
    await expect(page.getByRole('heading', { name: '開発フロー' })).toBeVisible();
  });
  await step(page, info, 'Then', '承認済みとなり公開版が一つ確定する', async () => {
    await page.getByRole('button', { name: 'この版を承認' }).click();
    await page.getByRole('button', { name: '承認する', exact: true }).click();
    await expect(page.getByText(/第1版を承認しました/)).toBeVisible();
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
    await page.getByRole('button', { name: 'RAGチャット', exact: true }).click();
  });
  await step(page, info, 'When', '開発フローについて質問する', async () => {
    await page.getByLabel('質問', { exact: true }).fill(doc.id);
    await page.getByRole('button', { name: '質問を送信' }).click();
    await expect(page.getByText('回答済み', { exact: true })).toBeVisible();
    await expect(page.getByText('参照した承認版')).toBeVisible();
  });
  await step(page, info, 'Then', '公開停止後に履歴を再取得すると古い回答を隠す', async () => {
    const docs = await api(request, 'leader', '/documents?scope=manage');
    for (const d of docs.filter(
      (d: { id: string; status: string; latest_version_id: string | null }) => d.id === doc.id,
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
    await page.getByRole('searchbox', { name: '文書を検索' }).fill(doc.title);
    await page.getByRole('button', { name: '検索する' }).click();
    await expect(page.getByText('条件に一致する文書はありません')).toBeVisible();
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
    await page.getByRole('button', { name: '執筆', exact: true }).click();
    await page.getByRole('searchbox', { name: '文書を検索' }).fill(doc.title);
    await page.getByRole('button', { name: '検索する' }).click();
    await page.getByRole('link', { name: doc.title, exact: true }).click();
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
    await page.getByRole('searchbox', { name: '文書を検索' }).fill(doc.title);
    await page.getByRole('button', { name: '検索する' }).click();
    await page.getByRole('link', { name: doc.title, exact: true }).click();
  });
  await step(page, info, 'Then', '本文と表が表示されページ全体は横にはみ出さない', async () => {
    await expect(page.getByRole('heading', { name: '開発フロー' })).toBeVisible();
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBe(true);
  });
});

test('添付画像をOCRで読み取り確認した版を申請する', async ({ page, request }, info) => {
  await page.setContent(
    '<article style="width:700px;padding:40px;background:white;color:black;font:48px sans-serif"><h1>RELEASE GUIDE</h1><p>承認後に開発を開始</p></article>',
  );
  const png = await page.locator('article').screenshot();
  const title = `E2E画像 ${Date.now()}`;
  const { doc } = await fixture(request, title);
  await step(page, info, 'Given', '執筆中の文書と読み取る画像を用意する', async () => {
    await login(page, 'author');
    await page.getByRole('button', { name: '執筆', exact: true }).click();
    await page.getByLabel('文書を検索').fill(title);
    await page.getByRole('button', { name: '検索する' }).click();
    await page.getByRole('link', { name: title, exact: true }).click();
    await expect(page.getByLabel('Markdown本文')).toBeEnabled();
  });
  await step(
    page,
    info,
    'When',
    '実際のTesseract OCRで画像を読み取り文字と位置を確認する',
    async () => {
      await page
        .getByLabel('画像を添付')
        .setInputFiles({ name: 'release.png', mimeType: 'image/png', buffer: png });
      // 初回OCRは5秒を超えるため、結果の内容を既定の30秒枠で待つ。
      await expect(page.getByLabel('図1・領域1の文字')).toHaveValue(/RELEASE/, { timeout: 30000 });
      await expect(page.getByLabel('図1・領域1の文字')).toBeVisible();
      await page.getByLabel('図1の代替テキスト').fill('承認後に開発を開始するリリース手順');
      await page.getByRole('button', { name: 'OCRを確認して確定' }).click();
      await expect(page.getByText('OCRを確認しました。文書を保存してください。')).toBeVisible();
      await page.getByRole('button', { name: '保存', exact: true }).click();
      await expect(page.getByText('保存しました。')).toBeVisible();
    },
  );
  await step(page, info, 'Then', '本文・画像・OCRを同じ承認対象として固定する', async () => {
    await page.getByRole('button', { name: '承認申請', exact: true }).click();
    await expect(page.getByText(/第1版を承認申請しました/)).toBeVisible();
    const state = await databaseEvidence(info, doc.id);
    expect(state.submission_count).toBe(1);
  });
});

for (const width of [320, 390, 768, 1440]) {
  test(`${width}pxで文字・フォーカス・メニュー・ログアウトを維持する`, async ({ page }, info) => {
    await page.setViewportSize({ width, height: 960 });
    await step(page, info, 'Given', `${width}px幅で閲覧者がログインしている`, async () => {
      await login(page, 'reader');
    });
    await step(page, info, 'When', 'キーボードでメニューからチャットへ進む', async () => {
      const chat = page.getByRole('button', { name: 'RAGチャット', exact: true });
      await chat.focus();
      await page.keyboard.press('Enter');
      await expect(page.getByRole('heading', { name: 'RAGチャット', exact: true })).toBeFocused();
      const question = page.getByLabel('質問', { exact: true });
      await question.focus();
      const fonts = await question.evaluate((e) => ({
        size: parseFloat(getComputedStyle(e).fontSize),
        outline: getComputedStyle(e).outlineStyle,
      }));
      expect(fonts.size).toBeGreaterThanOrEqual(16);
      expect(fonts.outline).not.toBe('none');
      if (width === 320)
        await page.evaluate(() => {
          document.documentElement.style.fontSize = '200%';
        });
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
        true,
      );
    });
    await step(page, info, 'Then', '画面幅や文字拡大でもログアウトに到達する', async () => {
      await page.getByRole('button', { name: 'ログアウト' }).focus();
      await page.keyboard.press('Enter');
      await expect(page.getByRole('button', { name: 'ローカルで始める' })).toBeVisible();
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
        true,
      );
    });
  });
}

test('未保存のナビ移動をキーボードで取り消して入力へ戻る', async ({ page, request }, info) => {
  const { doc } = await fixture(request, `E2E離脱保護 ${Date.now()}`);
  await step(page, info, 'Given', '執筆中の本文に未保存の変更がある', async () => {
    await login(page, 'author');
    await page.getByRole('button', { name: '執筆', exact: true }).click();
    await page.getByLabel('文書を検索').fill(doc.title);
    await page.getByRole('button', { name: '検索する' }).click();
    await page.getByRole('link', { name: doc.title }).click();
    await page.getByLabel('Markdown本文').fill('この入力を保持します');
  });
  await step(page, info, 'When', '別画面への移動を試みて確認内容を読む', async () => {
    await page.getByRole('button', { name: 'RAGチャット' }).focus();
    await page.keyboard.press('Enter');
    await expect(page.getByRole('dialog')).toContainText('未保存の変更');
    await expect(page.getByRole('button', { name: 'キャンセル' })).toBeFocused();
  });
  await step(page, info, 'Then', 'Escapeで編集を続けてフォーカスと本文を維持する', async () => {
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).not.toBeVisible();
    await expect(page.getByRole('button', { name: 'RAGチャット' })).toBeFocused();
    await expect(page.getByLabel('Markdown本文')).toHaveValue('この入力を保持します');
    const stored = await api(request, 'author', `/documents/${doc.id}/draft`);
    expect(stored.body).not.toBe('この入力を保持します');
    await databaseEvidence(info, doc.id);
  });
});

test('公開設定を確認して保存し削除理由を監査へ記録する', async ({ page, request }, info) => {
  const { doc } = await fixture(request, `E2E公開管理 ${Date.now()}`);
  await publish(request, doc.id);
  await step(page, info, 'Given', '管理部署の文書を選び変更前の状態を確認する', async () => {
    await login(page, 'leader');
    await page.getByRole('button', { name: '部署管理', exact: true }).click();
    await page.getByRole('button', { name: new RegExp(`管理.*${doc.title}`) }).click();
    await page
      .getByRole('combobox', { name: '公開範囲', exact: true })
      .selectOption('organization');
    const read = await api(request, 'reader', `/documents/${doc.id}`);
    expect(read.document.visibility).toBe('department');
  });
  await step(page, info, 'When', '公開先の変更前後を確認して保存する', async () => {
    await page.getByRole('button', { name: '変更内容を確認' }).click();
    await expect(page.getByRole('dialog')).toContainText('開発部');
    await expect(page.getByRole('dialog')).toContainText('組織内に公開');
    await page.getByRole('button', { name: '保存する', exact: true }).click();
    await expect(page.getByRole('heading', { name: `${doc.title} の公開設定` })).not.toBeVisible();
    const read = await api(request, 'reader', `/documents/${doc.id}`);
    expect(read.document.visibility).toBe('organization');
    await page.getByRole('button', { name: new RegExp(`管理.*${doc.title}`) }).click();
    await expect(page.getByRole('button', { name: '削除内容を確認' })).toBeDisabled();
    await page.getByLabel('削除理由（必須）').fill('検証文書の利用終了');
    await page.getByRole('button', { name: '削除内容を確認' }).click();
  });
  await step(page, info, 'Then', '削除を確定し監査記録と配信停止が一致する', async () => {
    await page.getByRole('button', { name: '削除する', exact: true }).click();
    await expect(page.getByRole('heading', { name: `${doc.title} の公開設定` })).not.toBeVisible();
    const state = await databaseEvidence(info, doc.id);
    expect(state.status).toBe('deleted');
    const sql = `SELECT json_build_object('document_id',document_id,'action',action,'reason',reason,'after_state',after_state) FROM audit WHERE document_id='${doc.id}' AND action='policy' AND after_state='deleted';`;
    const body = execFileSync(
      'docker',
      [
        'compose',
        'exec',
        '-T',
        'db',
        'psql',
        '-U',
        'kotorelay',
        '-d',
        'kotorelay',
        '-At',
        '-c',
        sql,
      ],
      { encoding: 'utf8' },
    );
    const audit = JSON.parse(body);
    expect(audit.reason).toBe('検証文書の利用終了');
    await info.attach('DB状態（削除理由の架空監査記録）', {
      body,
      contentType: 'application/json',
    });
  });
});

test('引用元更新を説明し旧版や新版本文を無断で引用表示しない', async ({ page, request }, info) => {
  const { doc } = await fixture(request, `E2E引用版 ${Date.now()}`);
  await publish(request, doc.id);
  await step(page, info, 'Given', '閲覧者が承認版を根拠にした回答を得る', async () => {
    await login(page, 'reader');
    await page.getByRole('button', { name: 'RAGチャット' }).click();
    await page.getByLabel('質問', { exact: true }).fill(doc.id);
    await page.getByRole('button', { name: '質問を送信' }).click();
    await expect(page.getByText('参照した承認版')).toBeVisible();
  });
  await step(page, info, 'When', '新版が承認された後に当時の引用を開く', async () => {
    const draft = await api(request, 'author', `/documents/${doc.id}/draft`);
    await api(request, 'author', `/documents/${doc.id}/draft`, 'PUT', {
      title: doc.title,
      body: '# 新しい公開本文\n\n新たな手順だけを記載します。',
      revision: draft.revision,
    });
    await publish(request, doc.id);
    await page.locator('.citations').getByRole('button').filter({ hasText: doc.title }).click();
    await expect(page.getByRole('heading', { name: '引用元が更新されています' })).toBeVisible();
    await expect(page.getByText('新たな手順だけを記載します。')).not.toBeVisible();
  });
  await step(page, info, 'Then', '明示的に最新版を開き元の会話にも戻れる', async () => {
    await page.getByRole('button', { name: '最新の承認版を開く' }).click();
    await expect(page.getByRole('heading', { name: '新しい公開本文' })).toBeVisible();
    await page.getByRole('button', { name: '文書一覧へ' }).click();
    await expect(page.getByText('参照した承認版')).toBeVisible();
    await databaseEvidence(info, doc.id);
  });
});

test('絵文字と本文内画像2枚をプレビュー・審査・閲覧で同じ位置に表示する', async ({
  page,
  request,
}, info) => {
  const { doc } = await fixture(request, `E2E同一版描画 ${Date.now()}`);
  await page.setContent(
    '<div style="width:200px;height:100px;background:#eaf4ee;color:#176851;font:32px sans-serif">手順の図</div>',
  );
  const png = await page.locator('div').screenshot();
  const body = '日😀\n\n# 手順\n\n前半の説明\n\n# 手順\n\n後半の説明\n';
  const placements = [];
  for (let i = 0; i < 2; i++) {
    const upload = await request.post(`/api/images/documents/${doc.id}`, {
      headers: { Authorization: 'Bearer demo-author' },
      multipart: { file: { name: 'figure.png', mimeType: 'image/png', buffer: png } },
    });
    expect(upload.ok()).toBeTruthy();
    const value = await upload.json();
    const corrected = await api(request, 'author', `/images/${value.asset.id}/ocr`, 'POST', {
      confirmed: true,
      regions: [],
    });
    placements.push({
      id: randomUUID(),
      asset_id: value.asset.id,
      ocr_run_id: corrected.ocr_run.id,
      offset: i === 0 ? 2 : Array.from('日😀\n\n# 手順\n\n前半の説明\n\n').length,
      heading: '手順',
      alt_text: `手順${i + 1}の説明図`,
      caption: `手順${i + 1}の図`,
    });
  }
  await api(request, 'author', `/documents/${doc.id}/draft`, 'PUT', {
    title: doc.title,
    body,
    revision: 2,
    placements,
  });
  async function order(selector: string) {
    const rendered = page.locator(selector);
    await expect(rendered.locator('img')).toHaveCount(2);
    await expect(rendered.locator('img').first()).toBeVisible();
    return rendered.locator('.document-part').evaluateAll((parts) =>
      parts.map((part) => ({
        text: part.querySelector('.markdown')?.textContent,
        alt: part.querySelector('img')?.alt ?? null,
      })),
    );
  }
  let expected: { text: string | null | undefined; alt: string | null }[] = [];
  await step(page, info, 'Given', '保存した下書きで画像2枚の位置と絵文字を確認する', async () => {
    await login(page, 'author');
    await page.getByRole('button', { name: '執筆', exact: true }).click();
    await page.getByLabel('文書を検索').fill(doc.title);
    await page.getByRole('button', { name: '検索する' }).click();
    await page.getByRole('link', { name: doc.title }).click();
    await expect(page.getByLabel('Markdown本文')).toHaveValue(body);
    expected = await order('.preview .placed-document');
    expect(expected[0]!.text).toBe('日😀');
  });
  await step(page, info, 'When', '申請した固定版を審査者が同じレンダラーで確認する', async () => {
    await page.getByRole('button', { name: '承認申請', exact: true }).click();
    await expect(page.getByText(/第1版を承認申請しました/)).toBeVisible();
    await login(page, 'reviewer');
    await page.getByRole('button', { name: '審査', exact: true }).click();
    await page
      .locator('.review-row')
      .filter({ hasText: doc.title })
      .getByRole('button', { name: '内容を確認' })
      .click();
    expect(await order('.placed-document')).toEqual(expected);
    const links = page
      .getByRole('navigation', { name: '文書の目次' })
      .getByRole('link', { name: '手順', exact: true });
    expect(await links.nth(0).getAttribute('href')).not.toBe(
      await links.nth(1).getAttribute('href'),
    );
  });
  await step(page, info, 'Then', '承認後の閲覧も本文と画像の順序が一致する', async () => {
    await page.getByRole('button', { name: 'この版を承認' }).click();
    await page.getByRole('button', { name: '承認する', exact: true }).click();
    await expect(page.getByText(/第1版を承認しました/)).toBeVisible();
    await login(page, 'reader');
    await page.getByLabel('文書を検索').fill(doc.title);
    await page.getByRole('button', { name: '検索する' }).click();
    await page.getByRole('link', { name: doc.title }).click();
    expect(await order('.article .placed-document')).toEqual(expected);
    await databaseEvidence(info, doc.id);
  });
});
