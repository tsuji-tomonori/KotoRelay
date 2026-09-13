"""save_draftの入力制約と応答型を定義する。"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field, StringConstraints

from kotorelay.schemas import Input, Placement


class SaveDraft(Input):
    # 本文先頭の空白と末尾改行はMarkdownと配置offsetの一部として保存する。
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
    body: str = Field(max_length=100_000)
    revision: int = Field(ge=1)
    placements: list[Placement] = Field(default_factory=list, max_length=10)


type ResponseData = dict[str, object]
