"""Refuse a plnr source file longer than the limit: a long file is several files wearing a hat.

    python tools/check_plnr_file_length.py            # every source file of the engine
    python tools/check_plnr_file_length.py FILE ...   # only these

The engine (src/plnr) came from its own repo with its own rule: lines per file, not pron's
code-lines rule of tools/check_file_length.py. It keeps it, over its own files only.

The limit is per file, counted in lines; the same check runs as a test, so a long file
never reaches a commit green.
"""

from __future__ import annotations

import sys
from pathlib import Path

LIMIT = 400
ROOT = Path(__file__).resolve().parent.parent
DIRS = ("src/plnr", "tests/plnr_engine", "examples/plnr")


def source_files(roots: list[str]) -> list[Path]:
    if roots:
        return [Path(r) for r in roots]
    out: list[Path] = []
    for d in DIRS:
        out.extend(sorted((ROOT / d).rglob("*.py")))
    out.append(Path(__file__).resolve())
    return out


def too_long(path: Path, limit: int = LIMIT) -> int | None:
    lines = len(path.read_text(encoding="utf-8").splitlines())
    return lines if lines > limit else None


def main(argv: list[str]) -> int:
    bad = []
    for path in source_files(argv):
        lines = too_long(path)
        if lines is not None:
            bad.append(f"{path}: {lines} lines (limit {LIMIT})")
    for line in bad:
        print(line)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
