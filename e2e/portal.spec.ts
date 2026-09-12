import { test, expect, type Page, type TestInfo } from '@playwright/test';

async function capture(page: Page, info: TestInfo, phase: string, text: string) {
  await test.step(`${phase}: ${text}`, async () => {
    const path = info.outputPath(`${phase}.png`);
    await page.screenshot({ path, fullPage: true });
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
