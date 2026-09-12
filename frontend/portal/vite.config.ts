import { defineConfig } from 'vite';
export default defineConfig({
  root: 'frontend/portal',
  base: './',
  publicDir: '../../artifacts/portal-public',
  build: { outDir: '../../artifacts/site', emptyOutDir: true },
  esbuild: { jsx: 'automatic' },
});
