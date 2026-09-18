"""Reading and writing the s-expressions this layer speaks.

Nothing here knows about goals or stores: text becomes nested Python data (lists, Sym,
str, int, float, bool, None) and back. A symbol that begins with '?' is left as a plain
Sym; terms.py is what treats it as a variable.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any


class Sym(str):
    """A symbol: a str subclass, so a pattern compares by name and prints unquoted."""

    __slots__ = ()

    def __repr__(self) -> str:
        return f"Sym({str.__repr__(self)})"


class SexpError(ValueError):
    """Text that is not an s-expression."""


_CONSTANTS: dict[str, Any] = {"true": True, "false": False, "nil": None}
_BREAK = "();"


def _string_token(text: str, i: int) -> tuple[str, int]:
    """The string literal starting at the opening quote, and where it ends."""
    out: list[str] = []
    j = i + 1
    while j < len(text) and text[j] != '"':
        if text[j] == "\\" and j + 1 < len(text):
            out.append(text[j + 1])
            j += 2
            continue
        out.append(text[j])
        j += 1
    if j >= len(text):
        raise SexpError("unterminated string")
    return '"' + "".join(out), j + 1


def _tokens(text: str) -> Iterator[str]:
    """Parens, string literals (kept with a leading quote) and bare atoms; ; is a comment."""
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == ";":
            while i < n and text[i] != "\n":
                i += 1
        elif c in "()":
            yield c
            i += 1
        elif c.isspace():
            i += 1
        elif c == '"':
            tok, i = _string_token(text, i)
            yield tok
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in _BREAK:
                j += 1
            yield text[i:j]
            i = j


def _atom(tok: str) -> Any:
    if tok.startswith('"'):
        return tok[1:]
    if tok in _CONSTANTS:
        return _CONSTANTS[tok]
    for cast in (int, float):
        try:
            return cast(tok)
        except ValueError:
            pass
    return Sym(tok)


def read_all(text: str) -> list[Any]:
    """Every form in the text, in order."""
    stack: list[list[Any]] = [[]]
    for tok in _tokens(text):
        if tok == "(":
            stack.append([])
        elif tok == ")":
            if len(stack) == 1:
                raise SexpError("unbalanced ')'")
            done = stack.pop()
            stack[-1].append(done)
        else:
            stack[-1].append(_atom(tok))
    if len(stack) != 1:
        raise SexpError("unbalanced '('")
    return stack[0]


def read_one(text: str) -> Any:
    forms = read_all(text)
    if len(forms) != 1:
        raise SexpError(f"expected one form, got {len(forms)}")
    return forms[0]


def write(form: Any) -> str:
    """A form as text, readable back by read_one."""
    if isinstance(form, Sym):
        return str(form)
    if isinstance(form, bool):
        return "true" if form else "false"
    if form is None:
        return "nil"
    if isinstance(form, str):
        return '"' + form.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(form, (int, float)):
        return str(form)
    if isinstance(form, (list, tuple)):
        return "(" + " ".join(write(x) for x in form) + ")"
    return str(form)
