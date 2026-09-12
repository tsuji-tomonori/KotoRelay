import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
const html = readFileSync('frontend/dist/index.html', 'utf8');
const hashes = [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)]
  .filter((match) => !/(?:^|\s)src\s*=/.test(match[1]))
  .map((match) => `'sha256-${createHash('sha256').update(match[2]).digest('base64')}'`);
const config = readFileSync('frontend/nginx.conf', 'utf8').replace(
  "script-src 'self'",
  `script-src 'self' ${[...new Set(hashes)].join(' ')}`,
);
mkdirSync('artifacts', { recursive: true });
writeFileSync('artifacts/nginx.conf', config);
