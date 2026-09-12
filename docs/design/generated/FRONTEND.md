<!-- 実装から生成。直接編集しない。入力SHA256: f4209c4ed7b292c6ed57aa300cf25000f8931a1f59b1fb43cfeb436b1d949dbe -->

# フロントエンド

Astroの単一ルート `/` がReactワークスペースを起動します。状態はReact hook、認証トークンはsessionStorage、APIは同一originの `/api` です。

| コンポーネント | 実装 |
| --- | --- |
| App | frontend/src/components/App.tsx |
| Login | frontend/src/components/App.tsx |
| Library | frontend/src/components/App.tsx |
| DocumentPanel | frontend/src/components/App.tsx |
| PlacedDocument | frontend/src/components/App.tsx |
| ProtectedImage | frontend/src/components/App.tsx |
| Images | frontend/src/components/App.tsx |
| Reviews | frontend/src/components/App.tsx |
| Chat | frontend/src/components/App.tsx |
| Groups | frontend/src/components/App.tsx |
| Operations | frontend/src/components/App.tsx |

## API呼出しと画面遷移

| 行 | 処理 |
| --- | --- |
| 65 | api<Identity>('/groups/me') |
| 86 | setSelected(null); |
| 92 | setSelected(null); |
| 105 | setSelected(null); |
| 123 | setSelected(null); |
| 179 | onBack={() => setSelected(null)} |
| 324 | api<Document[]>( |
| 340 | const doc = await api<Document>('/documents', 'POST', { title, department_id: dept }); |
| 514 | (edit ? api<Draft>(`/documents/${id}/draft`) : api<ReadDocument>(`/documents/${id}`)) |
| 531 | void api(`/metrics/views/${id}`, 'POST', { |
| 551 | setBusy(true); |
| 553 | const d = await api<Draft>(`/documents/${id}/draft`, 'PUT', { |
| 560 | setDirty(false); |
| 566 | setBusy(false); |
| 571 | setBusy(true); |
| 573 | const version = await api<Version>( |
| 583 | setBusy(false); |
| 596 | const result = await api<{ diff: string }>( |
| 665 | setDirty(true); |
| 678 | setDirty(true); |
| 713 | setDirty(true); |
| 845 | await api<Ocr>( |
| 867 | setBusy(true); |
| 871 | const result = await api<{ asset: { id: string }; ocr_run: { id: string }; ocr: Ocr }>( |
| 889 | setBusy(false); |
| 901 | const result = await api<{ ocr_run: { id: string } }>(`/images/${p.asset_id}/ocr`, 'POST', { |
| 1021 | api<Review[]>('/reviews') |
| 1032 | setSelected(item); |
| 1040 | setBusy(true); |
| 1049 | setSelected(null); |
| 1054 | setBusy(false); |
| 1074 | <button className="back" onClick={() => setSelected(null)}> |
| 1169 | setBusy(true); |
| 1171 | const answer = await api<Answer>( |
| 1183 | setBusy(false); |
| 1313 | api<Document[]>('/documents?scope=manage'), |
| 1314 | api<Metrics>( |
| 1317 | api<typeof members>(`/groups/${department}/members`), |
| 1520 | api<Job[]>('/operations/jobs') |

## 安全な表示

HTMLを無効化し、リンクschemeを検証します。画像は認証付きAPIからBlobとして表示し、破棄時にURLをrevokeします。文書読込完了まで入力を無効化し、競合時の入力を保持します。