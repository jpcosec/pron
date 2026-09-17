"""The extra modifiers a read left over, as predicates on the asked side (spec 02, 13).

"what did Ana book for Friday" reads the edges of `book` from Ana, and "for Friday" is not
about Ana: it narrows what comes back. Those leftover items become sldb predicates on the
asked phrase — a date literal against the model's `date` field, a word through the same
modifier machinery a noun phrase uses — and the read intersects its answer with them. The
phrase itself is copied first: the predicates belong to this read, not to the phrase.
"""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.surface.nouns import _word_modifier

if TYPE_CHECKING:
    from pron.world.lexicon import Lexicon
    from pron.world.world import World


class LeftoverPredicates:
    """What a read's extra modifiers add to the side it asks about."""

    def __init__(self, world: World, lex: Lexicon):
        self.world, self.lex = world, lex

    def __call__(self, np: NounPhrase, leftovers: list[Item]) -> list[str]:
        """The phrase's own predicates plus the leftovers'; none without leftovers."""
        if not leftovers or np.model is None:
            return []
        np = deepcopy(np)
        for it in leftovers:
            self._modifier(it, np)
        return list(np.predicates)

    def _modifier(self, it: Item, np: NounPhrase) -> None:
        if it.kind == "literal" and it.meta.get("kind") == "date":
            self._date(it, np)
        elif it.kind == "word":
            _word_modifier(it, None, np, self.lex)

    def _date(self, it: Item, np: NounPhrase) -> None:
        fld = self._date_field(np.model)
        if fld:
            np.predicates.append(f'{fld} = "{it.meta["value"]}"')

    def _date_field(self, model: str | None) -> str | None:
        return next(
            (
                f["name"]
                for f in self.world.schema(model, self.lex.stores)
                if f["name"] == "date"
            ),
            None,
        )
