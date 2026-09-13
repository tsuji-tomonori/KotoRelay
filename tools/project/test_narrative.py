"""テストのdocstringから人が読む検証単位を取得し、欠落は生成失敗にする。"""

import re


def parse(doc: str | None, location: str) -> dict[str, str]:
    values = {}
    for line in (doc or "").splitlines():
        match = re.fullmatch(r"\s*(Given|When|Then):\s*(.+)", line)
        if match:
            key, value = match.groups()
            if key.lower() in values:
                raise ValueError(f"テスト説明の重複: {location}: {key}")
            if not re.search(r"[ぁ-んァ-ヶ一-龠]", value) or len(value) < 8:
                raise ValueError(f"日本語の検証意図が必要: {location}: {key}")
            values[key.lower()] = value
    if set(values) != {"given", "when", "then"}:
        raise ValueError(f"Given/When/Thenの日本語説明が欠落: {location}")
    return values
