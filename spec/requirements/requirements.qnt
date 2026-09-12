// 永続要件の一次言語。product固有の要件を追加し、JSONとMarkdownをここから生成する。
module requirements {
  type AcceptanceCriterion = { id: str, given: str, when_: str, expected: str }
  type Verification = { method: str, evidence: str }
  type Traces = {
    design: List[str],
    implementation: List[str],
    tests: List[str],
    standards: List[str],
  }
  type Requirement = {
    id: str,
    revision: int,
    status: str,
    kind: str,
    title: str,
    subject: str,
    actionName: str,
    objectName: str,
    rationale: str,
    sourceRefs: List[str],
    acceptanceCriteria: List[AcceptanceCriterion],
    verification: Verification,
    traces: Traces,
    lastChangedBy: str,
    retirementReason: str,
    supersededBy: str,
    scopeName: str,
    categoryName: str,
  }
  type Catalog = {
    schemaVersion: int,
    catalogRevision: int,
    product: str,
    updatedAt: str,
    requirements: List[Requirement],
  }
  type RequirementOperation = {
    kind: str,
    id: str,
    expectedRevision: int,
    replacement: Requirement,
  }
  type BatchFold = {
    requirements: List[Requirement],
    touchedIds: List[str],
    valid: bool,
  }
  type Lifecycle = {
    catalogRevision: int,
    itemRevision: int,
    itemPresent: bool,
    itemStatus: str,
    traceRevision: int,
    priorCatalogRevision: int,
    priorItemRevision: int,
    priorItemPresent: bool,
    priorItemStatus: str,
    priorTraceRevision: int,
    lastOperation: str,
  }

  pure val requirementsSource: Catalog = {
  schemaVersion: 1,
  catalogRevision: 2,
  product: "KotoRelay（コトリレー）— 承認済み文書と画像に基づく部署対応RAG",
  updatedAt: "2026-09-12",
  requirements: [{
      id: "REQ-DOC-01",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "ブラウザでMarkdownを編集する",
      subject: "システム",
      actionName: "provide",
      objectName: "Markdown本文の編集",
      rationale: "優先度: Must（初期版の必須）。明示要求を具体化する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u01"],
      acceptanceCriteria: [{
          id: "AC-DOC-01",
          given: "担当文書の編集権限がある",
          when_: "ブラウザで本文を編集して保存する",
          expected: "Markdownの内容が保存され、再読込後も同じ内容を編集できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "initial-requirements-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-DOC-02",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "Markdownの表示を確認する",
      subject: "システム",
      actionName: "provide",
      objectName: "Markdownの表示確認",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u01"],
      acceptanceCriteria: [{
          id: "AC-DOC-02",
          given: "編集可能なMarkdownがある",
          when_: "プレビューを開く",
          expected: "見出し・段落・箇条書き・リンク・表・コードブロックが確認できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "initial-requirements-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-DOC-03",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "保存結果を明示する",
      subject: "システム",
      actionName: "provide",
      objectName: "保存状態の表示",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u01"],
      acceptanceCriteria: [{
          id: "AC-DOC-03",
          given: "本文に未保存変更がある",
          when_: "保存要求が成功または失敗する",
          expected: "成功時だけ保存済みと表示し、失敗時は未保存変更を保持して再試行できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "initial-requirements-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-DOC-04",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "文書と文書版を識別する",
      subject: "システム",
      actionName: "provide",
      objectName: "文書IDと文書版IDの分離",
      rationale: "優先度: Must（初期版の必須）。明示要求を具体化する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u02"],
      acceptanceCriteria: [{
          id: "AC-DOC-04",
          given: "同じ文書に複数の版がある",
          when_: "版を追加する",
          expected: "文書IDは維持され、変更不能な新しい文書版IDと文書内で一意の版番号が発行される",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-DOC-05",
      revision: 2,
      status: "active",
      kind: "constraint",
      title: "確定した版を改変させない",
      subject: "システム",
      actionName: "enforce",
      objectName: "文書版の不変性",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u02"],
      acceptanceCriteria: [{
          id: "AC-DOC-05",
          given: "保存された確定版または申請対象版がある",
          when_: "同じ版IDの本文を変更しようとする",
          expected: "変更を拒否し、改訂内容には別の版IDを割り当てる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-DOC-06",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "版の履歴を確認する",
      subject: "システム",
      actionName: "provide",
      objectName: "版履歴の閲覧",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u02"],
      acceptanceCriteria: [{
          id: "AC-DOC-06",
          given: "履歴閲覧権限がある",
          when_: "文書の版履歴を開く",
          expected: "版番号・作成者・作成日時・審査状態を版ごとに確認できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-DOC-07",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "版の差分を確認する",
      subject: "システム",
      actionName: "provide",
      objectName: "版間差分の表示",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u02"],
      acceptanceCriteria: [{
          id: "AC-DOC-07",
          given: "比較対象の両方の版に閲覧権限がある",
          when_: "二つの版を指定して比較する",
          expected: "追加・削除・変更箇所を比較対象の版IDとともに表示する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-DOC-08",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "編集競合を検出する",
      subject: "システム",
      actionName: "provide",
      objectName: "同時編集の更新競合検出",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u02"],
      acceptanceCriteria: [{
          id: "AC-DOC-08",
          given: "二人が同じ下書き更新番号から編集した",
          when_: "先行保存後に後続保存が到着する",
          expected: "後続保存を競合として拒否し、先行内容を黙って上書きせず、後続の入力を失わない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-WF-01",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "特定の版を承認申請する",
      subject: "システム",
      actionName: "provide",
      objectName: "文書版の承認申請",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u03",
        "docs/planning/REQUESTS.md#u12",
        "docs/planning/REQUESTS.md#u13"],
      acceptanceCriteria: [{
          id: "AC-WF-01",
          given: "執筆者が確定版を作成した",
          when_: "承認申請する",
          expected: "版ID・本文・画像・OCRを含む承認manifestハッシュ・申請者・申請日時を結び付けて審査待ちにする",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/reviews/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-WF-02",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "権限のある承認者が版を承認する",
      subject: "システム",
      actionName: "provide",
      objectName: "版単位の承認",
      rationale: "優先度: Must（初期版の必須）。明示要求を具体化する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u03",
        "docs/planning/REQUESTS.md#u12",
        "docs/planning/REQUESTS.md#u13"],
      acceptanceCriteria: [{
          id: "AC-WF-02",
          given: "対象版が審査待ちで承認権限がある",
          when_: "承認する",
          expected: "確認した版IDと承認manifestハッシュの版だけを承認済みにし、承認者と日時を記録する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/reviews/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-WF-03",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "却下理由を残す",
      subject: "システム",
      actionName: "provide",
      objectName: "版単位の却下",
      rationale: "優先度: Must（初期版の必須）。明示要求を具体化する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u03"],
      acceptanceCriteria: [{
          id: "AC-WF-03",
          given: "対象版が審査待ちで承認権限がある",
          when_: "理由を入力して却下する",
          expected: "対象版を却下とし、理由・実行者・日時を執筆者が確認できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/reviews/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-WF-04",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "却下後に改訂して再申請する",
      subject: "システム",
      actionName: "provide",
      objectName: "再申請の履歴維持",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u03"],
      acceptanceCriteria: [{
          id: "AC-WF-04",
          given: "却下された版がある",
          when_: "執筆者が修正して再申請する",
          expected: "却下履歴を残し、修正内容を別の版IDで申請する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/reviews/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-WF-05",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "審査結果の競合を防ぐ",
      subject: "システム",
      actionName: "provide",
      objectName: "承認と却下の競合制御",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u03"],
      acceptanceCriteria: [{
          id: "AC-WF-05",
          given: "同じ申請を複数の承認者が開いている",
          when_: "承認と却下が競合する",
          expected: "有効な審査遷移は一つだけ成立し、後続に最新状態と競合を返す",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/reviews/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-WF-06",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "審査操作を重複適用しない",
      subject: "システム",
      actionName: "provide",
      objectName: "審査要求の冪等性",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u03"],
      acceptanceCriteria: [{
          id: "AC-WF-06",
          given: "通信断により同じ審査要求が再送される",
          when_: "同じ要求識別子で再試行する",
          expected: "承認履歴・公開版更新・連携要求を重複作成せず、成立済みの結果を返す",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/reviews/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-WF-07",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "審査操作の認可を強制する",
      subject: "システム",
      actionName: "provide",
      objectName: "サーバーによる審査認可",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u03"],
      acceptanceCriteria: [{
          id: "AC-WF-07",
          given: "承認権限のない利用者または審査対象外の版がある",
          when_: "APIから直接承認や却下を要求する",
          expected: "処理を拒否し、版状態と公開状態を変更しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/reviews/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-ACL-01",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "利用者の本人性を検証する",
      subject: "システム",
      actionName: "provide",
      objectName: "保護された操作の認証",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-ACL-01",
          given: "未認証または無効な認証情報の要求が来る",
          when_: "文書閲覧・編集・審査・検索・チャットを要求する",
          expected: "保護された内容を返さず、認証が必要であることを返す",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-ACL-02",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "操作権限と公開範囲を別々に適用する",
      subject: "システム",
      actionName: "provide",
      objectName: "役割と資源権限の組合せ",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-ACL-02",
          given: "役割が同じでも文書の公開範囲が異なる",
          when_: "文書操作または検索を要求する",
          expected: "その操作を許す役割と対象文書の権限を両方満たす場合だけ許可する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-ACL-03",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "下書きの閲覧を制限する",
      subject: "システム",
      actionName: "provide",
      objectName: "未承認版へのアクセス制御",
      rationale: "優先度: Must（初期版の必須）。明示要求を具体化する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u05"],
      acceptanceCriteria: [{
          id: "AC-ACL-03",
          given: "文書に下書き・審査待ち・却下版がある",
          when_: "一般利用者と文書担当者がそれぞれアクセスする",
          expected: "一般利用者を拒否し、対象文書の下書き閲覧権限を持つ執筆者や承認者だけに表示する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-ACL-04",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "一般利用者には承認済み版だけを表示する",
      subject: "システム",
      actionName: "provide",
      objectName: "未承認内容の非公開",
      rationale: "優先度: Must（初期版の必須）。明示要求を具体化する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u04"],
      acceptanceCriteria: [{
          id: "AC-ACL-04",
          given: "未承認内容が承認済み版と同じ文書にある",
          when_: "一般利用者が本文・履歴・差分を開く",
          expected: "権限を満たす承認済み版だけを表示し、未承認内容を含む差分も返さない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-ACL-05",
      revision: 2,
      status: "active",
      kind: "constraint",
      title: "権限欠損時に拒否する",
      subject: "システム",
      actionName: "enforce",
      objectName: "認可失敗時の閉鎖",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-ACL-05",
          given: "公開範囲が未設定、不正または認可情報を取得できない",
          when_: "文書・検索・生成へのアクセスを要求する",
          expected: "公開扱いに補完せず拒否または一時利用不可とする",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-ACL-06",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "文書の存在情報も保護する",
      subject: "システム",
      actionName: "provide",
      objectName: "検索結果と補助表示の認可",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-ACL-06",
          given: "権限外の文書が存在する",
          when_: "一覧・検索・候補補完・件数・タグ集計を見る",
          expected: "権限外のタイトル・抜粋・存在を示す個別情報を表示しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-ACL-07",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "直接URLや識別子でも認可する",
      subject: "システム",
      actionName: "provide",
      objectName: "全取得経路でのアクセス制御",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-ACL-07",
          given: "他文書・他利用者のIDや引用URLを知っている",
          when_: "API・版URL・ダウンロード先へ直接アクセスする",
          expected: "現在の権限を再判定し、権限外の内容を返さない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-ACL-08",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "クライアントに権限を決めさせない",
      subject: "システム",
      actionName: "provide",
      objectName: "信頼できる属性による認可",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-ACL-08",
          given: "利用者が役割・所属・公開範囲・検索フィルターを改ざんする",
          when_: "改ざん値をAPIへ送る",
          expected: "認証済みIDとサーバー管理の最新権限から許可範囲を決め、権限を拡大しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-ACL-09",
      revision: 2,
      status: "active",
      kind: "constraint",
      title: "権限剥奪を索引更新から独立させる",
      subject: "システム",
      actionName: "enforce",
      objectName: "最新権限によるアクセス停止",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-ACL-09",
          given: "アカウント無効化・所属削除・文書範囲縮小が正本へ確定した",
          when_: "確定後に新しい閲覧・検索・生成を要求する",
          expected: "古いトークンや古い索引の許可を採用せず、剥奪対象を拒否する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-ACL-10",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "親文書の制限を断片へ引き継ぐ",
      subject: "システム",
      actionName: "provide",
      objectName: "チャンクと添付の権限継承",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-ACL-10",
          given: "文書を検索断片や表示用データへ変換する",
          when_: "断片または関連コンテンツを利用する",
          expected: "元文書より広い公開範囲にならず、出所と現在権限を再確認できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-ACL-11",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "会話を利用者に結び付ける",
      subject: "システム",
      actionName: "provide",
      objectName: "会話の所有者境界",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-ACL-11",
          given: "別利用者の会話IDを知っている",
          when_: "会話取得・追質問・削除を要求する",
          expected: "その会話への権限がない要求を拒否する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-ACL-12",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "履歴とキャッシュにも現在権限を適用する",
      subject: "システム",
      actionName: "provide",
      objectName: "保存された回答の再認可",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-ACL-12",
          given: "過去回答の参照文書への権限を後から失った",
          when_: "履歴を再表示またはキャッシュを再利用する",
          expected: "失効した根拠由来の回答本文を再配信・再利用せず、非表示の理由だけを権限に配慮して示す",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-PUB-01",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "文書ごとの最新承認版を一意に決める",
      subject: "システム",
      actionName: "provide",
      objectName: "最新承認版の決定",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-PUB-01",
          given: "同じ文書に複数の承認済み版がある",
          when_: "最新承認版を求める",
          expected: "文書内の版順で最も新しい承認済み版を一つだけ選び、承認操作の到着順で古い版に戻さない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-PUB-02",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "未承認の新版は公開版へ影響させない",
      subject: "システム",
      actionName: "provide",
      objectName: "審査中の公開継続",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u04"],
      acceptanceCriteria: [{
          id: "AC-PUB-02",
          given: "v1が承認済みでv2が下書き・審査待ちまたは却下である",
          when_: "一般閲覧またはRAG検索を行う",
          expected: "v2を公開・回答根拠へ混ぜず、有効なv1を利用できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-PUB-03",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "新版承認後に旧版で回答しない",
      subject: "システム",
      actionName: "provide",
      objectName: "旧承認版の回答利用停止",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-PUB-03",
          given: "v2の承認が確定しv1の検索データが残っている",
          when_: "新しい回答根拠を選ぶ",
          expected: "v1を除外し、v2の検索準備が未完了ならその文書を一時的に根拠から除く",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-PUB-04",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "索引未反映を利用者へ説明する",
      subject: "システム",
      actionName: "provide",
      objectName: "文書公開とRAG準備状態の分離",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-PUB-04",
          given: "最新版は承認済みだが検索準備待ちまたは失敗である",
          when_: "権限のある利用者が文書を閲覧する",
          expected: "最新版本文を閲覧でき、RAGへの反映状態を区別して確認できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-PUB-05",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "非公開化を回答根拠へ反映する",
      subject: "システム",
      actionName: "provide",
      objectName: "公開停止文書の利用停止",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-PUB-05",
          given: "文書の公開停止が確定した",
          when_: "閲覧・検索・引用または回答送信を行う",
          expected: "公開停止文書を利用せず、旧承認版へ自動的に戻さない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-PUB-06",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "古い連携ジョブで公開状態を戻さない",
      subject: "システム",
      actionName: "provide",
      objectName: "非同期処理の版順保証",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-PUB-06",
          given: "新版の処理後に旧版ジョブが遅着する",
          when_: "旧版ジョブの結果を反映する",
          expected: "最新承認版の指示を上書きせず、旧ジョブを失効として扱う",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/documents/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IDX-01",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "未承認本文を本番RAGの索引へ入れない",
      subject: "システム",
      actionName: "provide",
      objectName: "検索用データの入力制限",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-IDX-01",
          given: "下書き領域と承認済み領域がある",
          when_: "本番の索引作成処理を実行する",
          expected: "対象は承認済みの検索用データだけとなり、未承認本文を取得できない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/indexing/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IDX-02",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "索引の来歴を保持する",
      subject: "システム",
      actionName: "provide",
      objectName: "根拠断片の出所記録",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-IDX-02",
          given: "文書を検索断片へ変換する",
          when_: "断片を保存する",
          expected: "文書ID・版ID・本文ハッシュ・断片ID・見出し位置・処理設定版を追跡できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/indexing/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IDX-03",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "検索準備完了を実データで判定する",
      subject: "システム",
      actionName: "provide",
      objectName: "索引反映の公開判定",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-IDX-03",
          given: "取り込みジョブが完了と報告された",
          when_: "RAG利用可能へ切り替える",
          expected: "対象版の件数・必須属性・取得可能性を検証し、一部失敗や反映遅延だけでは完了扱いにしない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/indexing/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IDX-04",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "検索断片の欠損を拒否する",
      subject: "システム",
      actionName: "provide",
      objectName: "必須属性の検証",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-IDX-04",
          given: "版IDや権限識別情報が欠けた検索データがある",
          when_: "取り込みまたは根拠選択する",
          expected: "欠損値を推測せず対象を隔離し、生成へ渡さない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/indexing/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IDX-05",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "検索反映の失敗を再処理する",
      subject: "システム",
      actionName: "provide",
      objectName: "失敗した索引反映の回復",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-IDX-05",
          given: "一時エラーまたは恒久エラーで取り込みに失敗した",
          when_: "再試行または運用者の再処理を行う",
          expected: "重複した有効断片を作らず回復でき、失敗理由と対象版を運用者が確認できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/indexing/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IDX-06",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "正本と索引の不一致を検出する",
      subject: "システム",
      actionName: "provide",
      objectName: "反映漏れの照合",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-IDX-06",
          given: "更新イベントが欠落または重複した",
          when_: "正本と索引の照合を実行する",
          expected: "未反映・旧版残留・公開停止残留を検出し、安全な利用制限を維持したまま修復対象にする",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/indexing/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-RAG-01",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "質問に対してチャットで回答する",
      subject: "システム",
      actionName: "provide",
      objectName: "根拠に基づくチャット回答",
      rationale: "優先度: Must（初期版の必須）。明示要求を具体化する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-RAG-01",
          given: "閲覧可能な最新承認版に回答根拠がある",
          when_: "利用者が質問する",
          expected: "質問に対応した日本語の回答をチャット画面へ返す",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-RAG-02",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "検索時に公開範囲を強制する",
      subject: "システム",
      actionName: "provide",
      objectName: "必須検索条件の適用",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-RAG-02",
          given: "複数の公開範囲が索引に存在する",
          when_: "候補を検索する",
          expected: "認証済み利用者の許可範囲を検索前または検索中に適用し、候補不足でも条件を解除しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-RAG-03",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "モデルへ渡す前に根拠を再検証する",
      subject: "システム",
      actionName: "provide",
      objectName: "生成入力の有効性検証",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-RAG-03",
          given: "検索候補に旧版や権限変更前の断片が含まれ得る",
          when_: "候補を再順位付け器・圧縮器・生成モデルへ渡す",
          expected: "現行ACL・最新承認版・公開状態・承認manifestとchunk/画像hashが一致する本文・OCR・画像だけを渡す",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-RAG-04",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "回答の送信直前に再検証する",
      subject: "システム",
      actionName: "provide",
      objectName: "処理中の権限と版変更の反映",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-RAG-04",
          given: "検索後から回答確定前までに権限または承認版が変化する",
          when_: "回答を確定して送信する",
          expected: "確定時の根拠再検証に失敗した回答を送らず、新状態で再生成するか回答を保留する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-RAG-05",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "利用した文書版を引用する",
      subject: "システム",
      actionName: "provide",
      objectName: "回答と根拠の対応表示",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-RAG-05",
          given: "根拠付きの回答を返す",
          when_: "利用者が出典を見る",
          expected: "実際に使用した文書名・版ID・見出し・到達可能な引用先を確認でき、モデルが架空の引用先を付けても採用しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-RAG-06",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "根拠不足時に回答を保留する",
      subject: "システム",
      actionName: "provide",
      objectName: "未裏付け回答の抑止",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-RAG-06",
          given: "根拠がない、不足する、または矛盾を解決できない",
          when_: "質問に回答する",
          expected: "不足や確認事項を示し、未承認版・旧版・権限外資料・一般知識で業務事実を補って断定しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-RAG-07",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "追質問でも根拠を取り直す",
      subject: "システム",
      actionName: "provide",
      objectName: "会話継続時の根拠更新",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-RAG-07",
          given: "過去の回答後に文書版または権限が変わった",
          when_: "続けて質問する",
          expected: "過去のAI回答を正本として使わず、現在利用可能な根拠を再取得する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-RAG-08",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "文書内の命令で権限を変えさせない",
      subject: "システム",
      actionName: "provide",
      objectName: "プロンプトインジェクションへの境界維持",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-RAG-08",
          given: "文書や質問に権限無視・秘密開示・外部送信を指示する文がある",
          when_: "RAG処理する",
          expected: "その指示によって検索範囲・権限・外部操作を変えず、文書内容を情報として扱う",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-RAG-09",
      revision: 2,
      status: "active",
      kind: "constraint",
      title: "機密本文を処理ログへ残さない",
      subject: "システム",
      actionName: "enforce",
      objectName: "診断データの保護",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-RAG-09",
          given: "文書や質問に機密情報が含まれる",
          when_: "通常ログやエラーを記録する",
          expected: "認可前の候補本文や認証トークンを記録せず、許可された監査情報と本文の保存先を分離する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-OPS-01",
      revision: 2,
      status: "active",
      kind: "constraint",
      title: "AWS上で提供する",
      subject: "システム",
      actionName: "enforce",
      objectName: "AWS上の実行基盤",
      rationale: "優先度: Must（初期版の必須）。明示要求を具体化する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u08"],
      acceptanceCriteria: [{
          id: "AC-OPS-01",
          given: "システムを構築する",
          when_: "運用構成を選定する",
          expected: "フロント・API・文書保存・認証・RAGの主要機能をAWS上のサービスで提供する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md", "docs/design/generated/INFRA.md", "docs/OPERATIONS.md"],
        implementation: ["frontend/src/components/App.tsx", "infra/src/kotorelay_infra/stack.py", "backend/src/kotorelay/worker.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx", "infra/tests/test_stack.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-OPS-02",
      revision: 2,
      status: "active",
      kind: "constraint",
      title: "待機用計算資源の固定費を避ける",
      subject: "システム",
      actionName: "enforce",
      objectName: "利用量に連動する運用費",
      rationale: "優先度: Must（初期版の必須）。明示要求を具体化する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u08"],
      acceptanceCriteria: [{
          id: "AC-OPS-02",
          given: "通常運用のサービス構成を選定する",
          when_: "無アクセス時と通常利用時を見積もる",
          expected: "常時起動サーバーや最低計算容量の常設を必須にせず、保存費・付帯費・利用時の従量費を明示する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md", "docs/design/generated/INFRA.md", "docs/OPERATIONS.md"],
        implementation: ["frontend/src/components/App.tsx", "infra/src/kotorelay_infra/stack.py", "backend/src/kotorelay/worker.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx", "infra/tests/test_stack.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-OPS-03",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "人による審査履歴を監査できる",
      subject: "システム",
      actionName: "provide",
      objectName: "承認の追跡可能性",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u03"],
      acceptanceCriteria: [{
          id: "AC-OPS-03",
          given: "版が申請・承認・却下された",
          when_: "権限を持つ監査担当が履歴を確認する",
          expected: "対象版・実行主体・時刻・前後状態・却下理由を追跡でき、一般編集者が履歴を改変できない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md", "docs/design/generated/INFRA.md", "docs/OPERATIONS.md"],
        implementation: ["frontend/src/components/App.tsx", "infra/src/kotorelay_infra/stack.py", "backend/src/kotorelay/worker.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx", "infra/tests/test_stack.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-OPS-04",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "回答経路を追跡できる",
      subject: "システム",
      actionName: "provide",
      objectName: "回答の再現に必要な識別情報",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u06"],
      acceptanceCriteria: [{
          id: "AC-OPS-04",
          given: "回答または回答保留が発生した",
          when_: "運用者が原因を調査する",
          expected: "要求IDから利用した版・方針版・モデル版・検索設定・処理結果へ到達できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md", "docs/design/generated/INFRA.md", "docs/OPERATIONS.md"],
        implementation: ["frontend/src/components/App.tsx", "infra/src/kotorelay_infra/stack.py", "backend/src/kotorelay/worker.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx", "infra/tests/test_stack.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-OPS-05",
      revision: 2,
      status: "active",
      kind: "constraint",
      title: "高額な処理を制限する",
      subject: "システム",
      actionName: "enforce",
      objectName: "生成と取り込みの利用制限",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u08"],
      acceptanceCriteria: [{
          id: "AC-OPS-05",
          given: "利用者またはジョブが上限を超える",
          when_: "質問や再取り込みを要求する",
          expected: "設定された回数・同時実行・入力長・出力長・再試行上限を超えた処理を停止し、利用者へ理由を示す",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md", "docs/design/generated/INFRA.md", "docs/OPERATIONS.md"],
        implementation: ["frontend/src/components/App.tsx", "infra/src/kotorelay_infra/stack.py", "backend/src/kotorelay/worker.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx", "infra/tests/test_stack.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-OPS-06",
      revision: 2,
      status: "active",
      kind: "constraint",
      title: "承認と権限の正本を復旧できる",
      subject: "システム",
      actionName: "enforce",
      objectName: "文書版と制御情報の復旧",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u02"],
      acceptanceCriteria: [{
          id: "AC-OPS-06",
          given: "保存データや索引の復旧が必要となる",
          when_: "バックアップから復旧する",
          expected: "文書版と審査履歴を結び付けて復旧し、最新の失効情報が未検証の状態では閲覧とRAGを再開しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md", "docs/design/generated/INFRA.md", "docs/OPERATIONS.md"],
        implementation: ["frontend/src/components/App.tsx", "infra/src/kotorelay_infra/stack.py", "backend/src/kotorelay/worker.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx", "infra/tests/test_stack.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-OPS-07",
      revision: 2,
      status: "active",
      kind: "functional",
      title: "費用を工程別に確認する",
      subject: "システム",
      actionName: "provide",
      objectName: "費用の可視化",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u08"],
      acceptanceCriteria: [{
          id: "AC-OPS-07",
          given: "検索・生成・取り込み処理が稼働する",
          when_: "運用費を確認する",
          expected: "保存・検索・埋め込み・生成・API等の費用と利用量を分けて把握できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md", "docs/design/generated/INFRA.md", "docs/OPERATIONS.md"],
        implementation: ["frontend/src/components/App.tsx", "infra/src/kotorelay_infra/stack.py", "backend/src/kotorelay/worker.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx", "infra/tests/test_stack.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-ACL-13",
      revision: 1,
      status: "active",
      kind: "constraint",
      title: "Markdown表示で実行コードを動かさない",
      subject: "システム",
      actionName: "enforce",
      objectName: "編集・閲覧・回答画面での安全な描画",
      rationale: "優先度: Must（初期版の必須）。U01のブラウザ執筆とU07の権限を、保存型スクリプトによって迂回させないための派生条件。",
      sourceRefs: ["docs/planning/REQUESTS.md#u01",
        "docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-ACL-13",
          given: "本文・タイトル・回答にscript、イベント属性、危険なURLが含まれる",
          when_: "エディターのプレビュー、文書、引用または回答を表示する",
          expected: "埋め込まれたコードを実行せず、認証情報へのアクセスや意図しない外部通信を発生させない",
        }],
      verification: {
        method: "セキュリティ・E2E試験（製品試験は未実施）",
        evidence: "保存型XSSの入力を各描画経路へ渡し、コード実行と外部通信が発生しないことを確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/chat/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "initial-requirements-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-OPS-08",
      revision: 2,
      status: "active",
      kind: "constraint",
      title: "保護対象の通信と保存を暗号化する",
      subject: "システム",
      actionName: "enforce",
      objectName: "文書・権限・会話・監査情報の暗号化",
      rationale: "優先度: Must（初期版の必須）。公開範囲を設けた情報を通信と保存の経路でも保護する、U07からの派生条件。具体的な鍵方式は設計で決定する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u07"],
      acceptanceCriteria: [{
          id: "AC-OPS-08",
          given: "保護対象データを通信または保存する",
          when_: "通信経路と保存設定を検証する",
          expected: "保護対象の通信は暗号化され、文書・索引・制御情報・バックアップ・保存する会話と監査情報には保存時暗号化が適用される",
        }],
      verification: {
        method: "設定レビュー・構成試験（製品試験は未実施）",
        evidence: "実際の通信経路と各保存先の暗号化設定を確認する。鍵の権限と復旧手順は詳細設計で追跡する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md", "docs/design/generated/INFRA.md", "docs/OPERATIONS.md"],
        implementation: ["frontend/src/components/App.tsx", "infra/src/kotorelay_infra/stack.py", "backend/src/kotorelay/worker.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx", "infra/tests/test_stack.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-PRJ-01",
      revision: 1,
      status: "active",
      kind: "constraint",
      title: "要件を一つの正本から更新する",
      subject: "開発担当",
      actionName: "enforce",
      objectName: "要求と受入条件の一貫した保守",
      rationale: "優先度: Must（初期版の必須）。明示要求を具体化する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u09"],
      acceptanceCriteria: [{
          id: "AC-PRJ-01",
          given: "要件が追加・変更・廃止される",
          when_: "開発担当が文書を更新する",
          expected: "Quintの原子的要件を更新し、JSONとMarkdownを再生成して差分検査し、廃止時は理由を残す",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md"],
        implementation: ["tools/quintflow.py", "tools/project/design.py", "tools/project/evidence.py"],
        tests: ["tools/project/tests/test_project_tools.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "initial-requirements-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "project",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-PRJ-02",
      revision: 1,
      status: "active",
      kind: "constraint",
      title: "実装と検証の対応を追跡する",
      subject: "開発担当",
      actionName: "enforce",
      objectName: "要件と下流成果物の対応",
      rationale: "優先度: Must（初期版の必須）。利用者の明示要求を一貫して成立させるための派生条件。業務運用の選択肢は企画書の提案欄で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u09"],
      acceptanceCriteria: [{
          id: "AC-PRJ-02",
          given: "要件に対応する実装・検証が作成された",
          when_: "開発担当が要件との対応を更新する",
          expected: "実在する実装と検証への参照を追加し、未作成の成果物を完成済みとして記録しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "この受入条件の入力・期待結果・実測結果を照合する。実装時に対応する試験と証跡の参照を登録する。",
      },
      traces: {
        design: ["docs/design/generated/API.md"],
        implementation: ["tools/quintflow.py", "tools/project/design.py", "tools/project/evidence.py"],
        tests: ["tools/project/tests/test_project_tools.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "initial-requirements-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "project",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-DAT-01",
      revision: 1,
      status: "active",
      kind: "constraint",
      title: "Aurora DSQLを業務データの正本にする",
      subject: "システム",
      actionName: "enforce",
      objectName: "部署・文書・審査・利用管理データ",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u11"],
      acceptanceCriteria: [{
          id: "AC-DAT-01",
          given: "AWS上に業務データを保存する",
          when_: "データ保存先を実装する",
          expected: "文書版・審査・現行権限・部署・利用記録をAurora DSQLで管理し、本文と画像実体は参照hash付きの非公開オブジェクトとして分離する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/DATA.md"],
        implementation: ["backend/migrations/007_versions.sql", "backend/src/kotorelay/db.py"],
        tests: ["backend/tests/test_postgres.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-DAT-02",
      revision: 1,
      status: "active",
      kind: "constraint",
      title: "別組織・別文書への誤参照を防ぐ",
      subject: "システム",
      actionName: "enforce",
      objectName: "主キー・一意制約・複合外部キー",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u11"],
      acceptanceCriteria: [{
          id: "AC-DAT-02",
          given: "別文書または別組織の版・画像・OCRのIDを指定する",
          when_: "関係データを登録する",
          expected: "定義した複合FKで不整合な登録を拒否し、FKだけで閲覧認可が済んだとは扱わない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/DATA.md"],
        implementation: ["backend/migrations/007_versions.sql", "backend/src/kotorelay/db.py"],
        tests: ["backend/tests/test_postgres.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-DAT-03",
      revision: 1,
      status: "active",
      kind: "constraint",
      title: "非同期要求を業務更新と一緒に確定する",
      subject: "システム",
      actionName: "enforce",
      objectName: "DSQLと非同期処理の連携",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u11"],
      acceptanceCriteria: [{
          id: "AC-DAT-03",
          given: "承認・画像処理・削除で非同期処理が必要",
          when_: "正本状態を更新する",
          expected: "配送予定を同一transactionで記録し、重複配送・配送中断・遅着を冪等性と再照合で回復する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/DATA.md"],
        implementation: ["backend/migrations/007_versions.sql", "backend/src/kotorelay/db.py"],
        tests: ["backend/tests/test_postgres.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-DAT-04",
      revision: 1,
      status: "active",
      kind: "constraint",
      title: "DSQLの上限内で大量データを処理する",
      subject: "システム",
      actionName: "enforce",
      objectName: "OCR領域・チャンク・削除の分割処理",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u11"],
      acceptanceCriteria: [{
          id: "AC-DAT-04",
          given: "一回ではDBの更新行数やバイト上限を超える",
          when_: "作成または破棄する",
          expected: "上限内のバッチで再開可能に処理し、部分完了をsealed・ready・削除完了として扱わない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/DATA.md"],
        implementation: ["backend/migrations/007_versions.sql", "backend/src/kotorelay/db.py"],
        tests: ["backend/tests/test_postgres.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-IMG-01",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "文書に画像を添付して編集する",
      subject: "システム",
      actionName: "provide",
      objectName: "ブラウザの画像付きMarkdown編集",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u12"],
      acceptanceCriteria: [{
          id: "AC-IMG-01",
          given: "対象文書の執筆権限がある",
          when_: "対応画像を添付・移動・削除し保存する",
          expected: "本文中の挿入位置と画像IDが保持され、再表示して本文と画像を確認できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/images/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IMG-02",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "画像の文字をOCRで抽出する",
      subject: "システム",
      actionName: "provide",
      objectName: "画像中の日本語を含む文字起こし",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u13"],
      acceptanceCriteria: [{
          id: "AC-IMG-02",
          given: "対応画像に認識対象の文字がある",
          when_: "OCRを実行する",
          expected: "文字列・読み順・信頼度・OCR方式版を保存し、失敗と文字のない正常画像を区別する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/images/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IMG-03",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "OCR文字の画像内位置を保持する",
      subject: "システム",
      actionName: "provide",
      objectName: "画像内の矩形と多角形座標",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u13"],
      acceptanceCriteria: [{
          id: "AC-IMG-03",
          given: "OCR文字領域が検出された",
          when_: "結果を保存・表示する",
          expected: "canonical画像の寸法と正規化bbox/polygonを対応付け、画面サイズや回転が変わっても同じ文字領域を示せる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/images/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IMG-04",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "画像の文書内挿入位置を保持する",
      subject: "システム",
      actionName: "provide",
      objectName: "画像ノードの安定IDと原文範囲",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u13"],
      acceptanceCriteria: [{
          id: "AC-IMG-04",
          given: "同じ画像が複数箇所に配置されている",
          when_: "編集・版確定・引用を行う",
          expected: "配置ごとに識別し、版ID・見出し・本文中の位置から正しい挿入箇所へ到達できる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/images/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IMG-05",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "本文と画像とOCRを一つの承認対象にする",
      subject: "システム",
      actionName: "provide",
      objectName: "不変な画像付き版manifest",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u12"],
      acceptanceCriteria: [{
          id: "AC-IMG-05",
          given: "画像付きの版を申請する",
          when_: "申請および承認を確定する",
          expected: "本文・画像hash・配置・OCR run/hashを同じmanifestに固定し、OCR未完了または未確認の配置があれば申請を拒否する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/images/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IMG-06",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "OCRを訂正しても承認済み版を改変しない",
      subject: "システム",
      actionName: "provide",
      objectName: "OCR確認と訂正の版管理",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u13"],
      acceptanceCriteria: [{
          id: "AC-IMG-06",
          given: "編集者がOCR誤りを発見する",
          when_: "文字や領域を訂正して採用する",
          expected: "旧結果を保持した新OCR runを作り、承認版へ反映するには新しい文書版の審査を要する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/images/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IMG-07",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "チャンクから対応する画像とOCR領域を復元する",
      subject: "システム",
      actionName: "provide",
      objectName: "chunkと画像配置・OCR領域の対応",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u13"],
      acceptanceCriteria: [{
          id: "AC-IMG-07",
          given: "本文・画像・OCR文字を分割する",
          when_: "検索用chunkを生成する",
          expected: "画像を含むchunkごとに画像配置とOCR領域を関連付け、OCRが複数chunkへ分かれても元画像と領域へ戻れる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/images/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IMG-08",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "画像付き根拠をモデルの画像入力へ渡す",
      subject: "システム",
      actionName: "provide",
      objectName: "文字と画像を組み合わせた生成入力",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u14"],
      acceptanceCriteria: [{
          id: "AC-IMG-08",
          given: "採用された根拠chunkに画像の関連がある",
          when_: "生成モデルを呼び出す",
          expected: "同じ承認manifestの認可済み画像を構造化image入力へ含め、HTTPではBase64・SDKでは適切なbytesを用いて二重変換しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/images/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IMG-09",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "画像を渡せない根拠を黙って使わない",
      subject: "システム",
      actionName: "provide",
      objectName: "画像入力予算と根拠の完全性",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u14"],
      acceptanceCriteria: [{
          id: "AC-IMG-09",
          given: "選択chunkの画像が枚数・サイズ・解像度・token予算に収まらない",
          when_: "生成入力を組み立てる",
          expected: "予算内へ再選定する際は画像を渡せないchunkを全体として外し、必要根拠が不足すれば質問を絞るか回答を保留する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/images/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-IMG-10",
      revision: 1,
      status: "active",
      kind: "constraint",
      title: "画像・OCRにも文書の現行認可を適用する",
      subject: "システム",
      actionName: "enforce",
      objectName: "派生画像・OCR・モデル入力の保護",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u14"],
      acceptanceCriteria: [{
          id: "AC-IMG-10",
          given: "画像取得前または回答確定前に公開版や権限が変わる",
          when_: "画像表示・OCR取得・生成・引用を行う",
          expected: "現在許可される版と画像hashだけを利用し、旧版・未承認・権限外の画像やOCR文字を渡さない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/images/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-IMG-11",
      revision: 1,
      status: "active",
      kind: "constraint",
      title: "添付画像の不正入力を隔離する",
      subject: "システム",
      actionName: "enforce",
      objectName: "画像ファイルと外部参照の検証",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u12"],
      acceptanceCriteria: [{
          id: "AC-IMG-11",
          given: "画像のMIME偽装・破損・過大サイズ・外部URLが入力される",
          when_: "アップロードまたは画像処理を行う",
          expected: "許可形式・内容・サイズを検証し、不正画像を通常表示・OCR・生成に渡さず、任意外部URLを取得しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/images/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-IMG-12",
      revision: 1,
      status: "active",
      kind: "constraint",
      title: "画像バイナリを通常ログへ残さない",
      subject: "システム",
      actionName: "enforce",
      objectName: "Base64とOCR内容の診断情報保護",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u14"],
      acceptanceCriteria: [{
          id: "AC-IMG-12",
          given: "画像付き生成が成功または失敗する",
          when_: "保存・配送・ログを記録する",
          expected: "画像実体は非公開S3、DSQLと通常ログは必要な識別子・hash・サイズに限定し、Base64やOCR全文を通常ログへ書かない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/images/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-GRP-01",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "部署単位の所属と権限を管理する",
      subject: "システム",
      actionName: "provide",
      objectName: "部署・構成員・リーダー・兼務",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u15"],
      acceptanceCriteria: [{
          id: "AC-GRP-01",
          given: "利用者が一つ以上の部署に所属する",
          when_: "所属または役割を登録・更新・失効する",
          expected: "部署ごとの役割と執筆・審査権限を区別して管理し、認可で現行状態を用いる",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/groups/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-GRP-02",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "文書の所有部署と公開先を分ける",
      subject: "システム",
      actionName: "provide",
      objectName: "部署所有と部署間共有",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u15"],
      acceptanceCriteria: [{
          id: "AC-GRP-02",
          given: "部署Aの文書を部署Bへ公開する",
          when_: "Bの利用者が閲覧や管理を要求する",
          expected: "承認済み内容のreadを許可できるが、共有だけでは編集・承認・削除権限を与えない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/groups/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-GRP-03",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "リーダーが自部署の文書一覧を確認する",
      subject: "システム",
      actionName: "provide",
      objectName: "部署文書の管理一覧",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u15"],
      acceptanceCriteria: [{
          id: "AC-GRP-03",
          given: "現在の所属でleaderである",
          when_: "部署管理一覧を開く",
          expected: "自部署所有文書の管理用タイトル・更新・版・公開範囲・審査と反映状態をページングして確認でき、他部署管理情報を返さない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/groups/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-GRP-04",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "リーダーが審査状況を確認する",
      subject: "システム",
      actionName: "provide",
      objectName: "部署文書の申請・決定状況",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u15"],
      acceptanceCriteria: [{
          id: "AC-GRP-04",
          given: "自部署所有文書に審査履歴がある",
          when_: "リーダーが審査状況を見る",
          expected: "申請版・申請日時・状態・決定日時・却下理由を確認でき、本文閲覧と承認操作は別の権限で判定する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/groups/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-GRP-05",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "リーダーが自部署の文書を削除する",
      subject: "システム",
      actionName: "provide",
      objectName: "部署文書の削除",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u15"],
      acceptanceCriteria: [{
          id: "AC-GRP-05",
          given: "対象文書を所有する部署の現行leaderである",
          when_: "対象と理由を確認して削除を要求する",
          expected: "文書を論理削除し監査に残し、直後の認可から本文・画像・検索・生成・引用・過去回答の再配信を停止する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/groups/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-GRP-06",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "削除を再開可能に完了させる",
      subject: "システム",
      actionName: "provide",
      objectName: "保持と物理削除ジョブ",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u15"],
      acceptanceCriteria: [{
          id: "AC-GRP-06",
          given: "削除済み文書の保持期限と保全条件が満たされた",
          when_: "物理削除を進める",
          expected: "索引・S3オブジェクト版・OCR・派生データを依存順に削除し、失敗時に再開でき、未完了を完了と表示しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/groups/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-GRP-07",
      revision: 1,
      status: "active",
      kind: "constraint",
      title: "リーダーに承認権限を自動付与しない",
      subject: "システム",
      actionName: "enforce",
      objectName: "管理と審査の職務境界",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u15"],
      acceptanceCriteria: [{
          id: "AC-GRP-07",
          given: "leaderだがcan_reviewがない",
          when_: "審査APIを直接呼ぶ",
          expected: "拒否する。管理一覧権限だけで下書き本文や他人の会話本文を取得する要求も拒否する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/groups/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-MET-01",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "部署リーダーがRAG利用数を確認する",
      subject: "システム",
      actionName: "provide",
      objectName: "部署の質問数と処理結果",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u15"],
      acceptanceCriteria: [{
          id: "AC-MET-01",
          given: "自部署の質問が受け付けられた",
          when_: "期間を指定して集計を見る",
          expected: "一意な質問受付数と回答・保留・失敗・取消を区別して表示し、モデル再試行や通信再送を質問数へ二重計上しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/metrics/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-MET-02",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "部署リーダーが閲覧数を確認する",
      subject: "システム",
      actionName: "provide",
      objectName: "部署別・所有文書別の表示件数",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u15"],
      acceptanceCriteria: [{
          id: "AC-MET-02",
          given: "利用者が承認版本文を表示した",
          when_: "表示確認を記録して集計する",
          expected: "同一view IDの再送を一件とし、消費部署別と所有文書別に確認でき、preview・画像取得・RAG内部検索を閲覧として数えない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/metrics/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-MET-03",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "文書が回答に使われた回数を確認する",
      subject: "システム",
      actionName: "provide",
      objectName: "所有文書のRAG貢献",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u15"],
      acceptanceCriteria: [{
          id: "AC-MET-03",
          given: "一回答が同じ文書の複数chunkを使う",
          when_: "文書別のRAG利用を集計する",
          expected: "当該文書の一意な確定回答数として一件を計上し、文書別件数の合計を部署の質問数と混同しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/metrics/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-MET-04",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "兼務者の利用を一つの部署に帰属させる",
      subject: "システム",
      actionName: "provide",
      objectName: "利用時の部署スナップショット",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u15"],
      acceptanceCriteria: [{
          id: "AC-MET-04",
          given: "利用者が複数の有効所属を持つ",
          when_: "チャットまたは閲覧を開始する",
          expected: "検証済みの利用部署を一つ記録し、後日の異動で過去利用を付け替えず、選択部署による権限拡大を許さない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/metrics/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-MET-05",
      revision: 1,
      status: "active",
      kind: "functional",
      title: "集計を再計算し遅延を示す",
      subject: "システム",
      actionName: "provide",
      objectName: "利用イベントと集計の整合性",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u15"],
      acceptanceCriteria: [{
          id: "AC-MET-05",
          given: "重複または遅着イベントがある",
          when_: "期間集計を更新する",
          expected: "一意イベントから再計算して重複加算を防ぎ、集計時刻・時刻帯・反映範囲を表示し、期間ユニーク数を日次値の合計で代用しない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/metrics/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "functional",
    },
    {
      id: "REQ-MET-06",
      revision: 1,
      status: "active",
      kind: "constraint",
      title: "管理統計から会話本文を漏らさない",
      subject: "システム",
      actionName: "enforce",
      objectName: "部署境界と集計データの最小化",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u15"],
      acceptanceCriteria: [{
          id: "AC-MET-06",
          given: "リーダーが統計APIやIDを改ざんする",
          when_: "他部署の集計や個人の質問本文を要求する",
          expected: "管理対象外の情報を拒否し、通常の部署統計には他人の会話本文や他部署利用者名を含めない",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md", "docs/design/generated/FRONTEND.md"],
        implementation: ["frontend/src/components/App.tsx", "backend/src/kotorelay/operations/metrics/functions.py"],
        tests: ["backend/tests/test_workflow.py", "frontend/tests/app.test.tsx"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "product",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-PRJ-03",
      revision: 1,
      status: "active",
      kind: "constraint",
      title: "プロジェクト名をKotoRelayに統一する",
      subject: "開発担当",
      actionName: "enforce",
      objectName: "名称と識別子",
      rationale: "優先度: Must（初期版の必須）。追加の明示要求と、それを一貫して成立させる派生条件。具体的な上限値や運用選択は提案設計で別管理する。",
      sourceRefs: ["docs/planning/REQUESTS.md#u10"],
      acceptanceCriteria: [{
          id: "AC-PRJ-03",
          given: "このプロジェクトの文書と設計を作成する",
          when_: "名称を記載する",
          expected: "名称KotoRelay・読みコトリレー・識別子kotorelayを用い、既存資料の版履歴は維持する",
        }],
      verification: {
        method: "設計レビュー・単体試験・PostgreSQL結合試験・Compose E2E（AWS実機は未検証）",
        evidence: "受入条件の入力・期待結果・実測結果を照合する。DSQL制約、モデルへ実際に送った画像の識別子、現行認可、利用イベントを必要に応じて確認する。",
      },
      traces: {
        design: ["docs/design/generated/API.md"],
        implementation: ["tools/quintflow.py", "tools/project/design.py", "tools/project/evidence.py"],
        tests: ["tools/project/tests/test_project_tools.py"],
        standards: ["AGENTS.md"],
      },
      lastChangedBy: "requirements-v0.2-2026-09-12",
      retirementReason: "",
      supersededBy: "",
      scopeName: "project",
      categoryName: "nonfunctional",
    },
    {
      id: "REQ-PRJ-04", revision: 1, status: "active", kind: "constraint",
      title: "指定技術で実装する", subject: "開発担当", actionName: "enforce", objectName: "指定技術で実装する",
      rationale: "利用者の実装・品質公開の明示指定。", sourceRefs: ["docs/planning/REQUESTS.md#u16"],
      acceptanceCriteria: [{ id: "AC-PRJ-04", given: "KotoRelayの実装がある", when_: "実装を構築する", expected: "TypeScript/Astro、Python/FastAPI/uv、Python CDKを使用し、AWSはDSQL、ローカルはPostgreSQLへ接続する" }],
      verification: {method: "CIとローカルの実コマンド", evidence: "GitHub Pagesの同一runの品質記録"},
      traces: {design: ["docs/design/generated/INFRA.md"], implementation: ["tools/project/verify.py", "frontend/portal/App.tsx", "infra/src/kotorelay_infra/stack.py"], tests: ["tools/project/tests/test_project_tools.py", "infra/tests/test_stack.py", "e2e/workflow.spec.ts"], standards: ["AGENTS.md"]},
      lastChangedBy: "implementation-2026-09-12", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional",
    },
    {
      id: "REQ-PRJ-05", revision: 1, status: "active", kind: "constraint",
      title: "品質の閾値を検査する", subject: "開発担当", actionName: "enforce", objectName: "品質の閾値を検査する",
      rationale: "利用者の実装・品質公開の明示指定。", sourceRefs: ["docs/planning/REQUESTS.md#u16"],
      acceptanceCriteria: [{ id: "AC-PRJ-05", given: "KotoRelayの実装がある", when_: "実装を検証する", expected: "静的解析・整形・単体試験を実行し、C0相当95%以上とC1相当90%以上の実測値を判定する" }],
      verification: {method: "CIとローカルの実コマンド", evidence: "GitHub Pagesの同一runの品質記録"},
      traces: {design: ["docs/design/generated/INFRA.md"], implementation: ["tools/project/verify.py", "frontend/portal/App.tsx", "infra/src/kotorelay_infra/stack.py"], tests: ["tools/project/tests/test_project_tools.py", "infra/tests/test_stack.py", "e2e/workflow.spec.ts"], standards: ["AGENTS.md"]},
      lastChangedBy: "implementation-2026-09-12", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional",
    },
    {
      id: "REQ-PRJ-06", revision: 1, status: "active", kind: "constraint",
      title: "Compose上でE2Eの証拠を取得する", subject: "開発担当", actionName: "enforce", objectName: "Compose上でE2Eの証拠を取得する",
      rationale: "利用者の実装・品質公開の明示指定。", sourceRefs: ["docs/planning/REQUESTS.md#u16"],
      acceptanceCriteria: [{ id: "AC-PRJ-06", given: "KotoRelayの実装がある", when_: "Playwrightを実行する", expected: "Given/When/Thenの説明と各段階の画面PNGを保存し、必要なDB状態を提示する" }],
      verification: {method: "CIとローカルの実コマンド", evidence: "GitHub Pagesの同一runの品質記録"},
      traces: {design: ["docs/design/generated/INFRA.md"], implementation: ["tools/project/verify.py", "frontend/portal/App.tsx", "infra/src/kotorelay_infra/stack.py"], tests: ["tools/project/tests/test_project_tools.py", "infra/tests/test_stack.py", "e2e/workflow.spec.ts"], standards: ["AGENTS.md"]},
      lastChangedBy: "implementation-2026-09-12", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional",
    },
    {
      id: "REQ-PRJ-07", revision: 1, status: "active", kind: "constraint",
      title: "設計と品質を単一SPAで公開する", subject: "開発担当", actionName: "enforce", objectName: "設計と品質を単一SPAで公開する",
      rationale: "利用者の実装・品質公開の明示指定。", sourceRefs: ["docs/planning/REQUESTS.md#u16"],
      acceptanceCriteria: [{ id: "AC-PRJ-07", given: "KotoRelayの実装がある", when_: "Gitへpushして公開する", expected: "GitHub Pagesで設計・静的解析・カバレッジ・日本語単体試験一覧・E2E画像を単一SPAとして閲覧できる" }],
      verification: {method: "CIとローカルの実コマンド", evidence: "GitHub Pagesの同一runの品質記録"},
      traces: {design: ["docs/design/generated/INFRA.md"], implementation: ["tools/project/verify.py", "frontend/portal/App.tsx", "infra/src/kotorelay_infra/stack.py"], tests: ["tools/project/tests/test_project_tools.py", "infra/tests/test_stack.py", "e2e/workflow.spec.ts"], standards: ["AGENTS.md"]},
      lastChangedBy: "implementation-2026-09-12", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional",
    },
    {
      id: "REQ-PRJ-08", revision: 1, status: "active", kind: "constraint",
      title: "CDKの構成を多面的に検証する", subject: "開発担当", actionName: "enforce", objectName: "CDKの構成を多面的に検証する",
      rationale: "利用者の実装・品質公開の明示指定。", sourceRefs: ["docs/planning/REQUESTS.md#u16"],
      acceptanceCriteria: [{ id: "AC-PRJ-08", given: "KotoRelayの実装がある", when_: "CDKをsynthする", expected: "cdk-nag・スナップショット・アサーションを実行し、費用を増やす対策の除外は対象と理由を明示する" }],
      verification: {method: "CIとローカルの実コマンド", evidence: "GitHub Pagesの同一runの品質記録"},
      traces: {design: ["docs/design/generated/INFRA.md"], implementation: ["tools/project/verify.py", "frontend/portal/App.tsx", "infra/src/kotorelay_infra/stack.py"], tests: ["tools/project/tests/test_project_tools.py", "infra/tests/test_stack.py", "e2e/workflow.spec.ts"], standards: ["AGENTS.md"]},
      lastChangedBy: "implementation-2026-09-12", retirementReason: "", supersededBy: "", scopeName: "project", categoryName: "nonfunctional",
    }],
}

  pure val lifecycleRequirement: Requirement = {
    id: "REQ-LIFECYCLE-MODEL-001",
    revision: 1,
    status: "active",
    kind: "functional",
    title: "lifecycle fixture",
    subject: "requirements lifecycle model",
    actionName: "maintain",
    objectName: "a typed catalog requirement",
    rationale: "A concrete item makes lifecycle refinement non-vacuous.",
    sourceRefs: ["model:requirements-lifecycle"],
    acceptanceCriteria: [
      { id: "AC-LIFECYCLE-MODEL-001-1", given: "a current catalog", when_: "a CAS transition is accepted", expected: "catalog and item revisions advance together" }
    ],
    verification: { method: "Quint model", evidence: "catalog lifecycle transition tests" },
    traces: {
      design: [],
      implementation: [],
      tests: [],
      standards: ["QUINT-0.32"],
    },
    lastChangedBy: "model:add",
    retirementReason: "",
    supersededBy: "",
    scopeName: "project",
    categoryName: "nonfunctional",
  }

  pure val successionR1: Requirement = lifecycleRequirement
    .with("id", "REQ-SUCCESSION-R1")
    .with("acceptanceCriteria", [
      { id: "AC-SUCCESSION-R1", given: "R1 exists", when_: "R1 is superseded", expected: "the chain advances" }
    ])
    .with("status", "retired")
    .with("retirementReason", "superseded by R2")
    .with("supersededBy", "REQ-SUCCESSION-R2")
  pure val successionR2: Requirement = lifecycleRequirement
    .with("id", "REQ-SUCCESSION-R2")
    .with("acceptanceCriteria", [
      { id: "AC-SUCCESSION-R2", given: "R2 exists", when_: "R2 is superseded", expected: "the chain advances" }
    ])
    .with("status", "retired")
    .with("retirementReason", "superseded by R3")
    .with("supersededBy", "REQ-SUCCESSION-R3")
  pure val successionR3: Requirement = lifecycleRequirement
    .with("id", "REQ-SUCCESSION-R3")
    .with("acceptanceCriteria", [
      { id: "AC-SUCCESSION-R3", given: "R3 exists", when_: "the chain terminates", expected: "R3 is active" }
    ])
  pure val successionCycleR2: Requirement = successionR2
    .with("supersededBy", "REQ-SUCCESSION-R1")
  pure val successionRetiredTerminalR2: Requirement = successionR2
    .with("supersededBy", "")
  pure val successionCatalog: Catalog = {
    schemaVersion: 1,
    catalogRevision: 1,
    product: "succession-contract",
    updatedAt: "succession:fixture",
    requirements: [successionR1, successionR2, successionR3],
  }

  pure val batchRequirement1: Requirement = lifecycleRequirement
    .with("id", "REQ-BATCH-1")
    .with("acceptanceCriteria", [
      { id: "AC-BATCH-1", given: "batch source", when_: "item one changes", expected: "revision advances once" }
    ])
  pure val batchRequirement2: Requirement = lifecycleRequirement
    .with("id", "REQ-BATCH-2")
    .with("acceptanceCriteria", [
      { id: "AC-BATCH-2", given: "batch source", when_: "item two changes", expected: "revision advances once" }
    ])
  pure val batchRequirement3: Requirement = lifecycleRequirement
    .with("id", "REQ-BATCH-3")
    .with("acceptanceCriteria", [
      { id: "AC-BATCH-3", given: "batch source", when_: "item three changes", expected: "revision advances once" }
    ])
  pure val batchBefore: Catalog = {
    schemaVersion: 1,
    catalogRevision: 5,
    product: "batch-contract",
    updatedAt: "batch:before",
    requirements: [batchRequirement1, batchRequirement2, batchRequirement3],
  }
  pure val batchAfterTwo: Catalog = batchBefore
    .with("catalogRevision", 6)
    .with("updatedAt", "batch:two")
    .with("requirements", [
      batchRequirement1
        .with("revision", 2)
        .with("title", "batch item one updated")
        .with("lastChangedBy", "batch:change"),
      batchRequirement2
        .with("revision", 2)
        .with("traces", batchRequirement2.traces.with("tests", ["tests/batch-two.py"]))
        .with("lastChangedBy", "batch:change"),
      batchRequirement3,
    ])
  pure val batchAfterThree: Catalog = batchBefore
    .with("catalogRevision", 6)
    .with("updatedAt", "batch:three")
    .with("requirements", [
      batchAfterTwo.requirements.nth(0),
      batchAfterTwo.requirements.nth(1),
      batchRequirement3
        .with("revision", 2)
        .with("status", "retired")
        .with("retirementReason", "batch retirement")
        .with("lastChangedBy", "batch:change"),
    ])
  pure val batchStaleAfter: Catalog = batchAfterTwo.with("requirements", [
    batchRequirement1,
    batchAfterTwo.requirements.nth(1),
    batchRequirement3,
  ])
  pure val batchPartialAfterStale: Catalog = batchBefore
    .with("catalogRevision", 6)
    .with("updatedAt", "batch:stale-after-valid")
    .with("requirements", [
      batchAfterTwo.requirements.nth(0),
      batchRequirement2,
      batchRequirement3,
    ])
  pure val batchInvalidAfter: Catalog = batchAfterTwo.with("requirements", [
    batchAfterTwo.requirements.nth(0).with("title", ""),
    batchAfterTwo.requirements.nth(1),
    batchRequirement3,
  ])
  pure val batchUpdateOperation: RequirementOperation = {
    kind: "update",
    id: "REQ-BATCH-1",
    expectedRevision: 1,
    replacement: batchAfterTwo.requirements.nth(0),
  }
  pure val batchTraceOperation: RequirementOperation = {
    kind: "trace",
    id: "REQ-BATCH-2",
    expectedRevision: 1,
    replacement: batchAfterTwo.requirements.nth(1),
  }
  pure val batchRetireOperation: RequirementOperation = {
    kind: "retire",
    id: "REQ-BATCH-3",
    expectedRevision: 1,
    replacement: batchAfterThree.requirements.nth(2),
  }
  pure val batchStaleOperation: RequirementOperation = batchUpdateOperation
    .with("expectedRevision", 0)
  pure val batchStaleTraceOperation: RequirementOperation = batchTraceOperation
    .with("expectedRevision", 0)
  pure val batchInvalidOperation: RequirementOperation = batchUpdateOperation
    .with("replacement", batchInvalidAfter.requirements.nth(0))
  pure val batchResurrectionOperation: RequirementOperation = {
    kind: "update",
    id: "REQ-BATCH-3",
    expectedRevision: 2,
    replacement: batchAfterThree.requirements.nth(2)
      .with("revision", 3)
      .with("status", "active")
      .with("retirementReason", "")
      .with("lastChangedBy", "batch:change"),
  }
  pure val batchResurrectedAfter: Catalog = batchAfterThree
    .with("catalogRevision", 7)
    .with("updatedAt", "batch:resurrection")
    .with("requirements", batchAfterThree.requirements.replaceAt(
      2,
      batchResurrectionOperation.replacement
    ))

  var catalog: Catalog
  var lifecycle: Lifecycle

  action init = all {
    catalog' = requirementsSource,
    lifecycle' = {
      catalogRevision: requirementsSource.catalogRevision,
      itemRevision: 0,
      itemPresent: false,
      itemStatus: "missing",
      traceRevision: 0,
      priorCatalogRevision: requirementsSource.catalogRevision,
      priorItemRevision: 0,
      priorItemPresent: false,
      priorItemStatus: "missing",
      priorTraceRevision: 0,
      lastOperation: "init",
    },
  }

  action addRequirementAt(expectedCatalogRevision: int): bool = all {
    expectedCatalogRevision == catalog.catalogRevision,
    lifecycle.catalogRevision == expectedCatalogRevision,
    not(lifecycle.itemPresent),
    catalog.requirements.indices().forall(i =>
      catalog.requirements.nth(i).id != lifecycleRequirement.id
    ),
    catalog' = catalog
      .with("catalogRevision", catalog.catalogRevision + 1)
      .with("requirements", catalog.requirements.append(lifecycleRequirement)),
    lifecycle' = {
      catalogRevision: lifecycle.catalogRevision + 1,
      itemRevision: 1,
      itemPresent: true,
      itemStatus: "active",
      traceRevision: 0,
      priorCatalogRevision: lifecycle.catalogRevision,
      priorItemRevision: lifecycle.itemRevision,
      priorItemPresent: lifecycle.itemPresent,
      priorItemStatus: lifecycle.itemStatus,
      priorTraceRevision: lifecycle.traceRevision,
      lastOperation: "add",
    },
  }

  action addRequirement = addRequirementAt(lifecycle.catalogRevision)

  def updateRequirementIsAllowed(expectedCatalogRevision: int, expectedItemRevision: int): bool =
    all {
      lifecycle.itemPresent,
      lifecycle.itemStatus == "active",
      expectedCatalogRevision == catalog.catalogRevision,
      expectedCatalogRevision == lifecycle.catalogRevision,
      expectedItemRevision == lifecycle.itemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).id == lifecycleRequirement.id,
      catalog.requirements.nth(catalog.requirements.length() - 1).revision == expectedItemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).status == "active",
      catalog.requirements.nth(catalog.requirements.length() - 1).title != "lifecycle fixture updated",
    }

  action updateRequirementAt(expectedCatalogRevision: int, expectedItemRevision: int): bool = all {
    updateRequirementIsAllowed(expectedCatalogRevision, expectedItemRevision),
    catalog' = catalog
      .with("catalogRevision", catalog.catalogRevision + 1)
      .with(
        "requirements",
        catalog.requirements.replaceAt(
          catalog.requirements.length() - 1,
          catalog.requirements.nth(catalog.requirements.length() - 1)
            .with("revision", expectedItemRevision + 1)
            .with("title", "lifecycle fixture updated")
            .with("lastChangedBy", "model:update")
        )
      ),
    lifecycle' = {
      catalogRevision: lifecycle.catalogRevision + 1,
      itemRevision: lifecycle.itemRevision + 1,
      itemPresent: true,
      itemStatus: "active",
      traceRevision: lifecycle.traceRevision,
      priorCatalogRevision: lifecycle.catalogRevision,
      priorItemRevision: lifecycle.itemRevision,
      priorItemPresent: lifecycle.itemPresent,
      priorItemStatus: lifecycle.itemStatus,
      priorTraceRevision: lifecycle.traceRevision,
      lastOperation: "update",
    },
  }

  action updateRequirement = updateRequirementAt(lifecycle.catalogRevision, lifecycle.itemRevision)

  def traceUpdateIsAllowed(expectedCatalogRevision: int, expectedItemRevision: int): bool =
    all {
      lifecycle.itemPresent,
      lifecycle.itemStatus == "active",
      lifecycle.traceRevision == 0,
      expectedCatalogRevision == catalog.catalogRevision,
      expectedCatalogRevision == lifecycle.catalogRevision,
      expectedItemRevision == lifecycle.itemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).id == lifecycleRequirement.id,
      catalog.requirements.nth(catalog.requirements.length() - 1).revision == expectedItemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).status == "active",
    }

  action updateRequirementTraceAt(expectedCatalogRevision: int, expectedItemRevision: int): bool = all {
    traceUpdateIsAllowed(expectedCatalogRevision, expectedItemRevision),
    catalog' = catalog
      .with("catalogRevision", catalog.catalogRevision + 1)
      .with(
        "requirements",
        catalog.requirements.replaceAt(
          catalog.requirements.length() - 1,
          catalog.requirements.nth(catalog.requirements.length() - 1)
            .with("revision", expectedItemRevision + 1)
            .with(
              "traces",
              catalog.requirements.nth(catalog.requirements.length() - 1).traces.with(
                "tests",
                catalog.requirements.nth(catalog.requirements.length() - 1).traces.tests
                  .append("tests/model-trace-update.py")
              )
            )
            .with("lastChangedBy", "model:trace-update")
        )
      ),
    lifecycle' = {
      catalogRevision: lifecycle.catalogRevision + 1,
      itemRevision: lifecycle.itemRevision + 1,
      itemPresent: true,
      itemStatus: "active",
      traceRevision: lifecycle.traceRevision + 1,
      priorCatalogRevision: lifecycle.catalogRevision,
      priorItemRevision: lifecycle.itemRevision,
      priorItemPresent: lifecycle.itemPresent,
      priorItemStatus: lifecycle.itemStatus,
      priorTraceRevision: lifecycle.traceRevision,
      lastOperation: "trace-update",
    },
  }

  action updateRequirementTrace =
    updateRequirementTraceAt(lifecycle.catalogRevision, lifecycle.itemRevision)

  def retirementIsAllowed(expectedCatalogRevision: int, expectedItemRevision: int): bool =
    all {
      lifecycle.itemPresent,
      lifecycle.itemStatus == "active",
      expectedCatalogRevision == catalog.catalogRevision,
      expectedCatalogRevision == lifecycle.catalogRevision,
      expectedItemRevision == lifecycle.itemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).id == lifecycleRequirement.id,
      catalog.requirements.nth(catalog.requirements.length() - 1).revision == expectedItemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).status == "active",
    }

  action retireRequirementAt(expectedCatalogRevision: int, expectedItemRevision: int): bool = all {
    retirementIsAllowed(expectedCatalogRevision, expectedItemRevision),
    catalog' = catalog
      .with("catalogRevision", catalog.catalogRevision + 1)
      .with(
        "requirements",
        catalog.requirements.replaceAt(
          catalog.requirements.length() - 1,
          catalog.requirements.nth(catalog.requirements.length() - 1)
            .with("revision", expectedItemRevision + 1)
            .with("status", "retired")
            .with("retirementReason", "model retirement")
            .with("lastChangedBy", "model:retire")
        )
      ),
    lifecycle' = {
      catalogRevision: lifecycle.catalogRevision + 1,
      itemRevision: lifecycle.itemRevision + 1,
      itemPresent: true,
      itemStatus: "retired",
      traceRevision: lifecycle.traceRevision,
      priorCatalogRevision: lifecycle.catalogRevision,
      priorItemRevision: lifecycle.itemRevision,
      priorItemPresent: lifecycle.itemPresent,
      priorItemStatus: lifecycle.itemStatus,
      priorTraceRevision: lifecycle.traceRevision,
      lastOperation: "retire",
    },
  }

  action retireRequirement = retireRequirementAt(lifecycle.catalogRevision, lifecycle.itemRevision)

  action lifecycleStutter = all {
    catalog' = catalog,
    lifecycle' = {
      catalogRevision: lifecycle.catalogRevision,
      itemRevision: lifecycle.itemRevision,
      itemPresent: lifecycle.itemPresent,
      itemStatus: lifecycle.itemStatus,
      traceRevision: lifecycle.traceRevision,
      priorCatalogRevision: lifecycle.catalogRevision,
      priorItemRevision: lifecycle.itemRevision,
      priorItemPresent: lifecycle.itemPresent,
      priorItemStatus: lifecycle.itemStatus,
      priorTraceRevision: lifecycle.traceRevision,
      lastOperation: "none",
    },
  }

  action counterOnlyMutation = all {
    catalog' = catalog,
    lifecycle' = lifecycle.with("catalogRevision", lifecycle.catalogRevision + 1),
  }

  action step = any {
    addRequirement,
    updateRequirement,
    updateRequirementTrace,
    retireRequirement,
    lifecycleStutter,
  }

  pure val allowedStatuses = Set("active", "retired")
  pure val allowedKinds = Set("functional", "quality", "constraint", "interface", "data", "operational")
  pure val allowedScopes = Set("product", "project")
  pure val allowedCategories = Set("functional", "nonfunctional")
  pure val allowedActions = Set(
    "constrain", "derive", "detect", "discover", "enable", "enforce", "estimate",
    "expand", "formalize", "generate", "maintain", "measure", "parse", "preserve",
    "provide", "route", "select", "separate", "stage", "stop", "structure", "validate", "verify"
  )

  pure def stringsAreUnique(values: List[str]): bool = values.indices().forall(i =>
    values.indices().forall(j => i == j or values.nth(i) != values.nth(j))
  )

  pure def stringsAreNonempty(values: List[str]): bool =
    values.indices().forall(i => values.nth(i) != "")

  pure def requirementIdsAreUniqueIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i =>
      requirements.indices().forall(j =>
        i == j or requirements.nth(i).id != requirements.nth(j).id
      )
    )

  val requirementIdsAreUnique = requirementIdsAreUniqueIn(catalog.requirements)

  // 構造的完全性は機械検査する。1 IDが意味的に1義務だけを表すかは、
  // 自然言語を解釈できる権限あるhuman semantic reviewの責務である。
  pure def requirementsAreStructurallyCompleteIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i => all {
      requirements.nth(i).id != "",
      requirements.nth(i).revision >= 1,
      requirements.nth(i).title != "",
      requirements.nth(i).subject != "",
      requirements.nth(i).actionName != "",
      requirements.nth(i).objectName != "",
      requirements.nth(i).rationale != "",
      requirements.nth(i).lastChangedBy != "",
      requirements.nth(i).sourceRefs.length() > 0,
      stringsAreNonempty(requirements.nth(i).sourceRefs),
      stringsAreUnique(requirements.nth(i).sourceRefs),
      requirements.nth(i).acceptanceCriteria.length() > 0,
      requirements.nth(i).verification.method != "",
      requirements.nth(i).verification.evidence != "",
    })

  val requirementsAreStructurallyComplete =
    requirementsAreStructurallyCompleteIn(catalog.requirements)

  pure def requirementsAreTypedIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i => all {
      allowedStatuses.contains(requirements.nth(i).status),
      allowedKinds.contains(requirements.nth(i).kind),
      allowedActions.contains(requirements.nth(i).actionName),
      (requirements.nth(i).scopeName == "").or(allowedScopes.contains(requirements.nth(i).scopeName)),
      (requirements.nth(i).categoryName == "").or(allowedCategories.contains(requirements.nth(i).categoryName)),
    })

  val requirementsAreTyped = requirementsAreTypedIn(catalog.requirements)

  pure def acceptanceCriteriaAreCompleteIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i =>
      requirements.nth(i).acceptanceCriteria.indices().forall(j => all {
        requirements.nth(i).acceptanceCriteria.nth(j).id != "",
        requirements.nth(i).acceptanceCriteria.nth(j).given != "",
        requirements.nth(i).acceptanceCriteria.nth(j).when_ != "",
        requirements.nth(i).acceptanceCriteria.nth(j).expected != "",
      })
    )

  val acceptanceCriteriaAreComplete =
    acceptanceCriteriaAreCompleteIn(catalog.requirements)

  pure def acceptanceCriterionIdsAreUniqueIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i =>
      requirements.indices().forall(j =>
        requirements.nth(i).acceptanceCriteria.indices().forall(x =>
          requirements.nth(j).acceptanceCriteria.indices().forall(y =>
          (i == j and x == y) or
            requirements.nth(i).acceptanceCriteria.nth(x).id !=
              requirements.nth(j).acceptanceCriteria.nth(y).id
          )
        )
      )
    )

  val acceptanceCriterionIdsAreUnique =
    acceptanceCriterionIdsAreUniqueIn(catalog.requirements)

  pure def traceLinksAreUniqueIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i => all {
      stringsAreNonempty(requirements.nth(i).traces.design),
      stringsAreNonempty(requirements.nth(i).traces.implementation),
      stringsAreNonempty(requirements.nth(i).traces.tests),
      stringsAreNonempty(requirements.nth(i).traces.standards),
      stringsAreUnique(requirements.nth(i).traces.design),
      stringsAreUnique(requirements.nth(i).traces.implementation),
      stringsAreUnique(requirements.nth(i).traces.tests),
      stringsAreUnique(requirements.nth(i).traces.standards),
    })

  val traceLinksAreUnique = traceLinksAreUniqueIn(catalog.requirements)

  pure def classificationIsPairedIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i =>
      (requirements.nth(i).scopeName == "") iff
      (requirements.nth(i).categoryName == "")
    )

  val classificationIsPaired = classificationIsPairedIn(catalog.requirements)

  pure def retirementFieldsAreConsistentIn(requirements: List[Requirement]): bool =
    requirements.indices().forall(i => all {
    (requirements.nth(i).status == "active").implies(all {
      requirements.nth(i).retirementReason == "",
      requirements.nth(i).supersededBy == "",
    }),
    (requirements.nth(i).status == "retired").implies(
      requirements.nth(i).retirementReason != ""
    ),
    (requirements.nth(i).supersededBy != "").implies(all {
      requirements.nth(i).status == "retired",
      requirements.nth(i).supersededBy != requirements.nth(i).id,
    }),
  })

  val retirementFieldsAreConsistent =
    retirementFieldsAreConsistentIn(catalog.requirements)

  pure def supersessionChainsAreValid(requirements: List[Requirement]): bool =
    requirements.indices().forall(i =>
      (requirements.nth(i).supersededBy != "").implies(
        requirements.indices().exists(j => all {
          j > i,
          requirements.nth(j).id == requirements.nth(i).supersededBy,
          requirements.nth(j).id != requirements.nth(i).id,
          (requirements.nth(j).status == "active").or(all {
            requirements.nth(j).status == "retired",
            requirements.nth(j).supersededBy != "",
          }),
        })
      )
    )

  pure def catalogHeaderIsValid(source: Catalog): bool = all {
    source.schemaVersion == 1,
    source.catalogRevision >= 1,
    source.product != "",
    source.updatedAt != "",
    source.requirements.length() > 0,
  }

  // Pure catalog component of catalogWellFormed. Lifecycle witness refinement
  // remains a state invariant below and is intentionally not fabricated for a
  // caller-supplied batch result.
  pure def catalogDataWellFormed(source: Catalog): bool = all {
    catalogHeaderIsValid(source),
    requirementIdsAreUniqueIn(source.requirements),
    requirementsAreStructurallyCompleteIn(source.requirements),
    requirementsAreTypedIn(source.requirements),
    acceptanceCriteriaAreCompleteIn(source.requirements),
    acceptanceCriterionIdsAreUniqueIn(source.requirements),
    traceLinksAreUniqueIn(source.requirements),
    classificationIsPairedIn(source.requirements),
    retirementFieldsAreConsistentIn(source.requirements),
    supersessionChainsAreValid(source.requirements),
  }

  pure def stringsContain(values: List[str], value: str): bool =
    values.indices().exists(i => values.nth(i) == value)

  pure def requirementExists(requirements: List[Requirement], id: str): bool =
    requirements.indices().exists(i => requirements.nth(i).id == id)

  pure def requirementById(requirements: List[Requirement], id: str): Requirement =
    requirements.select(requirement => requirement.id == id).head()

  pure def replaceRequirement(
    requirements: List[Requirement],
    id: str,
    replacement: Requirement,
  ): List[Requirement] =
    range(0, requirements.length()).foldl(requirements, (result, index) =>
      if (result.nth(index).id == id)
        result.replaceAt(index, replacement)
      else
        result
    )

  pure def updateReplacementIsValid(
    current: Requirement,
    replacement: Requirement,
    changeId: str,
  ): bool = all {
    current.status == "active",
    replacement == current
      .with("revision", current.revision + 1)
      .with("kind", replacement.kind)
      .with("title", replacement.title)
      .with("subject", replacement.subject)
      .with("actionName", replacement.actionName)
      .with("objectName", replacement.objectName)
      .with("rationale", replacement.rationale)
      .with("sourceRefs", replacement.sourceRefs)
      .with("acceptanceCriteria", replacement.acceptanceCriteria)
      .with("verification", replacement.verification)
      .with("scopeName", replacement.scopeName)
      .with("categoryName", replacement.categoryName)
      .with("lastChangedBy", changeId),
    replacement
      .with("revision", current.revision)
      .with("lastChangedBy", current.lastChangedBy) != current,
  }

  pure def traceReplacementIsValid(
    current: Requirement,
    replacement: Requirement,
    changeId: str,
  ): bool = all {
    current.status == "active",
    replacement.traces != current.traces,
    replacement == current
      .with("revision", current.revision + 1)
      .with("traces", replacement.traces)
      .with("lastChangedBy", changeId),
  }

  pure def retirementReplacementIsValid(
    current: Requirement,
    replacement: Requirement,
    changeId: str,
  ): bool = all {
    current.status == "active",
    replacement.retirementReason != "",
    replacement == current
      .with("revision", current.revision + 1)
      .with("status", "retired")
      .with("retirementReason", replacement.retirementReason)
      .with("supersededBy", replacement.supersededBy)
      .with("lastChangedBy", changeId),
  }

  pure def batchOperationIsAllowed(
    accumulator: BatchFold,
    operation: RequirementOperation,
    changeId: str,
  ): bool =
    if (not(accumulator.valid)) false
    else if (stringsContain(accumulator.touchedIds, operation.id)) false
    else if (operation.kind == "add") all {
      not(requirementExists(accumulator.requirements, operation.id)),
      operation.expectedRevision == 0,
      operation.id == operation.replacement.id,
      operation.replacement.revision == 1,
      operation.replacement.status == "active",
      operation.replacement.retirementReason == "",
      operation.replacement.supersededBy == "",
      operation.replacement.lastChangedBy == changeId,
    }
    else if (not(requirementExists(accumulator.requirements, operation.id))) false
    else if (
      operation.expectedRevision !=
        requirementById(accumulator.requirements, operation.id).revision
    ) false
    else if (operation.kind == "update") updateReplacementIsValid(
      requirementById(accumulator.requirements, operation.id),
      operation.replacement,
      changeId
    )
    else if (operation.kind == "trace") traceReplacementIsValid(
      requirementById(accumulator.requirements, operation.id),
      operation.replacement,
      changeId
    )
    else if (operation.kind == "retire") retirementReplacementIsValid(
      requirementById(accumulator.requirements, operation.id),
      operation.replacement,
      changeId
    )
    else false

  pure def applyBatchOperation(
    accumulator: BatchFold,
    operation: RequirementOperation,
    changeId: str,
  ): BatchFold =
    if (batchOperationIsAllowed(accumulator, operation, changeId)) {
      requirements:
        if (operation.kind == "add")
          accumulator.requirements.append(operation.replacement)
        else
          replaceRequirement(accumulator.requirements, operation.id, operation.replacement),
      touchedIds: accumulator.touchedIds.append(operation.id),
      valid: true,
    } else accumulator.with("valid", false)

  pure def initialBatchFold(before: Catalog): BatchFold = {
    requirements: before.requirements,
    touchedIds: [],
    valid: true,
  }

  pure def foldBatchOperations(
    before: Catalog,
    operations: List[RequirementOperation],
    changeId: str,
  ): BatchFold = operations.foldl(
    initialBatchFold(before),
    (accumulator, operation) => applyBatchOperation(accumulator, operation, changeId)
  )

  pure def batchCandidate(
    before: Catalog,
    operations: List[RequirementOperation],
    changedAt: str,
    changeId: str,
  ): Catalog = before
    .with("catalogRevision", before.catalogRevision + 1)
    .with("updatedAt", changedAt)
    .with("requirements", foldBatchOperations(before, operations, changeId).requirements)

  pure def batchWouldBeAccepted(
    before: Catalog,
    expectedCatalogRevision: int,
    operations: List[RequirementOperation],
    changedAt: str,
    changeId: str,
  ): bool = all {
    expectedCatalogRevision == before.catalogRevision,
    operations.length() > 0,
    changedAt != "",
    changeId != "",
    foldBatchOperations(before, operations, changeId).valid,
    catalogDataWellFormed(batchCandidate(before, operations, changedAt, changeId)),
  }

  // This relation models the same arbitrary-length operation fold and CAS
  // boundary as specflow.apply_change. No operation may resurrect a retired
  // item, and any stale or invalid member makes the entire batch stutter.
  pure def atomicBatchTransitionIsValid(
    before: Catalog,
    after: Catalog,
    expectedCatalogRevision: int,
    operations: List[RequirementOperation],
    changedAt: str,
    changeId: str,
    outcome: str,
  ): bool = all {
    Set("accepted", "rejected").contains(outcome),
    catalogDataWellFormed(before),
    (outcome == "accepted") iff batchWouldBeAccepted(
      before, expectedCatalogRevision, operations, changedAt, changeId
    ),
    (outcome == "accepted").implies(
      after == batchCandidate(before, operations, changedAt, changeId)
    ),
    (outcome == "rejected").implies(after == before),
  }

  val lifecycleRevisionTransitionIsSound = all {
    Set("init", "add", "update", "trace-update", "retire", "none").contains(lifecycle.lastOperation),
    (lifecycle.lastOperation == "init").implies(all {
      lifecycle.catalogRevision == requirementsSource.catalogRevision,
      lifecycle.itemRevision == 0,
      not(lifecycle.itemPresent),
    }),
    (lifecycle.lastOperation == "add").implies(all {
      not(lifecycle.priorItemPresent),
      lifecycle.itemPresent,
      lifecycle.itemStatus == "active",
      lifecycle.catalogRevision == lifecycle.priorCatalogRevision + 1,
      lifecycle.itemRevision == 1,
    }),
    (lifecycle.lastOperation == "update").implies(all {
      lifecycle.priorItemPresent,
      lifecycle.priorItemStatus == "active",
      lifecycle.itemStatus == "active",
      lifecycle.catalogRevision == lifecycle.priorCatalogRevision + 1,
      lifecycle.itemRevision == lifecycle.priorItemRevision + 1,
      lifecycle.traceRevision == lifecycle.priorTraceRevision,
    }),
    (lifecycle.lastOperation == "trace-update").implies(all {
      lifecycle.priorItemPresent,
      lifecycle.priorItemStatus == "active",
      lifecycle.itemStatus == "active",
      lifecycle.catalogRevision == lifecycle.priorCatalogRevision + 1,
      lifecycle.itemRevision == lifecycle.priorItemRevision + 1,
      lifecycle.traceRevision == lifecycle.priorTraceRevision + 1,
    }),
    (lifecycle.lastOperation == "retire").implies(all {
      lifecycle.priorItemPresent,
      lifecycle.priorItemStatus == "active",
      lifecycle.itemPresent,
      lifecycle.itemStatus == "retired",
      lifecycle.catalogRevision == lifecycle.priorCatalogRevision + 1,
      lifecycle.itemRevision == lifecycle.priorItemRevision + 1,
      lifecycle.traceRevision == lifecycle.priorTraceRevision,
    }),
    (lifecycle.lastOperation == "none").implies(all {
      lifecycle.catalogRevision == lifecycle.priorCatalogRevision,
      lifecycle.itemRevision == lifecycle.priorItemRevision,
      lifecycle.itemPresent == lifecycle.priorItemPresent,
      lifecycle.itemStatus == lifecycle.priorItemStatus,
      lifecycle.traceRevision == lifecycle.priorTraceRevision,
    }),
  }

  val lifecycleRefinesCatalog = all {
    lifecycle.catalogRevision == catalog.catalogRevision,
    lifecycle.itemPresent iff
      catalog.requirements.indices().exists(i =>
        catalog.requirements.nth(i).id == lifecycleRequirement.id
      ),
    lifecycle.itemPresent.implies(all {
      catalog.requirements.nth(catalog.requirements.length() - 1).id == lifecycleRequirement.id,
      catalog.requirements.nth(catalog.requirements.length() - 1).revision == lifecycle.itemRevision,
      catalog.requirements.nth(catalog.requirements.length() - 1).status == lifecycle.itemStatus,
      (lifecycle.traceRevision == 0).implies(
        catalog.requirements.nth(catalog.requirements.length() - 1).traces.tests ==
          lifecycleRequirement.traces.tests
      ),
      (lifecycle.traceRevision == 1).implies(
        catalog.requirements.nth(catalog.requirements.length() - 1).traces.tests ==
          lifecycleRequirement.traces.tests.append("tests/model-trace-update.py")
      ),
    }),
  }

  val catalogWellFormed = all {
    catalogDataWellFormed(catalog),
    lifecycleRevisionTransitionIsSound,
    lifecycleRefinesCatalog,
  }

  run catalogContractTest = {
    init.then(all {
      assert(catalogWellFormed),
      catalog' = catalog,
      lifecycle' = lifecycle,
    })
  }

  run catalogAndSupersessionMutationRejectionTest = {
    init.then(all {
      assert(not(catalogHeaderIsValid(catalog.with("requirements", [])))),
      assert(catalogDataWellFormed(successionCatalog)),
      assert(supersessionChainsAreValid([successionR1, successionR2, successionR3])),
      assert(not(catalogDataWellFormed(successionCatalog.with("requirements", [successionR1])))),
      assert(not(catalogDataWellFormed(successionCatalog.with("requirements", [successionR1, successionRetiredTerminalR2])))),
      assert(not(catalogDataWellFormed(successionCatalog.with("requirements", [successionR1, successionCycleR2])))),
      assert(not(supersessionChainsAreValid([successionR1]))),
      assert(not(supersessionChainsAreValid([successionR1, successionRetiredTerminalR2]))),
      assert(not(supersessionChainsAreValid([successionR1, successionCycleR2]))),
      catalog' = catalog,
      lifecycle' = lifecycle,
    })
  }

  run atomicBatchTransitionContractTest = {
    init.then(all {
      assert(atomicBatchTransitionIsValid(batchBefore, batchAfterTwo, 5, [batchUpdateOperation, batchTraceOperation], "batch:two", "batch:change", "accepted")),
      assert(atomicBatchTransitionIsValid(batchBefore, batchAfterThree, 5, [batchUpdateOperation, batchTraceOperation, batchRetireOperation], "batch:three", "batch:change", "accepted")),
      assert(atomicBatchTransitionIsValid(batchBefore, batchBefore, 4, [batchUpdateOperation], "batch:stale-catalog", "batch:change", "rejected")),
      assert(atomicBatchTransitionIsValid(batchBefore, batchBefore, 5, [batchStaleOperation], "batch:stale-item", "batch:change", "rejected")),
      assert(atomicBatchTransitionIsValid(batchBefore, batchBefore, 5, [batchUpdateOperation, batchStaleTraceOperation], "batch:stale-after-valid", "batch:change", "rejected")),
      assert(not(atomicBatchTransitionIsValid(batchBefore, batchPartialAfterStale, 5, [batchUpdateOperation, batchStaleTraceOperation], "batch:stale-after-valid", "batch:change", "accepted"))),
      assert(atomicBatchTransitionIsValid(batchBefore, batchBefore, 5, [batchUpdateOperation, batchUpdateOperation], "batch:duplicate", "batch:change", "rejected")),
      assert(atomicBatchTransitionIsValid(batchBefore, batchBefore, 5, [batchInvalidOperation], "batch:invalid", "batch:change", "rejected")),
      assert(not(atomicBatchTransitionIsValid(batchBefore, batchInvalidAfter, 5, [batchInvalidOperation], "batch:invalid", "batch:change", "accepted"))),
      assert(catalogDataWellFormed(batchResurrectedAfter)),
      assert(atomicBatchTransitionIsValid(batchAfterThree, batchAfterThree, 6, [batchResurrectionOperation], "batch:resurrection", "batch:change", "rejected")),
      assert(not(atomicBatchTransitionIsValid(batchAfterThree, batchResurrectedAfter, 6, [batchResurrectionOperation], "batch:resurrection", "batch:change", "accepted"))),
      catalog' = catalog,
      lifecycle' = lifecycle,
    })
  }

  run lifecycleContractTest = {
    init
      .then(addRequirement)
      .then(updateRequirement)
      .then(updateRequirementTrace)
      .then(retireRequirement)
      .then(all {
        assert(catalogWellFormed),
        assert(lifecycleRefinesCatalog),
        assert(not(updateRequirementIsAllowed(catalog.catalogRevision, lifecycle.itemRevision))),
        assert(not(traceUpdateIsAllowed(catalog.catalogRevision, lifecycle.itemRevision))),
        catalog' = catalog,
        lifecycle' = lifecycle,
      })
  }

  run lifecycleCasRejectionTest = {
    init
      .then(addRequirement)
      .then(all {
        assert(not(updateRequirementIsAllowed(catalog.catalogRevision - 1, lifecycle.itemRevision))),
        assert(not(updateRequirementIsAllowed(catalog.catalogRevision, lifecycle.itemRevision - 1))),
        catalog' = catalog,
        lifecycle' = lifecycle,
      })
  }


  run refinementRejectsCounterOnlyMutationTest = {
    init
      .then(counterOnlyMutation)
      .then(all {
        assert(not(lifecycleRefinesCatalog)),
        catalog' = catalog,
        lifecycle' = lifecycle,
      })
  }
}
