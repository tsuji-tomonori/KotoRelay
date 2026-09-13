import { test, expect, type Page, type TestInfo } from '@playwright/test';

async function capture(page: Page, info: TestInfo, phase: string, text: string) {
  await test.step(`${phase}: ${text}`, async () => {
    const invalidCoordinates = await page
      .locator('figure svg')
      .evaluateAll((diagrams) =>
        diagrams.flatMap((diagram) =>
          [...diagram.querySelectorAll('*')].flatMap((node) =>
            [...node.attributes]
              .filter(
                (attribute) =>
                  [
                    'x',
                    'y',
                    'x1',
                    'x2',
                    'y1',
                    'y2',
                    'cx',
                    'cy',
                    'r',
                    'rx',
                    'ry',
                    'width',
                    'height',
                    'd',
                    'points',
                    'viewBox',
                    'transform',
                    'pathLength',
                  ].includes(attribute.name) && /NaN|undefined|Infinity/.test(attribute.value),
              )
              .map((attribute) => `${node.tagName}.${attribute.name}=${attribute.value}`),
          ),
        ),
      );
    expect(invalidCoordinates, '図の数値座標に不正値がない').toEqual([]);
    const path = info.outputPath(`${phase}.png`);
    await page.screenshot({ path, fullPage: false });
    await info.attach(`${phase}: ${text}`, { path, contentType: 'image/png' });
  });
}
test.beforeEach(async ({ page }, info) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: '概要', exact: true })).toBeVisible();
  await capture(page, info, 'Given', '同一runの品質データが読み込まれている');
});
test.afterEach(async ({ page }, info) => {
  await capture(page, info, 'Then', '検索・表示・認可された証跡の検証結果を確認する');
});

test('品質ポータルで日本語ケースと実測カバレッジを検索する', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: '概要', exact: true })).toBeVisible();
  await page
    .getByRole('navigation')
    .getByRole('button', { name: /単体テスト/ })
    .click();
  await page.getByRole('searchbox').fill('競合');
  await capture(page, test.info(), 'When', '日本語のケース名でテスト一覧を絞り込む');
  await expect(page.locator('.inventory button').first()).toBeVisible();
  await page
    .getByRole('navigation')
    .getByRole('button', { name: /カバレッジ/ })
    .click();
  await expect(page.locator('progress')).toBeVisible();
  await expect(page.locator('.coverage')).toContainText(' / ');
});

test('E2Eの各段階の画像を拡大しEscapeで元の位置へ戻る', async ({ page }) => {
  await page.goto('/');
  await page
    .getByRole('navigation')
    .getByRole('button', { name: /E2Eテスト/ })
    .click();
  for (const phase of ['Given', 'When', 'Then'])
    await expect(
      page.getByRole('button', { name: phase + 'のスクリーンショットを拡大' }),
    ).toBeVisible();
  const image = page.getByRole('button', { name: 'Whenのスクリーンショットを拡大' });
  await image.click();
  await capture(page, test.info(), 'When', 'When段階の画像を拡大する');
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).not.toBeVisible();
  await expect(image).toBeFocused();
  await page.locator('.inventory button').filter({ hasText: '承認者がmanifest' }).click();
  await expect(page.getByText('DB状態（架空のテスト文書のみ）')).toBeVisible();
});

test('生成設計の章と目次とMermaidを表示する', async ({ page }) => {
  await page.goto('/');
  await page
    .getByRole('navigation')
    .getByRole('button', { name: /設計書/ })
    .click();
  await page.getByRole('searchbox').fill('実装データモデル');
  await page.locator('.inventory button').first().click();
  await expect(page.getByText('この設計書の目次')).toBeVisible();
  await expect(page.locator('figure svg')).toBeVisible({ timeout: 45000 });
  await capture(page, test.info(), 'When', '設計書の目次とER図を描画する');
  await expect(page.getByRole('alert')).toHaveCount(0);
});

test('シーケンス図のSQL呼出しに日本語の役割説明を表示する', async ({ page }) => {
  await page
    .getByRole('navigation', { name: '品質ナビゲーション' })
    .getByRole('button', { name: /設計書/ })
    .click();
  await page.getByRole('searchbox').fill('ask_question');
  await page
    .locator('.inventory button')
    .filter({ hasText: /^最新承認版の根拠で回答 — シーケンス$/ })
    .click();
  const diagram = page.locator('figure svg');
  await expect(diagram).toBeVisible({ timeout: 45000 });
  await capture(page, test.info(), 'When', '回答APIのシーケンスを日本語のSQL役割説明で描画する');
  await expect(diagram).toContainText(
    '現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を取得する。',
  );
  await expect(diagram).not.toContainText('answers_get');
  const fontSize = await diagram
    .locator('.messageText')
    .first()
    .evaluate((element) => {
      const scale = (element as SVGGraphicsElement).getScreenCTM()?.a ?? 0;
      return Number.parseFloat(getComputedStyle(element).fontSize) * scale;
    });
  expect(fontSize).toBeGreaterThanOrEqual(12);
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await expect(page.getByRole('alert')).toHaveCount(0);
});

test('品質ポータルがモバイル幅で横にはみ出さない', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await expect(page.getByRole('heading', { name: '概要', exact: true })).toBeVisible();
  await page
    .getByRole('navigation')
    .getByRole('button', { name: /E2Eテスト/ })
    .click();
  await capture(page, test.info(), 'When', '390px幅でE2E結果を開く');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  );
});

test('設計をAPIグループとAPIと帳票の階層で開き検索後も現在位置を保つ', async ({ page }) => {
  await page
    .getByRole('navigation', { name: '品質ナビゲーション' })
    .getByRole('button', { name: /設計書/ })
    .click();
  const operation = page.locator('.inventory summary').filter({ hasText: /^save_draft$/ });
  await operation.click();
  await page
    .locator('.inventory button')
    .filter({ hasText: /^競合を検出して下書きを保存 — 詳細設計$/ })
    .click();
  await capture(page, test.info(), 'When', 'documentsからsave_draftの詳細設計を開く');
  const trail = page.getByRole('navigation', { name: '設計書の現在位置' });
  await expect(trail).toContainText('API');
  await expect(trail).toContainText('documents');
  await expect(trail).toContainText('save_draft');
  for (const title of [
    '1. 正常系入力',
    '2. 正常系前提',
    '3. 正常系リソース変更',
    '4. 正常系レスポンス',
  ])
    await expect(page.getByRole('heading', { name: title, exact: true })).toBeVisible();
  await page.getByRole('searchbox').fill('save_draft');
  await expect(page.locator('.inventory summary').filter({ hasText: /^documents$/ })).toBeVisible();
  await expect(trail).toContainText('save_draft');
  await page
    .locator('.inventory button')
    .filter({ hasText: /^競合を検出して下書きを保存 \(save_draft\)$/ })
    .click();
  await page.locator('.markdown').getByRole('link', { name: 'クエリ', exact: true }).click();
  await expect(page.getByRole('searchbox')).toHaveValue('');
  await expect(trail).toContainText('クエリ');
  const anchors = await page
    .locator('.toc a')
    .evaluateAll((links) => links.map((link) => link.getAttribute('href')));
  expect(new Set(anchors).size).toBe(anchors.length);

  await expect(
    page.locator('.markdown').getByRole('heading', { name: 'SQL種別', exact: true }).first(),
  ).toBeVisible();
});

test('CRUDの表と図とSQL根拠を表示しCSVをダウンロードする', async ({ page }) => {
  await page
    .getByRole('navigation', { name: '品質ナビゲーション' })
    .getByRole('button', { name: /設計書/ })
    .click();
  await page.getByRole('searchbox').fill('DB CRUD対応表');
  await page
    .locator('.inventory button')
    .filter({ hasText: /^DB CRUD対応表$/ })
    .click();
  await expect(page.locator('.markdown table').first()).toContainText('create_document');
  await expect(page.locator('figure svg').first()).toBeVisible({ timeout: 45000 });
  await capture(page, test.info(), 'When', 'APIとテーブルのCRUD対応とグループ別の図を開く');
  await expect(page.getByRole('heading', { name: '抽出根拠', exact: true })).toBeVisible();
  await page.getByRole('searchbox').fill('CRUD図と対応表');
  await page
    .locator('.inventory button')
    .filter({ hasText: /^CRUD図と対応表$/ })
    .click();
  const csv = page.locator('.markdown').getByRole('link', { name: 'CSV', exact: true }).first();
  const [download] = await Promise.all([page.waitForEvent('download'), csv.click()]);
  expect(download.suggestedFilename()).toBe('db.csv');
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test('APIごとのファイル責務と所有SQLを生成設計で確認する', async ({ page }) => {
  await page
    .getByRole('navigation', { name: '品質ナビゲーション' })
    .getByRole('button', { name: /設計書/ })
    .click();
  await page.getByRole('searchbox').fill('APIごとのファイルと責務');
  await page
    .locator('.inventory button')
    .filter({ hasText: /^APIごとのファイルと責務$/ })
    .click();
  const source = page
    .locator('.markdown')
    .getByText('backend/src/kotorelay/operations/documents/create_document', { exact: true });
  await source.scrollIntoViewIfNeeded();
  await expect(source).toBeVisible();
  for (const name of [
    'router.py',
    'functions.py',
    'schemas.py',
    'response_builders.py',
    'contract.py',
    'samples.py',
  ])
    await expect(page.locator('.markdown table').nth(1)).toContainText(name);
  await capture(page, test.info(), 'When', '文書作成APIの所有先とファイルごとの責務を確認する');
  await page.getByRole('searchbox').fill('create_document');
  await page
    .locator('.inventory button')
    .filter({ hasText: /^文書を作成 — クエリ$/ })
    .click();
  await expect(
    page.locator('.markdown').getByRole('heading', {
      name: 'documents/create_document/001_documents_insert.sql',
      exact: true,
    }),
  ).toBeVisible();
  await expect(page.locator('.markdown')).toContainText(
    'backend/src/kotorelay/operations/documents/create_document/sql/001_documents_insert.sql',
  );
  await expect(page.locator('.markdown')).toContainText('DocumentsInsertParams');
  await expect(page.locator('.markdown')).toContainText('params.latest_version_id');
  await expect(page.locator('.markdown')).toContainText('str | None');
});

test('routerの文書作成順をSQLの役割ラベルで確認し長い図をスクロールする', async ({ page }) => {
  await page
    .getByRole('navigation', { name: '品質ナビゲーション' })
    .getByRole('button', { name: /設計書/ })
    .click();
  await page.getByRole('searchbox').fill('create_document');
  await page
    .locator('.inventory button')
    .filter({ hasText: /^文書を作成 — シーケンス$/ })
    .click();
  const diagram = page.getByRole('region', { name: '設計図' });
  await expect(diagram.locator('svg')).toBeVisible({ timeout: 45000 });
  const roles = await diagram
    .locator('text.messageText')
    .evaluateAll((nodes) => nodes.map((node) => node.textContent ?? ''));
  const document = roles.findIndex((text) =>
    text.includes('現在の組織の文書を、所有部署・公開範囲・状態を指定して登録する。'),
  );
  const draft = roles.findIndex((text) =>
    text.includes(
      '現在の組織の文書の下書きを、本文の保存先・画像配置・改訂番号を指定して登録する。',
    ),
  );
  expect(document).toBeGreaterThanOrEqual(0);
  expect(draft).toBeGreaterThan(document);
  expect(await diagram.evaluate((node) => node.scrollHeight > node.clientHeight)).toBe(true);
  await diagram.evaluate((node) => {
    node.scrollTop = node.scrollHeight;
  });
  await capture(
    page,
    test.info(),
    'When',
    '実装順のSQL説明と確定までのフローを図の内部スクロールで確認する',
  );
  await expect(page.getByRole('alert')).toHaveCount(0);
});

test('例外応答と型付きログを日本語のテスト手順から照合できる', async ({ page }) => {
  await page
    .getByRole('navigation', { name: '品質ナビゲーション' })
    .getByRole('button', { name: /設計書/ })
    .click();
  await page.getByRole('searchbox').fill('save_draft');
  await page
    .locator('.inventory button')
    .filter({ hasText: /— シーケンス$/ })
    .click();
  const diagram = page.getByRole('region', { name: '設計図' });
  await expect(diagram.locator('svg')).toBeVisible({ timeout: 45000 });
  await expect(diagram).toContainText('HTTP 409');
  await expect(diagram).toContainText('他の操作で更新されました。');
  await expect(diagram).toContainText('KR_HTTP_REJECTED');
  await expect(diagram).not.toContainText('例外を送出し通常経路を終了');
  await page
    .locator('.inventory button')
    .filter({ hasText: /— ログメッセージ$/ })
    .click();
  await expect(page.locator('.markdown')).toContainText('RequestValidationError');
  await expect(page.locator('.markdown')).toContainText('復旧手順');
  await expect(page.locator('.markdown')).toContainText('他の操作で更新されました。');
  await page
    .getByRole('heading', { name: '例外からHTTPエラー応答への対応', exact: true })
    .scrollIntoViewIfNeeded();
  await capture(page, test.info(), 'When', '例外のHTTP応答とログのメッセージ・復旧手順を照合する');
  await page
    .locator('.inventory button')
    .filter({ hasText: /— 単体テスト詳細$/ })
    .click();
  await expect(page.locator('.markdown')).toContainText('保存番号2の下書きがある。');
  await expect(page.locator('.markdown')).toContainText('古い保存番号1');
  await expect(page.locator('.markdown')).not.toContainText('result.status_code == 409');
  await page
    .getByRole('navigation', { name: '品質ナビゲーション' })
    .getByRole('button', { name: /単体テスト/ })
    .click();
  await page.getByRole('searchbox').fill('競合保存は先行内容を上書きしない');
  await page.locator('.inventory button').first().click();
  await expect(page.locator('.test-narrative')).toContainText('Given — 前提');
  await expect(page.locator('.test-narrative')).toContainText(
    '409を返し、先に保存した本文を上書きしない。',
  );
});
