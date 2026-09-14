"""S-expressions: pron's structured language (spec 06, 13). A move is a list of forms; the natural
language surface is a wrapper that resolves a sentence to these forms and evaluates them.

Only the reader and the printer live here; what each form means is in pron.forms.
Atoms are symbols (Sym), strings, integers, floats, and the symbols true, false and nil.
"""

from __future__ import annotations

import re
from typing import Any

TOKEN = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))')


class Sym(str):
    """A bare symbol: a form name, a relation, a model, a field."""

    def __repr__(self) -> str:
        return f"Sym({str.__repr__(self)})"


class SexpError(ValueError):
    pass


def read(text: str) -> list[Any]:
    """Every top-level expression in text, in order."""
    tokens: list[tuple[str, Any]] = []
    pos = 0
    text = text.strip()
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if m is None or m.end() == pos:
            raise SexpError(f"cannot read s-expression at {pos}: {text[pos:pos + 20]!r}")
        pos = m.end()
        if m.group(1):
            tokens.append(("(", None))
        elif m.group(2):
            tokens.append((")", None))
        elif m.group(3) is not None:
            tokens.append(("atom", _unescape(m.group(3))))
        elif m.group(4) is not None:
            tokens.append(("atom", _atom(m.group(4))))
        if pos < len(text) and text[pos:].strip() == "":
            break
    out, i = [], 0
    while i < len(tokens):
        expr, i = _parse(tokens, i)
        out.append(expr)
    return out


def read_one(text: str) -> Any:
    exprs = read(text)
    if len(exprs) != 1:
        raise SexpError(f"expected one s-expression, got {len(exprs)}")
    return exprs[0]


def write(expr: Any) -> str:
    if isinstance(expr, list):
        return "(" + " ".join(write(e) for e in expr) + ")"
    if isinstance(expr, Sym):
        return str(expr)
    if isinstance(expr, bool):
        return "true" if expr else "false"
    if expr is None:
        return "nil"
    if isinstance(expr, (int, float)):
        return repr(expr)
    return '"' + str(expr).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _parse(tokens: list[tuple[str, Any]], i: int) -> tuple[Any, int]:
    kind, value = tokens[i]
    if kind == "(":
        items, i = [], i + 1
        while i < len(tokens) and tokens[i][0] != ")":
            item, i = _parse(tokens, i)
            items.append(item)
        if i >= len(tokens):
            raise SexpError("unbalanced parentheses: missing ')'")
        return items, i + 1
    if kind == ")":
        raise SexpError("unbalanced parentheses: unexpected ')'")
    return value, i + 1


def _atom(text: str) -> Any:
    if text == "true":
        return True
    if text == "false":
        return False
    if text == "nil":
        return None
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.\d+", text):
        return float(text)
    return Sym(text)


def _unescape(text: str) -> str:
    return re.sub(r"\\(.)", r"\1", text)
