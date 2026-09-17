"""The opening of a noun phrase (spec 02): what comes before its head — a determiner, a
genitive ("Ana's reservations"), or a phrase that is only a referent, including a pronoun an
alias form swallowed ("confirm it").
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.surface.phrases.phrase_words import PRONOUNS, det_kind, head_model

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon

SWALLOWING_ALIASES = ("alias-action", "alias-compose", "alias-relation")


class PhraseOpening:
    """The position, determiner and genitive of one phrase attempt, read before its head."""

    def __init__(self, items: list[Item], start: int, lex: "Lexicon") -> None:
        self.items = items
        self.start = start
        self.lex = lex
        self.i = start
        self.det: str | None = None
        self.genitive: list[str] = []

    def _determiner(self) -> bool:
        """Past the determiner, if there is one; False when the sentence ends right after it."""
        it = self.items[self.i]
        if it.kind != "det":
            return True
        self.det = det_kind(it.text)
        self.i += 1
        return self.i < len(self.items)

    def _genitive(self) -> None:
        """ "Ana's reservations": the possessor's tokens become a complement of the head."""
        items, i = self.items, self.i
        if items[i].kind != "unknown":
            return
        k = i
        while (
            k < len(items)
            and items[k].kind in ("unknown", "number")
            and not items[k].text.endswith("'s")
        ):
            k += 1
        if self._possessive_before_head(k):
            self.genitive = [x.text for x in items[i:k]] + [items[k].text[:-2]]
            self.i = k + 1

    def _possessive_before_head(self, k: int) -> bool:
        items = self.items
        return (
            k < len(items)
            and items[k].kind == "unknown"
            and items[k].text.endswith("'s")
            and k + 1 < len(items)
            and head_model(items[k + 1]) is not None
        )

    def _referent(self, it: Item) -> tuple[NounPhrase, int] | None:
        if it.kind == "referent" and it.meta.get("who") in ("singular", "plural"):
            np = NounPhrase(
                None, self.det, it.number or "singular", referent=it, items=[it]
            )
            return np, self.i - self.start + 1
        if it.kind == "word" and it.words and it.words[0].kind in SWALLOWING_ALIASES:
            return self._swallowed_pronoun(it)
        return None

    def _swallowed_pronoun(self, it: Item) -> tuple[NounPhrase, int] | None:
        """ "confirm it", "book her": the alias form swallowed the pronoun; it is still a referent."""
        last = it.text.split()[-1].lower()
        number = PRONOUNS.get(last)
        if not number or self.det is not None:
            return None
        fake = Item(
            "referent", last, number=number, meta={"who": number, "implicit": True}
        )
        return NounPhrase(None, None, number, referent=fake, items=[it]), 1
