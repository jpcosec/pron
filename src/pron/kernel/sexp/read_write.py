"""S-expressions: pron's structured language (spec 06, 13). A move is a list of forms; the natural
language surface is a wrapper that resolves a sentence to these forms and evaluates them.

Only the reader and the printer live here; what each form means is in pron.sexpr.forms.compiler.
Atoms are symbols (Sym), strings, integers, floats, and the symbols true, false and nil.
"""

from __future__ import annotations

import re
from typing import Any

from pron.kernel.sexp.sexp_error import SexpError
from pron.kernel.sexp.sym import Sym

TOKEN = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))')


def read(text: str) -> list[Any]:
    """Every top-level expression in text, in order."""
    tokens = _tokens(text.strip())
    out, i = [], 0
    while i < len(tokens):
        expr, i = _parse(tokens, i)
        out.append(expr)
    return out


def _tokens(text: str) -> list[tuple[str, Any]]:
    tokens: list[tuple[str, Any]] = []
    pos = 0
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if m is None or m.end() == pos:
            raise SexpError(
                f"cannot read s-expression at {pos}: {text[pos : pos + 20]!r}"
            )
        pos = m.end()
        tokens.append(_token(m))
        if pos < len(text) and text[pos:].strip() == "":
            break
    return tokens


def _token(m: re.Match[str]) -> tuple[str, Any]:
    """A parenthesis, a quoted string, or a bare atom: exactly one of TOKEN's groups matched."""
    if m.group(1):
        return ("(", None)
    if m.group(2):
        return (")", None)
    if m.group(3) is not None:
        return ("atom", _unescape(m.group(3)))
    return ("atom", _atom(m.group(4)))


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
