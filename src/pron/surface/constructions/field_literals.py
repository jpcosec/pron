"""The field literals of a sentence (spec 06, spec 13 §$literals): what each noun phrase
captured, then every field word followed by a literal, a number or an unknown run, and every
alias form with slots — for the fields of one model's family when a model is given.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.item import Item
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.kernel.parts.word import Word
from pron.surface.interpret import FIELD_KINDS
from pron.surface.phrases.field_values import field_is_string, slot_value, value_run

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon

VALUE_KINDS = ("literal", "number", "unknown")


class FieldLiterals:
    """field name -> value, as a sentence says them."""

    def __init__(self, lex: "Lexicon") -> None:
        self.lex = lex

    def __call__(
        self, items: list[Item], nps: list[NounPhrase], model: str | None = None
    ) -> dict[str, Any]:
        """Field literals anywhere in the sentence: field word + literal/number, alias forms with slots, literals with markers."""
        out: dict[str, Any] = {}
        for np in nps:
            out.update(np.captures)
        for k, it in enumerate(items):
            if it.kind == "word":
                self._item(items, k, model, out)
        return out

    def _item(
        self, items: list[Item], k: int, model: str | None, out: dict[str, Any]
    ) -> None:
        """The first field word of the item that belongs to the model gives its value, if any."""
        it = items[k]
        w = next(
            (
                w
                for w in it.words
                if w.kind in FIELD_KINDS and not self._foreign(w, model)
            ),
            None,
        )
        if w is None:
            return
        assert w.field_name is not None
        if it.slots:
            out[w.field_name] = slot_value(it)
        elif k + 1 < len(items) and items[k + 1].kind in VALUE_KINDS:
            out[w.field_name], _ = value_run(
                items[k + 1 :],
                string_field=field_is_string(self.lex, w.model, w.field_name),
            )

    def _foreign(self, w: Word, model: str | None) -> bool:
        """A field word of another model, outside the given model's family."""
        return bool(
            model
            and w.model
            and w.model != model
            and model not in self.lex.world.family_of(w.model)
        )
