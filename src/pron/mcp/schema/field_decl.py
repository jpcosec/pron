"""One field of a model declared in JSON (spec 14 §4, nivel 3): `{name, type, description,
required?, default?, enum?}` with the types sldb's schema already describes — `str`, `int`,
`float`, `bool`, `list[str]`, `Literal[…]` (or any of them with `enum`). What it becomes in
the generated module.
"""

from __future__ import annotations

import ast
import json
import keyword
from dataclasses import dataclass
from typing import Any

from pron.mcp.writes.arg_error import ArgError

TYPES = ("str", "int", "float", "bool", "list[str]")
EMPTY: dict[str, Any] = {
    "str": "",
    "int": 0,
    "float": 0.0,
    "bool": False,
    "list[str]": [],
}


@dataclass(frozen=True)
class FieldDecl:
    """A declared field, checked: an identifier, a known type, a description."""

    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum: tuple[str, ...] = ()

    @staticmethod
    def of(raw: Any) -> "FieldDecl":
        """ArgError when the declaration does not make a field."""
        name, kind = _name(raw), str(raw.get("type") or "str").strip()
        enum = tuple(map(str, raw.get("enum") or _literal(kind)))
        if not enum and kind not in TYPES:
            raise ArgError(f"field {name}: type {kind!r} is not one of {list(TYPES)}")
        if not str(raw.get("description") or "").strip():
            raise ArgError(f"field {name} needs a description")
        default = raw.get("default")
        return FieldDecl(
            name,
            kind,
            raw["description"],
            bool(raw.get("required", default is None)),
            default,
            enum,
        )

    @property
    def annotation(self) -> str:
        return f"Literal[{', '.join(map(repr, self.enum))}]" if self.enum else self.type

    @property
    def empty(self) -> Any:
        """The default of an optional field: the one given, else its type's empty value."""
        if self.default is not None:
            return self.default
        return self.enum[0] if self.enum else EMPTY[self.type]

    def source(self) -> str:
        """The field's line in the class body."""
        described = f"description={self.description!r}"
        default = "" if self.required else f"default={self.empty!r}, "
        return f"    {self.name}: {self.annotation} = Field({default}{described})"

    def default_json(self) -> str | None:
        """The default as sldb's draft edit takes it (JSON text), None when required."""
        return None if self.required else json.dumps(self.empty)


def _name(raw: Any) -> str:
    """The declared field's name: a public identifier."""
    if not isinstance(raw, dict) or not isinstance(raw.get("name"), str):
        raise ArgError(f"a field is {{name, type, description, …}}, not {raw!r}")
    name = raw["name"]
    if not name.isidentifier() or keyword.iskeyword(name) or name.startswith("_"):
        raise ArgError(f"field name {name!r} is not an identifier")
    return name


def _literal(kind: str) -> list[str]:
    """The values of a `Literal[…]` type, or none."""
    if not (kind.startswith("Literal[") and kind.endswith("]")):
        return []
    try:
        values = ast.literal_eval(f"[{kind[len('Literal[') : -1]}]")
    except (ValueError, SyntaxError):
        raise ArgError(f"type {kind!r} is not a Literal of strings") from None
    if not values or not all(isinstance(v, str) for v in values):
        raise ArgError(f"type {kind!r} is not a Literal of strings")
    return values
