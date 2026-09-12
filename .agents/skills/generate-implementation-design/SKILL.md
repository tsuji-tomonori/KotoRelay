---
name: generate-implementation-design
description: Deterministically generate as-built design from implementation artifacts and check that generated documentation still matches the implementation.
---

# Generate Implementation Design

形式契約: `spec/skills/skills.qnt`の`name: "generate-implementation-design"`（保守・監査時に参照）。

実装から現在状態の設計を決定的に生成する。これは2本目のガードレールである。

Dev標準の導入時と、現在状態の設計に影響する実装変更時に起動する。generator未宣言・未接続をno-opの理由にしない。初回または生成不足なら[adoption.md](references/adoption.md)を読み、対象棚卸し、generator/adapter接続、必要なMarkdown生成、欠落・drift検査まで実施する。実装がない領域だけを非該当とし、必要領域の未生成は導入未完了として扱う。

## Authority order

1. `spec/requirements/requirements.qnt`は意図した挙動を定義する。
2. 実装artifactは実装済み構造とinterfaceを定義する。
3. `docs/design/generated/`の生成設計は実装artifactを説明し、digestを持つ。
4. 不一致は欠陥であり、生成文書を直接編集して隠さない。

出力はgeneratorが完全所有するpathに限定し、symlink、directory置換、管理外pathへの出力を拒否する。

APIを持つ場合は[APIの6帳票契約](references/api-documents.md)を適用し、全operationの詳細設計・OpenAPI interface・ログmessage・query・Mermaid sequence・要因別unit-test詳細を生成する。必須要因／要素から実在テストへの欠落を解消し、6帳票の集合とdriftを検査する。

## FastAPI

- route AST、applicationが生成するOpenAPI、handler metadata、error branch、SQL ASTから設計を生成する。
- executable SQLを正規表現で推測せず、parseできないSQLを拒否する。
- 作成または再編時は`references/fastapi-contract.md`を読む。
- SQLがある導入・実装変更では[sql-and-language.md](references/sql-and-language.md)に従い、API別SQL、DDL/SQL由来の型付きquery生成と境界検査を接続する。説明コメントと生成ヘッダーは原則日本語とし、英語が残る生成物は生成元から修正する。
- 実行例: `python tools/portable_python.py run <host-skill-path>/scripts/designflow.py -- fastapi --source-root <src> --openapi <openapi.json> --sql-root <sql> --requirements <requirements.json> --trace <trace.json> --test-root <tests> --out docs/design/generated/fastapi`

## AWS CDK

- synth後のCloudFormation templateからresource、parameter、template SHA-256を生成する。
- 作成または再編時は`references/cdk-contract.md`を読む。
- 実行例: `python tools/portable_python.py run <host-skill-path>/scripts/designflow.py -- cdk --template <template.yaml> --requirements <requirements.json> --trace <trace.json> --test-root <tests> --out docs/design/generated/cdk/<stack>`

## Pinned Python runtime

初回だけ`python tools/portable_python.py setup`でmanifestに固定されたisolated runtimeを準備する。対象repositoryの既存venvやglobal packageを変更せず、`designflow.py`と`qualityflow.py`は常に`python tools/portable_python.py run <host-skill-path>/scripts/{designflow,qualityflow}.py -- <args...>`で実行する。`<host-skill-path>`はinstaller receiptとhost adapterが配置した、このSkillのhost-native rootへ解決し、特定hostのdirectory名を本文へ固定しない。

## Verification

1. generationが成功する。
2. 同じ入力の2回目の出力がbyte一致する。
3. `--check`が既存生成物との差を検出する。
4. canonical requirements JSON、明示的なartifact trace JSON、test sourceを入力する。trace JSONの`applicable_requirement_ids`は、generatorが扱う変更surfaceに関係するactive requirementだけを明示する。
5. `applicable_requirement_ids`とrequirement→operation / resource→実在test nodeのmappingを集合として完全一致させる。未知ID、inactive ID、未mapping ID、宣言外の余剰mappingを拒否し、実装から要件充足を推測して新しいtraceを捏造しない。
6. generator対象外の変更surfaceは、path、理由、support statusを持つstructured `unsupported_surface`として返し、必要な設計はproject adapterで補う。補完できなければ未完了であり、報告だけで完了へ進めない。generator対象内で未対応構文を検出した場合はpath、function、line、node kindを持つbounded diagnosticでfail-closedにする。どちらも未生成surfaceへ完全性を主張しない。

`--check`はローカルでも対象repositoryが既に持つCIでも実行できる。このSkillはCI workflow、required check、branch protection、merge ruleを作成も要求もしない。生成設計は実装との一致を示すが、実装が要件を満たすことまでは証明しない。

<!-- BEGIN GENERATED QUINT CONTRACT -->
## Quint contract（自動生成）

このblockは`spec/skills/skills.qnt`から自動生成し、直接編集しません。
詳細・要件trace・digestは`spec/skills/skills.json`の同名契約を、契約の保守・監査時だけ参照します。
repository policyは導入先が所有します。非該当ならartifactやblocking判定を作りません。

- Skill: `generate-implementation-design`
- 柱: design
- repository blocking: yes
- 既定portable: yes
- 適用条件: when-adopting-or-changing-implementation
- 起動context: `as-built-adoption-or-change`
- 外部作用capability: no
- Authority: implementation
- 副作用: repository-write
- 失敗状態: fail-on-missing-or-drift
<!-- END GENERATED QUINT CONTRACT -->
