"""Report files over the standards.md Layer 1 limit: code lines, not counting blanks,
comments, docstrings or imports. Exit 1 on any offender unless --report."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

LIMIT = 100


def _excluded_lines(tree: ast.Module) -> set[int]:
    lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            lines.update(range(node.lineno, node.end_lineno + 1))
        body = getattr(node, "body", None)
        if isinstance(body, list) and body and _is_docstring(body[0]):
            lines.update(range(body[0].lineno, body[0].end_lineno + 1))
    return lines


def _is_docstring(stmt: ast.stmt) -> bool:
    return isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str)


def code_lines(path: Path) -> int:
    source = path.read_text(encoding="utf-8")
    excluded = _excluded_lines(ast.parse(source))
    return sum(
        1
        for number, line in enumerate(source.splitlines(), start=1)
        if line.strip() and not line.strip().startswith("#") and number not in excluded
    )


def main(argv: list[str]) -> int:
    report_only = "--report" in argv
    roots = [Path(a) for a in argv if not a.startswith("--")] or [Path("src")]
    offenders = sorted(
        ((code_lines(p), p) for root in roots for p in root.rglob("*.py")),
        reverse=True,
    )
    offenders = [(n, p) for n, p in offenders if n > LIMIT]
    for n, p in offenders:
        print(f"{p}: {n} code lines (limit {LIMIT})")
    return 0 if report_only or not offenders else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
