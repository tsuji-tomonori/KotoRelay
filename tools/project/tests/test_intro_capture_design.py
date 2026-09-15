"""収録設計の読み取り専用生成と欠落・差分検出を確認する。"""

import shutil
import subprocess
from pathlib import Path


def test_収録設計の合成は既存ファイルを修復せず差分を検出する(tmp_path):
    root = Path(__file__).resolve().parents[3]
    for name in (
        "tools/video/design.mjs",
        "tools/video/capture-intro.mjs",
        ".github/workflows/intro-capture.yml",
    ):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, target)
    output = tmp_path / "docs/design/generated/INTRO-CAPTURE.md"
    output.parent.mkdir(parents=True)

    def generate(*args):
        return subprocess.run(
            [shutil.which("node") or "/usr/bin/node", "tools/video/design.mjs", *args],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )

    # 総合生成用のstdoutは欠落を勝手に補完しない。
    expected = generate("--stdout")
    assert expected.returncode == 0
    assert "出力と検証" in expected.stdout
    assert not output.exists()
    assert generate("--check").returncode != 0
    assert generate().returncode == 0
    assert output.read_text() == expected.stdout
    assert generate("--check").returncode == 0

    # 既存生成物の破損と入力実装の変更をそれぞれ検出する。
    output.write_text("古い設計\n")
    assert generate("--stdout").stdout == expected.stdout
    assert output.read_text() == "古い設計\n"
    assert generate("--check").returncode != 0
    output.write_text(expected.stdout)
    source = tmp_path / "tools/video/capture-intro.mjs"
    source.write_text(source.read_text() + "\n// 収録条件の変更\n")
    assert generate("--check").returncode != 0
    assert generate("--stdout").stdout != expected.stdout
