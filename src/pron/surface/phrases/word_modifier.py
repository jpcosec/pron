"""One word item as a modifier of a noun phrase (spec 02): a value word, a predicate alias
with its slots filled, or a field word with its value — each one sldb predicate on the head.
A word whose model is outside the head's family is not a modifier of this phrase.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.item import Item
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.kernel.parts.word import Word
from pron.surface.phrases.field_values import (
    field_is_string,
    slot_value,
    sldb_literal,
    value_run,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class WordModifier:
    """Attaches one word item to a noun phrase, if one of its words modifies the head."""

    def __init__(self, lex: "Lexicon") -> None:
        self.lex = lex

    def __call__(self, it: Item, following: list[Item] | None, np: NounPhrase) -> int:
        """Returns the items used: 0 when no word of the item modifies this phrase."""
        assert np.model is not None
        following = following or []
        family = set(self.lex.world.family_of(np.model))
        for w in it.words:
            used = self._word(w, it, following, np) if w.model in family else 0
            if used:
                return used
        return 0

    def _word(self, w: Word, it: Item, following: list[Item], np: NounPhrase) -> int:
        if w.kind == "value":
            np.predicates.append(f'{w.field_name} = "{w.payload["value"]}"')
            np.items.append(it)
            return 1
        if w.kind == "alias-predicate":
            return self._predicate(w, it, np)
        if w.kind in ("field", "alias-field"):
            return self._field(w, it, following, np)
        return 0

    def _predicate(self, w: Word, it: Item, np: NounPhrase) -> int:
        where, unknown = self._fill_predicate(w, it)
        if unknown:
            np.unknown_values.append(unknown)
        np.predicates.append(where)
        np.items.append(it)
        return 1

    def _field(self, w: Word, it: Item, following: list[Item], np: NounPhrase) -> int:
        """A field word with its value: a captured slot, or the run of items after it."""
        assert w.field_name is not None
        found = self._field_value(w, it, following)
        if found is None:
            return 0
        value, used = found
        np.predicates.append(f"{w.field_name} = {sldb_literal(value)}")
        np.captures[w.field_name] = value
        np.items += [it, *following[:used]]
        return 1 + used

    def _field_value(
        self, w: Word, it: Item, following: list[Item]
    ) -> tuple[Any, int] | None:
        """(value, items used after the word): a captured slot, else the run after it."""
        if it.slots:
            return slot_value(it), 0
        if following and following[0].kind in ("number", "literal", "unknown"):
            return value_run(
                following, string_field=field_is_string(self.lex, w.model, w.field_name)
            )
        return None

    def _fill_predicate(
        self, w: Word, it: Item
    ) -> tuple[str, tuple[str, str, str] | None]:
        """(where M "<predicate>") with N / Z / X slots substituted; a Z that is not a known value is reported."""
        assert w.model is not None
        where = str(w.payload["where"])
        unknown = None
        for slot, value in it.slots.items():
            if slot == "Z":
                where, unknown = self._fill_z(w.model, where, value, unknown)
            else:
                where = where.replace(slot, str(value))
        return where, unknown

    def _fill_z(
        self, model: str, where: str, value: Any, unknown: tuple[str, str, str] | None
    ) -> tuple[str, tuple[str, str, str] | None]:
        """Z quoted in; reported when the field it compares has known values and this is not one."""
        fld = where.split("=")[0].strip().split()[0]
        known = {v.payload["value"] for v in self.lex.values_of(model, fld)}
        if known and value not in known:
            unknown = (model, fld, value)
        return where.replace("Z", f'"{value}"'), unknown
