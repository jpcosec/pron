"""The field and value a change names (spec 11 §7): outside the subject phrase, the first
field word of the subject's family with a slot or a value after it, or a value word of that
family, which names its field itself.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.item import Item
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.surface.constructions.field_literals import VALUE_KINDS
from pron.surface.interpret import FIELD_KINDS
from pron.surface.phrases.field_values import slot_value

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class FieldAndValue:
    """(field name, value) for a subject, or (None, None)."""

    def __init__(self, lex: "Lexicon") -> None:
        self.lex = lex

    def __call__(
        self, items: list[Item], subject: NounPhrase
    ) -> tuple[str | None, Any]:
        family = (
            set(self.lex.world.family_of(subject.model)) if subject.model else set()
        )
        for k, it in enumerate(items):
            if it.kind != "word" or it in subject.items:
                continue
            found = self._in_item(items, k, family, subject)
            if found is not None:
                return found
        return None, None

    @staticmethod
    def _in_item(
        items: list[Item], k: int, family: set[str], subject: NounPhrase
    ) -> tuple[str | None, Any] | None:
        it = items[k]
        for w in it.words:
            if w.kind in FIELD_KINDS and (
                not family or w.model in family or subject.model is None
            ):
                if it.slots:
                    return w.field_name, slot_value(it)
                if k + 1 < len(items) and items[k + 1].kind in VALUE_KINDS:
                    return w.field_name, items[k + 1].meta.get("value", items[k + 1].text)
            if w.kind == "value" and (not family or w.model in family):
                return w.field_name, w.payload["value"]
        return None
