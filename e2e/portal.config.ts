import { defineConfig, devices } from '@playwright/test';
import { fileURLToPath } from 'node:url';
export default defineConfig({
  testDir: '.',
  testMatch: 'portal.spec.ts',
  workers: 1,
  retries: 0,
  timeout: 60000,
  outputDir: '../artifacts/portal-tests',
  reporter: [['list'], ['json', { outputFile: '../artifacts/portal-playwright.json' }]],
  use: {
    baseURL: 'http://localhost:4173',
    screenshot: 'only-on-failure',
    ...devices['Desktop Chrome'],
  },
  webServer: {
    command: 'python3 -m http.server 4173 --directory artifacts/site',
    cwd: fileURLToPath(new URL('..', import.meta.url)),
    url: 'http://localhost:4173',
    reuseExistingServer: !process.env.CI,
  },
});
