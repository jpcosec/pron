"""The value a field word takes in a sentence (spec 02, spec 06): a slot the form captured,
one literal or number, or for a string field the whole run of unknown and number items up
to the next known one; and that value written as an sldb literal.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.item import Item
from pron.surface.phrases.phrase_words import PREDICATE_STOP

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


def slot_value(it: Item) -> Any:
    """The value a form's slot captured, in slot priority (N, DAY, TIME, Z, X), else the text."""
    for key in ("N", "DAY", "TIME", "Z", "X"):
        if key in it.slots:
            return it.slots[key]
    return it.text


def field_is_string(lex: "Lexicon", model: str | None, field_name: str | None) -> bool:
    if not model or not field_name:
        return False
    for f in lex.world.schema(model, lex.stores):
        if f["name"] == field_name:
            return f["kind"] == "string"
    return False


def value_run(following: list[Item], string_field: bool) -> tuple[Any, int]:
    """The value after a field word: one literal or number, or for a string field the whole run of
    unknown and number items ("Ana Rojas", "9 5555 1234") up to the next known item."""
    first = following[0]
    if first.kind == "literal":
        return first.meta.get("value", first.text), 1
    if not string_field:
        return first.meta.get("value", first.text), 1
    parts, used = [], 0
    for it in following:
        if it.kind in ("unknown", "number") and it.text.lower() not in PREDICATE_STOP:
            parts.append(it.text)
            used += 1
        else:
            break
    return " ".join(parts), used


def sldb_literal(value: Any) -> str:
    """A number as itself, anything else quoted."""
    return str(value) if isinstance(value, (int, float)) else f'"{value}"'
