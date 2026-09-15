/** 収録コードとCI定義から収録設計を生成し、差分を検査する。 */
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
const script = await readFile('tools/video/capture-intro.mjs', 'utf8');
const workflow = await readFile('.github/workflows/intro-capture.yml', 'utf8');
const actors = [...script.matchAll(/await actor\('([^']+)', '([^']+)'\)/g)];
const marks = [...script.matchAll(/await (author|reviewer|reader)\.mark\('([^']+)'\)/g)];
const output = 'docs/design/generated/INTRO-CAPTURE.md';
const text = [
  '# 導入動画用の実画面収録設計', '',
  '<!-- tools/video/design.mjs が実装から生成。直接編集しない。 -->', '',
  '動画制作向けの独立した収録ツール。製品の要件・API・データモデルを変更しない。', '',
  '## 入力と実行環境', '',
  '- 既存のDocker Composeで起動したフロントエンド・API・PostgreSQL。',
  '- 実APIで準備した架空文書と、既存のローカルサンプル利用者。',
  '- 画面はPlaywrightの実ブラウザー操作で録画し、DOMの改変・通信のモックは行わない。',
  '- ローカル回答は承認済み文書の抜粋。AWSのLLM回答を実行したとは扱わない。', '',
  '## 収録順序', '', '| 録画名 | 役割 | 操作区間 |', '| --- | --- | --- |',
  ...actors.map(([,name,role]) => `| ${name} | ${role} | ${marks.filter((m)=>m[1]===name).map((m)=>m[2]).join(' → ')} |`), '',
  '## 出力と検証', '',
  '- artifacts/intro-capture/: WebM、各操作後のPNG、時間位置を記録したJSON、診断ログ。',
  '- 保存・申請・承認の成功、回答本文と引用元、検索反映済み表示をPlaywrightで検査。',
  '- PRで専用ワークフローを実行し、成果物を14日間保持。公開・デプロイは行わない。',
  '- node tools/video/design.mjs --check で本設計の欠落・差分を検査する。', '',
  '## 実装の識別', '',
  `- 収録コード SHA-256: ${createHash('sha256').update(script).digest('hex')}`,
  `- CI定義 SHA-256: ${createHash('sha256').update(workflow).digest('hex')}`, '',
].join('\n');
if (process.argv.includes('--stdout')) {
  process.stdout.write(text);
} else if (process.argv.includes('--check')) {
  if (await readFile(output, 'utf8').catch(()=>null) !== text) throw new Error('収録設計が欠落または変更されています。node tools/video/design.mjs を実行してください。');
} else await writeFile(output, text);
