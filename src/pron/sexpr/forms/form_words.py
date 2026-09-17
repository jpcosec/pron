"""The words a form names, checked against the session's lexicon (spec 01, 13): a model, a
relation or an alias outside the projection does not exist, and a kernel verb the session
cannot use is refused.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from pron.kernel.parts.word import Word
from pron.sexpr.forms.unknown_word import UnknownWord
from pron.world.store_error import StoreError

if TYPE_CHECKING:
    from pron.world.lexicon import Lexicon
    from pron.world.world import World


class FormWords:
    """The lexicon's words by what a form calls them."""

    def __init__(self, lex: Lexicon, world: World):
        self.lex, self.world = lex, world

    def need_model(self, model: str) -> None:
        if model not in self.lex.models and not (
            set(self.world.family_of(model)) & set(self.lex.models)
        ):
            raise UnknownWord(f"I don't have that word: {model}")

    def relation(self, relation: str) -> Word:
        w = self._first(lambda x: x.kind == "relation" and x.relation == relation)
        if w is None:
            raise UnknownWord(f"I don't have that word: relation {relation}")
        return w

    def kernel(self, verb: str) -> Word:
        w = self._first(lambda x: x.kind == "action" and x.payload.get("verb") == verb)
        if w is None:
            raise StoreError(f"in this session I cannot {verb}")
        return w

    def alias(self, symbol: str) -> Word:
        w = self._first(
            lambda x: x.kind.startswith("alias-") and x.payload.get("symbol") == symbol
        )
        if w is None:
            raise UnknownWord(f"I don't have that word: alias {symbol}")
        return w

    def _first(self, test: Callable[[Word], bool]) -> Word | None:
        return next((x for x in self.lex.words if test(x)), None)
