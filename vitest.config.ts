import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: {
    environment: 'jsdom',
    include: ['frontend/tests/**/*.test.{ts,tsx}'],
    setupFiles: ['frontend/tests/setup.ts'],
    reporters: ['default', 'json', 'junit'],
    outputFile: { json: 'artifacts/vitest.json', junit: 'artifacts/vitest.xml' },
    coverage: {
      provider: 'v8',
      include: ['frontend/src/**/*.{ts,tsx}'],
      reporter: ['json', 'json-summary', 'html', 'text'],
      reportsDirectory: 'artifacts/frontend-coverage',
      thresholds: { statements: 95, branches: 90, lines: 95 },
    },
  },
});
