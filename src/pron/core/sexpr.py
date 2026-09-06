"""S-expression kernel: parse and serialize the Meaning layer.

Implements atom-sexpr-serialization-quotes-selectors-and-roundtrips: symbols
unquoted, selectors always double-quoted, options as trailing :keyword pairs,
and parse(serialize(e)) == e. Depends on nothing in the project.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Symbol:
    """An unquoted symbol resolved later through its anchor."""

    name: str

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Keyword:
    """A :keyword introducing an option pair."""

    name: str

    def __repr__(self) -> str:
        return f":{self.name}"


SExpr = list  # an expression is a Python list of Symbol | Keyword | str | int | float | SExpr


class SexprError(ValueError):
    """Raised when a surface string is not a valid s-expression."""


def parse(text: str) -> SExpr:
    """Parse canonical s-expression text into the Meaning structure."""
    tokens = _tokenize(text)
    if not tokens:
        raise SexprError("empty expression")
    expr, rest = _read(tokens)
    if rest:
        raise SexprError(f"trailing tokens after expression: {rest[:3]}")
    if not isinstance(expr, list):
        raise SexprError("top-level form must be a list")
    return expr


def serialize(expr: SExpr) -> str:
    """Serialize a Meaning structure back to canonical text (roundtrips)."""
    return _write(expr)


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif c in "()":
            tokens.append(c)
            i += 1
        elif c == '"':
            j = i + 1
            buf: list[str] = []
            while j < n and text[j] != '"':
                if text[j] == "\\" and j + 1 < n:
                    buf.append(text[j + 1])
                    j += 2
                else:
                    buf.append(text[j])
                    j += 1
            if j >= n:
                raise SexprError("unterminated string")
            tokens.append('"' + "".join(buf))
            i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in '()"':
                j += 1
            tokens.append(text[i:j])
            i = j
    return tokens


def _read(tokens: list[str]) -> tuple[object, list[str]]:
    head, rest = tokens[0], tokens[1:]
    if head == "(":
        items: list[object] = []
        while rest and rest[0] != ")":
            item, rest = _read(rest)
            items.append(item)
        if not rest:
            raise SexprError("unbalanced parentheses")
        return items, rest[1:]
    if head == ")":
        raise SexprError("unexpected ')'")
    return _read_atom(head), rest


def _read_atom(token: str) -> object:
    if token.startswith('"'):
        return token[1:]
    if token.startswith(":"):
        return Keyword(token[1:])
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        pass
    return Symbol(token)


def _write(item: object) -> str:
    if isinstance(item, list):
        return "(" + " ".join(_write(x) for x in item) + ")"
    if isinstance(item, Symbol):
        return item.name
    if isinstance(item, Keyword):
        return f":{item.name}"
    if isinstance(item, str):
        escaped = item.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return str(item)
