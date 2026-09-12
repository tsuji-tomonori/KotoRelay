"""DDLを一つずつ適用する。AWSでは事前にadmin接続を明示する。"""

from __future__ import annotations

import argparse
from pathlib import Path

from kotorelay.config import Settings
from kotorelay.db import Database


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path("backend/migrations"))
    args = parser.parse_args()
    settings = Settings()
    with Database(settings).connect() as connection:
        connection.autocommit = True
        for path in sorted(args.directory.glob("*.sql")):
            # 新規環境の構築専用。再適用時の既存テーブルは成功へ読み替えない。
            connection.execute(path.read_text())
            print(f"適用: {path.name}")


if __name__ == "__main__":
    main()
