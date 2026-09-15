# 導入動画用の実画面収録設計

<!-- tools/video/design.mjs が実装から生成。直接編集しない。 -->

動画制作向けの独立した収録ツール。製品の要件・API・データモデルを変更しない。

## 入力と実行環境

- 既存のDocker Composeで起動したフロントエンド・API・PostgreSQL。
- 実APIで準備した架空文書と、既存のローカルサンプル利用者。
- 画面はPlaywrightの実ブラウザー操作で録画し、DOMの改変・通信のモックは行わない。
- ローカル回答は承認済み文書の抜粋。AWSのLLM回答を実行したとは扱わない。

## 収録順序

| 録画名 | 役割 | 操作区間 |
| --- | --- | --- |
| author | author | create → write → submit |
| reviewer | reviewer | review |
| reader | reader | library → chat → answer → citation |

## 出力と検証

- artifacts/intro-capture/: WebM、各操作後のPNG、時間位置を記録したJSON、診断ログ。
- 保存・申請・承認の成功、回答本文と引用元、検索反映済み表示をPlaywrightで検査。
- PRで専用ワークフローを実行し、成果物を14日間保持。公開・デプロイは行わない。
- node tools/video/design.mjs --check で本設計の欠落・差分を検査する。

## 実装の識別

- 収録コード SHA-256: 7b932e98049215ea8ed0c5a7d4aa5bfc50160733c509dbfe307230348918cce0
- CI定義 SHA-256: d8b4e6d332493a0e920978e9b350cbd8c5833244e92c1c70b29d1a151264b4a0
