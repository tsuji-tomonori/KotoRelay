<!-- 実装から生成。直接編集しない。入力SHA256: 7ce322b2bb5c68dab4c51499ae55d5e49bae34d22b47e21dd6264975362b5d49 -->

# フロントエンド

Astroの単一ルート `/` がReactワークスペースを起動します。TypeScript構文木から全TS/TSXのコンポーネント・呼出し・操作イベントを列挙します。

| コンポーネント | 実装 | 行 |
| --- | --- | --- |
| App | frontend/src/components/App.tsx | 37 |
| Markdown | frontend/src/components/Markdown.tsx | 33 |
| Login | frontend/src/components/layout/Login.tsx | 4 |
| ConfirmDialog | frontend/src/components/ui/ConfirmDialog.tsx | 3 |
| Chat | frontend/src/features/chat/Chat.tsx | 13 |
| DocumentPanel | frontend/src/features/documents/DocumentPanel.tsx | 19 |
| Library | frontend/src/features/documents/Library.tsx | 14 |
| PlacedDocument | frontend/src/features/documents/PlacedDocument.tsx | 46 |
| Groups | frontend/src/features/groups/Groups.tsx | 16 |
| PolicyEditor | frontend/src/features/groups/Groups.tsx | 309 |
| Images | frontend/src/features/images/Images.tsx | 6 |
| ImageEditor | frontend/src/features/images/Images.tsx | 124 |
| ProtectedImage | frontend/src/features/images/ProtectedImage.tsx | 3 |
| Operations | frontend/src/features/operations/Operations.tsx | 3 |
| Reviews | frontend/src/features/reviews/Reviews.tsx | 15 |

## API呼出しと状態遷移

| 実装 | 行 | 処理 |
| --- | --- | --- |
| frontend/src/components/App.tsx | 53 | setPending(() => action) |
| frontend/src/components/App.tsx | 60 | api<Identity>('/groups/me') |
| frontend/src/components/App.tsx | 63 | setIdentity(value) |
| frontend/src/components/App.tsx | 64 | setDepartment(value.departments[0]?.id ?? '') |
| frontend/src/components/App.tsx | 65 | setError('') |
| frontend/src/components/App.tsx | 70 | setError(String(e)) |
| frontend/src/components/App.tsx | 71 | setIdentity(null) |
| frontend/src/components/App.tsx | 88 | setScreen(next) |
| frontend/src/components/App.tsx | 89 | setSelected(null) |
| frontend/src/components/App.tsx | 90 | setError('') |
| frontend/src/components/App.tsx | 91 | setMenu(false) |
| frontend/src/components/App.tsx | 97 | setToken('') |
| frontend/src/components/App.tsx | 98 | setIdentity(null) |
| frontend/src/components/App.tsx | 99 | setSelected(null) |
| frontend/src/components/App.tsx | 100 | setScreen('library') |
| frontend/src/components/App.tsx | 105 | setSelected({ id, citation }) |
| frontend/src/components/App.tsx | 106 | setError('') |
| frontend/src/components/App.tsx | 116 | setIdentity(null) |
| frontend/src/components/App.tsx | 117 | setToken(value) |
| frontend/src/components/App.tsx | 118 | setSelected(null) |
| frontend/src/components/App.tsx | 161 | setMenu(!menu) |
| frontend/src/components/App.tsx | 172 | setDepartment(value) |
| frontend/src/components/App.tsx | 215 | setError('') |
| frontend/src/components/App.tsx | 228 | setSelected(null) |
| frontend/src/components/App.tsx | 269 | setPending(null) |
| frontend/src/components/App.tsx | 273 | setPending(null) |
| frontend/src/components/layout/Login.tsx | 53 | setPersona(e.target.value) |
| frontend/src/components/layout/Login.tsx | 76 | setAccessToken(e.target.value) |
| frontend/src/features/chat/Chat.tsx | 36 | setBusy(true) |
| frontend/src/features/chat/Chat.tsx | 38 | api<Answer>(<br>        '/chat',<br>        'POST',<br>        { question, department_id: department, conversation_id: conversation },<br>        crypto.randomUUID(),<br>      ) |
| frontend/src/features/chat/Chat.tsx | 44 | setConversation(answer.conversation_id) |
| frontend/src/features/chat/Chat.tsx | 45 | setAnswers([...answers, answer]) |
| frontend/src/features/chat/Chat.tsx | 46 | setQuestion('') |
| frontend/src/features/chat/Chat.tsx | 47 | setNotice(<br>        answer.status === 'answered'<br>          ? '回答を受け取りました。'<br>          : '確認できる文書からは回答できませんでした。質問を具体化してください。',<br>      ) |
| frontend/src/features/chat/Chat.tsx | 55 | setBusy(false) |
| frontend/src/features/chat/Chat.tsx | 61 | setAnswers(await api(`/chat/${conversation}`)) |
| frontend/src/features/chat/Chat.tsx | 61 | api(`/chat/${conversation}`) |
| frontend/src/features/chat/Chat.tsx | 63 | setAnswers([]) |
| frontend/src/features/chat/Chat.tsx | 144 | setDepartment(e.target.value) |
| frontend/src/features/chat/Chat.tsx | 145 | setConversation(null) |
| frontend/src/features/chat/Chat.tsx | 146 | setAnswers([]) |
| frontend/src/features/chat/Chat.tsx | 147 | setNotice('利用部署を変更し、新しい会話を開始しました。') |
| frontend/src/features/chat/Chat.tsx | 166 | setQuestion(e.target.value) |
| frontend/src/features/documents/DocumentPanel.tsx | 65 | setFailed(false) |
| frontend/src/features/documents/DocumentPanel.tsx | 66 | api<Draft>(`/documents/${id}/draft`) |
| frontend/src/features/documents/DocumentPanel.tsx | 66 | api<ReadDocument>(`/documents/${id}`) |
| frontend/src/features/documents/DocumentPanel.tsx | 71 | setDraft(d) |
| frontend/src/features/documents/DocumentPanel.tsx | 72 | setBody(d.body) |
| frontend/src/features/documents/DocumentPanel.tsx | 73 | setTitle(d.document.title) |
| frontend/src/features/documents/DocumentPanel.tsx | 74 | setPlacements(d.placements) |
| frontend/src/features/documents/DocumentPanel.tsx | 77 | setRead(d) |
| frontend/src/features/documents/DocumentPanel.tsx | 78 | setBody(d.body) |
| frontend/src/features/documents/DocumentPanel.tsx | 79 | setTitle(d.version.title) |
| frontend/src/features/documents/DocumentPanel.tsx | 81 | setPlacements(manifest.images.map((i) => i.placement)) |
| frontend/src/features/documents/DocumentPanel.tsx | 86 | setFailed(true) |
| frontend/src/features/documents/DocumentPanel.tsx | 96 | api(`/metrics/views/${id}`, 'POST', {<br>        id: crypto.randomUUID(),<br>        department_id: usageDepartment,<br>      }) |
| frontend/src/features/documents/DocumentPanel.tsx | 118 | setBusy(true) |
| frontend/src/features/documents/DocumentPanel.tsx | 120 | api<Draft>(`/documents/${id}/draft`, 'PUT', {<br>        title,<br>        body,<br>        revision: draft.revision,<br>        placements,<br>      }) |
| frontend/src/features/documents/DocumentPanel.tsx | 126 | setDraft(d) |
| frontend/src/features/documents/DocumentPanel.tsx | 127 | setDirty(false) |
| frontend/src/features/documents/DocumentPanel.tsx | 128 | setMessage('保存しました。') |
| frontend/src/features/documents/DocumentPanel.tsx | 130 | setMessage('未保存の変更があります。入力は保持されています。') |
| frontend/src/features/documents/DocumentPanel.tsx | 133 | setBusy(false) |
| frontend/src/features/documents/DocumentPanel.tsx | 138 | setBusy(true) |
| frontend/src/features/documents/DocumentPanel.tsx | 140 | api<Version>(<br>        `/documents/${id}/submissions`,<br>        'POST',<br>        { revision: draft.revision },<br>        crypto.randomUUID(),<br>      ) |
| frontend/src/features/documents/DocumentPanel.tsx | 146 | setMessage(<br>        `第${version.number}版を承認申請しました。${draft.document.latest_version_id ? '一般閲覧では現在の承認版が引き続き公開されます。' : '承認後に閲覧へ公開されます。'}`,<br>      ) |
| frontend/src/features/documents/DocumentPanel.tsx | 152 | setBusy(false) |
| frontend/src/features/documents/DocumentPanel.tsx | 157 | setHistory(await api(`/documents/${id}/history`)) |
| frontend/src/features/documents/DocumentPanel.tsx | 157 | api(`/documents/${id}/history`) |
| frontend/src/features/documents/DocumentPanel.tsx | 158 | setShowHistory(true) |
| frontend/src/features/documents/DocumentPanel.tsx | 165 | api<{ diff: string }>(<br>        `/documents/${id}/diff?left=${left}&right=${right}`,<br>      ) |
| frontend/src/features/documents/DocumentPanel.tsx | 168 | setDiff(result.diff) |
| frontend/src/features/documents/DocumentPanel.tsx | 230 | setReload(reload + 1) |
| frontend/src/features/documents/DocumentPanel.tsx | 238 | setShowLatest(true) |
| frontend/src/features/documents/DocumentPanel.tsx | 268 | setView(key!) |
| frontend/src/features/documents/DocumentPanel.tsx | 284 | setTitle(e.target.value) |
| frontend/src/features/documents/DocumentPanel.tsx | 285 | setDirty(true) |
| frontend/src/features/documents/DocumentPanel.tsx | 294 | setCursor(Array.from(body.slice(0, e.currentTarget.selectionStart)).length) |
| frontend/src/features/documents/DocumentPanel.tsx | 300 | setPlacements(relocatePlacements(body, e.target.value, placements)) |
| frontend/src/features/documents/DocumentPanel.tsx | 301 | setBody(e.target.value) |
| frontend/src/features/documents/DocumentPanel.tsx | 302 | setDirty(true) |
| frontend/src/features/documents/DocumentPanel.tsx | 338 | setPlacements(next) |
| frontend/src/features/documents/DocumentPanel.tsx | 339 | setDirty(true) |
| frontend/src/features/documents/Library.tsx | 47 | setLoading(true) |
| frontend/src/features/documents/Library.tsx | 48 | setFailed(false) |
| frontend/src/features/documents/Library.tsx | 57 | api<DocumentPage>(`/documents?${params}`) |
| frontend/src/features/documents/Library.tsx | 60 | setDocs(value.items) |
| frontend/src/features/documents/Library.tsx | 61 | setHasNext(value.has_next) |
| frontend/src/features/documents/Library.tsx | 66 | setFailed(true) |
| frontend/src/features/documents/Library.tsx | 71 | setLoading(false) |
| frontend/src/features/documents/Library.tsx | 78 | setBusy(true) |
| frontend/src/features/documents/Library.tsx | 80 | api<Document>('/documents', 'POST', { title, department_id: dept }) |
| frontend/src/features/documents/Library.tsx | 82 | setTitle('') |
| frontend/src/features/documents/Library.tsx | 83 | setCreating(false) |
| frontend/src/features/documents/Library.tsx | 88 | setBusy(false) |
| frontend/src/features/documents/Library.tsx | 92 | setSearch('') |
| frontend/src/features/documents/Library.tsx | 93 | setDepartment('') |
| frontend/src/features/documents/Library.tsx | 94 | setStatus('') |
| frontend/src/features/documents/Library.tsx | 95 | setFilter({ search: '', department: '', status: '' }) |
| frontend/src/features/documents/Library.tsx | 96 | setPage(0) |
| frontend/src/features/documents/Library.tsx | 111 | setCreating(!creating) |
| frontend/src/features/documents/Library.tsx | 122 | setTitle(e.target.value) |
| frontend/src/features/documents/Library.tsx | 126 | setDept(e.target.value) |
| frontend/src/features/documents/Library.tsx | 148 | setFilter({ search, department, status }) |
| frontend/src/features/documents/Library.tsx | 149 | setPage(0) |
| frontend/src/features/documents/Library.tsx | 157 | setSearch(e.target.value) |
| frontend/src/features/documents/Library.tsx | 164 | setDepartment(e.target.value) |
| frontend/src/features/documents/Library.tsx | 176 | setStatus(e.target.value) |
| frontend/src/features/documents/Library.tsx | 194 | setReload(reload + 1) |
| frontend/src/features/documents/Library.tsx | 264 | setPage(page - 1) |
| frontend/src/features/documents/Library.tsx | 268 | setPage(page + 1) |
| frontend/src/features/groups/Groups.tsx | 47 | setLoading(true) |
| frontend/src/features/groups/Groups.tsx | 48 | setFailed(false) |
| frontend/src/features/groups/Groups.tsx | 49 | setMetrics(null) |
| frontend/src/features/groups/Groups.tsx | 50 | setDocs([]) |
| frontend/src/features/groups/Groups.tsx | 51 | setMembers([]) |
| frontend/src/features/groups/Groups.tsx | 55 | api<DocumentPage>(<br>        `/documents?scope=manage&page=true&department_id=${department}&offset=${page * 30}`,<br>      ) |
| frontend/src/features/groups/Groups.tsx | 58 | api<Metrics>(`/metrics/${department}?start=${start.toISOString()}&end=${end.toISOString()}`) |
| frontend/src/features/groups/Groups.tsx | 59 | api<Member[]>(`/groups/${department}/members`) |
| frontend/src/features/groups/Groups.tsx | 63 | setDocs(d.items) |
| frontend/src/features/groups/Groups.tsx | 64 | setHasNext(d.has_next) |
| frontend/src/features/groups/Groups.tsx | 65 | setMetrics(m) |
| frontend/src/features/groups/Groups.tsx | 66 | setMembers(u) |
| frontend/src/features/groups/Groups.tsx | 71 | setFailed(true) |
| frontend/src/features/groups/Groups.tsx | 76 | setLoading(false) |
| frontend/src/features/groups/Groups.tsx | 87 | setBusy(true) |
| frontend/src/features/groups/Groups.tsx | 88 | setMember(null) |
| frontend/src/features/groups/Groups.tsx | 91 | api('/groups/memberships', 'PUT', {<br>        user_id: m.user_id,<br>        department_id: m.department_id,<br>        leader: m.leader,<br>        can_author: m.can_author,<br>        can_review: m.can_review,<br>        active: !m.active,<br>      }) |
| frontend/src/features/groups/Groups.tsx | 99 | setRevision((v) => v + 1) |
| frontend/src/features/groups/Groups.tsx | 103 | setBusy(false) |
| frontend/src/features/groups/Groups.tsx | 138 | setDepartment(value) |
| frontend/src/features/groups/Groups.tsx | 139 | setPage(0) |
| frontend/src/features/groups/Groups.tsx | 140 | setSelected(null) |
| frontend/src/features/groups/Groups.tsx | 153 | setPeriod(Number(e.target.value)) |
| frontend/src/features/groups/Groups.tsx | 164 | setRevision((v) => v + 1) |
| frontend/src/features/groups/Groups.tsx | 235 | setSelected(doc) |
| frontend/src/features/groups/Groups.tsx | 247 | setPage(page - 1) |
| frontend/src/features/groups/Groups.tsx | 251 | setPage(page + 1) |
| frontend/src/features/groups/Groups.tsx | 264 | setSelected(null) |
| frontend/src/features/groups/Groups.tsx | 266 | setNotice(message) |
| frontend/src/features/groups/Groups.tsx | 268 | setSelected(null) |
| frontend/src/features/groups/Groups.tsx | 269 | setRevision((v) => v + 1) |
| frontend/src/features/groups/Groups.tsx | 285 | setMember(m) |
| frontend/src/features/groups/Groups.tsx | 298 | setMember(null) |
| frontend/src/features/groups/Groups.tsx | 346 | setConfirm('') |
| frontend/src/features/groups/Groups.tsx | 347 | setBusy(true) |
| frontend/src/features/groups/Groups.tsx | 349 | api(`/documents/${doc.id}/policy`, 'PUT', {<br>        revision: doc.revision,<br>        visibility,<br>        shared_departments: visibility === 'selected' ? shared : [],<br>        status: deleting ? 'deleted' : status,<br>        reason: deleting ? reason : '',<br>      }) |
| frontend/src/features/groups/Groups.tsx | 358 | setNotice(<br>        '保存できませんでした。入力を保持しています。競合の場合は現在の設定を確認してください。',<br>      ) |
| frontend/src/features/groups/Groups.tsx | 363 | setBusy(false) |
| frontend/src/features/groups/Groups.tsx | 382 | setVisibility(e.target.value) |
| frontend/src/features/groups/Groups.tsx | 397 | setShared(<br>                    e.target.checked ? [...shared, d.id] : shared.filter((id) => id !== d.id),<br>                  ) |
| frontend/src/features/groups/Groups.tsx | 409 | setStatus(e.target.value) |
| frontend/src/features/groups/Groups.tsx | 426 | setConfirm('policy') |
| frontend/src/features/groups/Groups.tsx | 442 | setReason(e.target.value) |
| frontend/src/features/groups/Groups.tsx | 450 | setConfirm('delete') |
| frontend/src/features/groups/Groups.tsx | 460 | setConfirm('') |
| frontend/src/features/images/Images.tsx | 35 | setPending((current) => (current[id] === value ? current : { ...current, [id]: value })) |
| frontend/src/features/images/Images.tsx | 44 | setBusy(true) |
| frontend/src/features/images/Images.tsx | 48 | api<{ asset: { id: string }; ocr_run: { id: string }; ocr: Ocr }>(<br>        `/images/documents/${documentId}`,<br>        'POST',<br>        form,<br>      ) |
| frontend/src/features/images/Images.tsx | 68 | setBusy(false) |
| frontend/src/features/images/Images.tsx | 163 | setOcr(null) |
| frontend/src/features/images/Images.tsx | 164 | setFailed(false) |
| frontend/src/features/images/Images.tsx | 165 | api<Ocr>(`/images/ocr/${p.ocr_run_id}${versionId ? `?version_id=${versionId}` : ''}`) |
| frontend/src/features/images/Images.tsx | 168 | setOcr(value) |
| frontend/src/features/images/Images.tsx | 169 | setRegions(value.regions) |
| frontend/src/features/images/Images.tsx | 170 | setDirty(false) |
| frontend/src/features/images/Images.tsx | 175 | setFailed(true) |
| frontend/src/features/images/Images.tsx | 187 | setRegions(<br>      regions.map((r) =><br>        r.region_id === id ? { ...r, [field]: value, source: 'human', confidence: null } : r,<br>      ),<br>    ) |
| frontend/src/features/images/Images.tsx | 192 | setDirty(true) |
| frontend/src/features/images/Images.tsx | 195 | setBusy(true) |
| frontend/src/features/images/Images.tsx | 197 | api<{ ocr_run: { id: string } }>(`/images/${p.asset_id}/ocr`, 'POST', {<br>        regions: regions.map((r, i) => ({ ...r, order: i })),<br>        confirmed: true,<br>      }) |
| frontend/src/features/images/Images.tsx | 201 | setDirty(false) |
| frontend/src/features/images/Images.tsx | 203 | setNotice('OCRを確認しました。文書を保存してください。') |
| frontend/src/features/images/Images.tsx | 207 | setBusy(false) |
| frontend/src/features/images/Images.tsx | 297 | setSelected(r.region_id!) |
| frontend/src/features/images/Images.tsx | 309 | setRetry(retry + 1) |
| frontend/src/features/images/Images.tsx | 328 | setSelected(r.region_id!) |
| frontend/src/features/images/Images.tsx | 354 | setRegions(regions.filter((v) => v.region_id !== r.region_id)) |
| frontend/src/features/images/Images.tsx | 355 | setDirty(true) |
| frontend/src/features/images/Images.tsx | 375 | setAdding(!adding) |
| frontend/src/features/images/Images.tsx | 391 | setBounds({ ...bounds, [field]: e.target.value }) |
| frontend/src/features/images/Images.tsx | 400 | setRegions([<br>                        ...regions,<br>                        {<br>                          ...newBounds,<br>                          region_id: id,<br>                          text: '',<br>                          source: 'human',<br>                          confidence: null,<br>                          order: regions.length,<br>                        },<br>                      ]) |
| frontend/src/features/images/Images.tsx | 411 | setSelected(id) |
| frontend/src/features/images/Images.tsx | 412 | setDirty(true) |
| frontend/src/features/images/Images.tsx | 413 | setAdding(false) |
| frontend/src/features/images/ProtectedImage.tsx | 18 | setUrl('') |
| frontend/src/features/images/ProtectedImage.tsx | 19 | setFailed(false) |
| frontend/src/features/images/ProtectedImage.tsx | 21 | getImage(token, id, version) |
| frontend/src/features/images/ProtectedImage.tsx | 24 | setUrl(value) |
| frontend/src/features/images/ProtectedImage.tsx | 28 | setFailed(true) |
| frontend/src/features/operations/Operations.tsx | 12 | setLoading(true) |
| frontend/src/features/operations/Operations.tsx | 13 | setFailed(false) |
| frontend/src/features/operations/Operations.tsx | 14 | api<Job[]>('/operations/jobs?details=true') |
| frontend/src/features/operations/Operations.tsx | 16 | setJobs(value) |
| frontend/src/features/operations/Operations.tsx | 20 | setFailed(true) |
| frontend/src/features/operations/Operations.tsx | 25 | setLoading(false) |
| frontend/src/features/operations/Operations.tsx | 32 | setBusy(true) |
| frontend/src/features/operations/Operations.tsx | 34 | api(`/operations/jobs/${job.id}`, 'POST') |
| frontend/src/features/operations/Operations.tsx | 35 | setRevision(revision + 1) |
| frontend/src/features/operations/Operations.tsx | 39 | setBusy(false) |
| frontend/src/features/operations/Operations.tsx | 44 | setDifferences(await api('/operations/reconcile')) |
| frontend/src/features/operations/Operations.tsx | 44 | api('/operations/reconcile') |
| frontend/src/features/operations/Operations.tsx | 67 | setRevision((v) => v + 1) |
| frontend/src/features/reviews/Reviews.tsx | 39 | setLoading(true) |
| frontend/src/features/reviews/Reviews.tsx | 40 | setFailed(false) |
| frontend/src/features/reviews/Reviews.tsx | 41 | api<Review[]>('/reviews') |
| frontend/src/features/reviews/Reviews.tsx | 43 | setItems(value) |
| frontend/src/features/reviews/Reviews.tsx | 47 | setFailed(true) |
| frontend/src/features/reviews/Reviews.tsx | 52 | setLoading(false) |
| frontend/src/features/reviews/Reviews.tsx | 60 | api<ReadDocument>(<br>        `/documents/${item.submission.document_id}?version_id=${item.submission.version_id}`,<br>      ) |
| frontend/src/features/reviews/Reviews.tsx | 63 | setRead(value) |
| frontend/src/features/reviews/Reviews.tsx | 64 | setDiff('') |
| frontend/src/features/reviews/Reviews.tsx | 69 | api<{ diff: string }>(<br>          `/documents/${value.document.id}/diff?left=${value.document.latest_version_id}&right=${value.version.id}`,<br>        ) |
| frontend/src/features/reviews/Reviews.tsx | 72 | setDiff(compared.diff) |
| frontend/src/features/reviews/Reviews.tsx | 74 | setSelected(item) |
| frontend/src/features/reviews/Reviews.tsx | 75 | setReason('') |
| frontend/src/features/reviews/Reviews.tsx | 82 | setBusy(true) |
| frontend/src/features/reviews/Reviews.tsx | 83 | setConfirmation('') |
| frontend/src/features/reviews/Reviews.tsx | 85 | api(<br>        `/reviews/${selected.submission.id}/decision`,<br>        'POST',<br>        { manifest_hash: selected.submission.manifest_hash, decision, reason },<br>        crypto.randomUUID(),<br>      ) |
| frontend/src/features/reviews/Reviews.tsx | 91 | setMessage(<br>        `第${read!.version.number}版を${decision === 'approved' ? '承認' : '却下'}しました。${decision === 'approved' ? '公開状況とRAG反映状況は文書一覧で確認できます。' : ''}`,<br>      ) |
| frontend/src/features/reviews/Reviews.tsx | 94 | setReason('') |
| frontend/src/features/reviews/Reviews.tsx | 95 | setSelected(null) |
| frontend/src/features/reviews/Reviews.tsx | 96 | setRead(null) |
| frontend/src/features/reviews/Reviews.tsx | 100 | setBusy(false) |
| frontend/src/features/reviews/Reviews.tsx | 124 | setSelected(null) |
| frontend/src/features/reviews/Reviews.tsx | 125 | setReason('') |
| frontend/src/features/reviews/Reviews.tsx | 176 | setReason(e.target.value) |
| frontend/src/features/reviews/Reviews.tsx | 182 | setConfirmation('approved') |
| frontend/src/features/reviews/Reviews.tsx | 188 | setConfirmation('rejected') |
| frontend/src/features/reviews/Reviews.tsx | 201 | setRetry(retry + 1) |
| frontend/src/features/reviews/Reviews.tsx | 244 | setConfirmation('') |

## 操作イベント

| 実装 | 行 | イベント | 処理 |
| --- | --- | --- | --- |
| frontend/src/components/App.tsx | 114 | onLogin | {(value) => {<br>          sessionStorage.setItem('kotorelay-token', value);<br>          setIdentity(null);<br>          setToken(value);<br>          setSelected(null);<br>        }} |
| frontend/src/components/App.tsx | 145 | onClick | {(e) => {<br>              e.preventDefault();<br>              move('library');<br>            }} |
| frontend/src/components/App.tsx | 161 | onClick | {() => setMenu(!menu)} |
| frontend/src/components/App.tsx | 170 | onChange | {(e) => {<br>                const value = e.target.value;<br>                navigate(() => setDepartment(value));<br>              }} |
| frontend/src/components/App.tsx | 184 | onClick | {logout} |
| frontend/src/components/App.tsx | 197 | onClick | {() => move(id)} |
| frontend/src/components/App.tsx | 215 | onClick | {() => setError('')} |
| frontend/src/components/App.tsx | 228 | onBack | {() => navigate(() => setSelected(null))} |
| frontend/src/components/App.tsx | 229 | onError | {setError} |
| frontend/src/components/App.tsx | 236 | onOpen | {open} |
| frontend/src/components/App.tsx | 237 | onError | {setError} |
| frontend/src/components/App.tsx | 240 | onError | {setError} |
| frontend/src/components/App.tsx | 242 | onError | {setError} |
| frontend/src/components/App.tsx | 244 | onError | {setError} |
| frontend/src/components/App.tsx | 253 | onOpen | {open} |
| frontend/src/components/App.tsx | 254 | onError | {setError} |
| frontend/src/components/App.tsx | 269 | onCancel | {() => setPending(null)} |
| frontend/src/components/App.tsx | 270 | onConfirm | {() => {<br>          const action = pending;<br>          dirtyKeys.current.clear();<br>          setPending(null);<br>          action?.();<br>        }} |
| frontend/src/components/layout/Login.tsx | 53 | onChange | {(e) => setPersona(e.target.value)} |
| frontend/src/components/layout/Login.tsx | 63 | onClick | {() => onLogin(`demo-${persona}`)} |
| frontend/src/components/layout/Login.tsx | 76 | onChange | {(e) => setAccessToken(e.target.value)} |
| frontend/src/components/layout/Login.tsx | 83 | onClick | {() => onLogin(accessToken)} |
| frontend/src/components/ui/ConfirmDialog.tsx | 36 | onCancel | {(e) => {<br>        e.preventDefault();<br>        onCancel();<br>      }} |
| frontend/src/components/ui/ConfirmDialog.tsx | 44 | onClick | {onCancel} |
| frontend/src/components/ui/ConfirmDialog.tsx | 47 | onClick | {onConfirm} |
| frontend/src/features/chat/Chat.tsx | 75 | onClick | {() => void refresh()} |
| frontend/src/features/chat/Chat.tsx | 110 | onClick | {() => onOpen(c.document_id, c)} |
| frontend/src/features/chat/Chat.tsx | 132 | onSubmit | {(e) => {<br>            e.preventDefault();<br>            void ask();<br>          }} |
| frontend/src/features/chat/Chat.tsx | 143 | onChange | {(e) => {<br>                  setDepartment(e.target.value);<br>                  setConversation(null);<br>                  setAnswers([]);<br>                  setNotice('利用部署を変更し、新しい会話を開始しました。');<br>                }} |
| frontend/src/features/chat/Chat.tsx | 166 | onChange | {(e) => setQuestion(e.target.value)} |
| frontend/src/features/documents/DocumentPanel.tsx | 175 | onClick | {onBack} |
| frontend/src/features/documents/DocumentPanel.tsx | 195 | onClick | {() => void loadHistory()} |
| frontend/src/features/documents/DocumentPanel.tsx | 202 | onClick | {() => void save()} |
| frontend/src/features/documents/DocumentPanel.tsx | 211 | onClick | {() => void submit()} |
| frontend/src/features/documents/DocumentPanel.tsx | 230 | onClick | {() => setReload(reload + 1)} |
| frontend/src/features/documents/DocumentPanel.tsx | 238 | onClick | {() => setShowLatest(true)} |
| frontend/src/features/documents/DocumentPanel.tsx | 241 | onClick | {onBack} |
| frontend/src/features/documents/DocumentPanel.tsx | 268 | onClick | {() => setView(key!)} |
| frontend/src/features/documents/DocumentPanel.tsx | 283 | onChange | {(e) => {<br>                setTitle(e.target.value);<br>                setDirty(true);<br>              }} |
| frontend/src/features/documents/DocumentPanel.tsx | 293 | onSelect | {(e) =><br>                  setCursor(Array.from(body.slice(0, e.currentTarget.selectionStart)).length)<br>                } |
| frontend/src/features/documents/DocumentPanel.tsx | 299 | onChange | {(e) => {<br>                  setPlacements(relocatePlacements(body, e.target.value, placements));<br>                  setBody(e.target.value);<br>                  setDirty(true);<br>                }} |
| frontend/src/features/documents/DocumentPanel.tsx | 337 | onChange | {(next) => {<br>            setPlacements(next);<br>            setDirty(true);<br>          }} |
| frontend/src/features/documents/DocumentPanel.tsx | 342 | onPending | {setOcrPending} |
| frontend/src/features/documents/DocumentPanel.tsx | 343 | onError | {onError} |
| frontend/src/features/documents/DocumentPanel.tsx | 357 | onClick | {() => void compare(history[index + 1]!.version.id, item.version.id)} |
| frontend/src/features/documents/DocumentPanel.tsx | 367 | onClick | {() => {<br>              const blob = new Blob([body], { type: 'text/markdown' });<br>              const url = URL.createObjectURL(blob);<br>              const a = document.createElement('a');<br>              a.href = url;<br>              a.download = 'draft.md';<br>              a.click();<br>              URL.revokeObjectURL(url);<br>            }} |
| frontend/src/features/documents/Library.tsx | 111 | onClick | {() => setCreating(!creating)} |
| frontend/src/features/documents/Library.tsx | 122 | onChange | {(e) => setTitle(e.target.value)} |
| frontend/src/features/documents/Library.tsx | 126 | onChange | {(e) => setDept(e.target.value)} |
| frontend/src/features/documents/Library.tsx | 137 | onClick | {() => void create()} |
| frontend/src/features/documents/Library.tsx | 146 | onSubmit | {(e) => {<br>          e.preventDefault();<br>          setFilter({ search, department, status });<br>          setPage(0);<br>        }} |
| frontend/src/features/documents/Library.tsx | 157 | onChange | {(e) => setSearch(e.target.value)} |
| frontend/src/features/documents/Library.tsx | 164 | onChange | {(e) => setDepartment(e.target.value)} |
| frontend/src/features/documents/Library.tsx | 176 | onChange | {(e) => setStatus(e.target.value)} |
| frontend/src/features/documents/Library.tsx | 194 | onClick | {() => setReload(reload + 1)} |
| frontend/src/features/documents/Library.tsx | 208 | onClick | {reset} |
| frontend/src/features/documents/Library.tsx | 235 | onClick | {(e) => {<br>                    e.preventDefault();<br>                    onOpen(doc.id);<br>                  }} |
| frontend/src/features/documents/Library.tsx | 264 | onClick | {() => setPage(page - 1)} |
| frontend/src/features/documents/Library.tsx | 268 | onClick | {() => setPage(page + 1)} |
| frontend/src/features/groups/Groups.tsx | 135 | onChange | {(e) => {<br>                  const value = e.target.value;<br>                  move(() => {<br>                    setDepartment(value);<br>                    setPage(0);<br>                    setSelected(null);<br>                  });<br>                }} |
| frontend/src/features/groups/Groups.tsx | 153 | onChange | {(e) => setPeriod(Number(e.target.value))} |
| frontend/src/features/groups/Groups.tsx | 164 | onClick | {() => setRevision((v) => v + 1)} |
| frontend/src/features/groups/Groups.tsx | 235 | onClick | {() => move(() => setSelected(doc))} |
| frontend/src/features/groups/Groups.tsx | 247 | onClick | {() => setPage(page - 1)} |
| frontend/src/features/groups/Groups.tsx | 251 | onClick | {() => setPage(page + 1)} |
| frontend/src/features/groups/Groups.tsx | 263 | onError | {onError} |
| frontend/src/features/groups/Groups.tsx | 264 | onCancel | {() => setSelected(null)} |
| frontend/src/features/groups/Groups.tsx | 265 | onSaved | {(message) => {<br>                setNotice(message);<br>                heading.current?.focus();<br>                setSelected(null);<br>                setRevision((v) => v + 1);<br>              }} |
| frontend/src/features/groups/Groups.tsx | 285 | onClick | {() => setMember(m)} |
| frontend/src/features/groups/Groups.tsx | 298 | onCancel | {() => setMember(null)} |
| frontend/src/features/groups/Groups.tsx | 299 | onConfirm | {() => void revoke()} |
| frontend/src/features/groups/Groups.tsx | 382 | onChange | {(e) => setVisibility(e.target.value)} |
| frontend/src/features/groups/Groups.tsx | 396 | onChange | {(e) =><br>                  setShared(<br>                    e.target.checked ? [...shared, d.id] : shared.filter((id) => id !== d.id),<br>                  )<br>                } |
| frontend/src/features/groups/Groups.tsx | 409 | onChange | {(e) => setStatus(e.target.value)} |
| frontend/src/features/groups/Groups.tsx | 426 | onClick | {() => setConfirm('policy')} |
| frontend/src/features/groups/Groups.tsx | 430 | onClick | {onCancel} |
| frontend/src/features/groups/Groups.tsx | 442 | onChange | {(e) => setReason(e.target.value)} |
| frontend/src/features/groups/Groups.tsx | 450 | onClick | {() => setConfirm('delete')} |
| frontend/src/features/groups/Groups.tsx | 460 | onCancel | {() => setConfirm('')} |
| frontend/src/features/groups/Groups.tsx | 461 | onConfirm | {() => void save()} |
| frontend/src/features/images/Images.tsx | 92 | onChange | {(e) => {<br>                const file = e.target.files?.[0];<br>                if (file) void upload(file);<br>                e.target.value = '';<br>              }} |
| frontend/src/features/images/Images.tsx | 114 | onChange | {(next) => onChange(placements.map((v) => (v.id === p.id ? next : v)))} |
| frontend/src/features/images/Images.tsx | 115 | onRemove | {() => onChange(placements.filter((v) => v.id !== p.id))} |
| frontend/src/features/images/Images.tsx | 116 | onError | {onError} |
| frontend/src/features/images/Images.tsx | 247 | onChange | {(e) => onChange({ ...p, alt_text: e.target.value })} |
| frontend/src/features/images/Images.tsx | 256 | onChange | {(e) => onChange({ ...p, caption: e.target.value })} |
| frontend/src/features/images/Images.tsx | 266 | onChange | {(e) => onChange({ ...p, offset: Number(e.target.value) })} |
| frontend/src/features/images/Images.tsx | 296 | onClick | {() => {<br>                  setSelected(r.region_id!);<br>                  refs.current[r.region_id!]?.focus();<br>                }} |
| frontend/src/features/images/Images.tsx | 309 | onClick | {() => setRetry(retry + 1)} |
| frontend/src/features/images/Images.tsx | 328 | onFocus | {() => setSelected(r.region_id!)} |
| frontend/src/features/images/Images.tsx | 329 | onChange | {(e) => change(r.region_id!, 'text', e.target.value)} |
| frontend/src/features/images/Images.tsx | 345 | onChange | {(e) => change(r.region_id!, field, Number(e.target.value))} |
| frontend/src/features/images/Images.tsx | 353 | onClick | {() => {<br>                      setRegions(regions.filter((v) => v.region_id !== r.region_id));<br>                      setDirty(true);<br>                    }} |
| frontend/src/features/images/Images.tsx | 375 | onClick | {() => setAdding(!adding)} |
| frontend/src/features/images/Images.tsx | 391 | onChange | {(e) => setBounds({ ...bounds, [field]: e.target.value })} |
| frontend/src/features/images/Images.tsx | 398 | onClick | {() => {<br>                      const id = crypto.randomUUID();<br>                      setRegions([<br>                        ...regions,<br>                        {<br>                          ...newBounds,<br>                          region_id: id,<br>                          text: '',<br>                          source: 'human',<br>                          confidence: null,<br>                          order: regions.length,<br>                        },<br>                      ]);<br>                      setSelected(id);<br>                      setDirty(true);<br>                      setAdding(false);<br>                    }} |
| frontend/src/features/images/Images.tsx | 428 | onClick | {() => void confirm()} |
| frontend/src/features/images/Images.tsx | 432 | onClick | {onRemove} |
| frontend/src/features/operations/Operations.tsx | 57 | onClick | {() => void reconcile()} |
| frontend/src/features/operations/Operations.tsx | 67 | onClick | {() => setRevision((v) => v + 1)} |
| frontend/src/features/operations/Operations.tsx | 92 | onClick | {() => void process(job)} |
| frontend/src/features/reviews/Reviews.tsx | 122 | onClick | {() => {<br>              const back = () => {<br>                setSelected(null);<br>                setReason('');<br>              };<br>              if (guard.navigate) guard.navigate(back);<br>              else back();<br>            }} |
| frontend/src/features/reviews/Reviews.tsx | 166 | onChange | {() => {}} |
| frontend/src/features/reviews/Reviews.tsx | 168 | onError | {onError} |
| frontend/src/features/reviews/Reviews.tsx | 176 | onChange | {(e) => setReason(e.target.value)} |
| frontend/src/features/reviews/Reviews.tsx | 182 | onClick | {() => setConfirmation('approved')} |
| frontend/src/features/reviews/Reviews.tsx | 188 | onClick | {() => setConfirmation('rejected')} |
| frontend/src/features/reviews/Reviews.tsx | 201 | onClick | {() => setRetry(retry + 1)} |
| frontend/src/features/reviews/Reviews.tsx | 230 | onClick | {() => void open(item)} |
| frontend/src/features/reviews/Reviews.tsx | 244 | onCancel | {() => setConfirmation('')} |
| frontend/src/features/reviews/Reviews.tsx | 245 | onConfirm | {() => void decide(confirmation)} |

## スタイル定義

```css
:root {
  font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', Meiryo, system-ui, sans-serif;
  font-synthesis: none;
  color: #1a1a1a;
  background: #f7f9f8;
  font-size: 100%;
  line-height: 1.6;
  --green: #176851;
  --muted: #595959;
  --border: #d8dfdb;
  --control-border: #767676;
  --link: #0017c1;
  --danger: #b42318;
  --focus: #ffd43d;
}

```

## 表示と版の整合

同じPlacedDocumentをプレビュー・審査・閲覧に使います。挿入位置はUnicodeコードポイント数です。OCR領域の識別と位置を独立して保持し、版と画像は認可付きAPIから読み込みます。未保存確認はWorkspaceで共有し、引用版の変更と非許可状態を区別して表示します。詳細は上記の実装イベントに対応します。