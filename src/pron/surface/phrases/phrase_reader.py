"""Reading one noun phrase at a position of a classified sentence (spec 02): past its opening
(`PhraseOpening`: determiner, genitive, referent), the adjectives before the head, the head
with its number, and the modifiers after it.
"""

from __future__ import annotations

from pron.kernel.parts.item import Item
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.surface.phrases.modifier_reader import ModifierReader
from pron.surface.phrases.phrase_opening import PhraseOpening
from pron.surface.phrases.phrase_words import head_model
from pron.surface.phrases.word_modifier import WordModifier

ASKING = ("what", "who", "how_many")


class PhraseReader(PhraseOpening):
    """One attempt at a noun phrase starting at `start`; call it once."""

    def __call__(self) -> tuple[NounPhrase | None, int]:
        """The phrase and the items it used, or (None, 0)."""
        if not self._determiner():
            return None, 0
        self._genitive()
        referent = self._referent(self.items[self.i])
        if referent is not None:
            return referent
        np = self._headed()
        if np is None:
            return None, 0
        return np, self._modifiers(np) - self.start

    def _headed(self) -> NounPhrase | None:
        """The head with its adjectives attached; None when there is no head or one does not attach."""
        pre = self._adjectives()
        if pre is None:
            return None
        it = self.items[self.i]
        head = head_model(it)
        if head is None:
            return None
        np = self._phrase(head, it)
        word_modifier = WordModifier(self.lex)
        return np if all(word_modifier(adj, [], np) for adj in pre) else None

    def _adjectives(self) -> list[Item] | None:
        """Value words and predicate aliases before the head ("the large tables", "the pending
        reservations"); None when the sentence ends before a head."""
        pre: list[Item] = []
        it = self.items[self.i]
        while (
            it.kind == "word"
            and head_model(it) is None
            and any(w.kind in ("value", "alias-predicate") for w in it.words)
        ):
            pre.append(it)
            self.i += 1
            if self.i >= len(self.items):
                return None
            it = self.items[self.i]
        return pre

    def _phrase(self, head: str, it: Item) -> NounPhrase:
        number = it.number or ("plural" if self.det in ("all",) else "singular")
        if self.det is None and number == "plural":
            self.det = "all"
        interrogated = self._interrogated()
        np = NounPhrase(
            head,
            self.det or ("the" if number == "singular" and not interrogated else "all"),
            number,
            interrogated=interrogated,
            items=[it],
        )
        if self.genitive:
            np.complements.append(self.genitive)
            np.items = self.items[self.start : self.i] + [it]
        return np

    def _interrogated(self) -> bool:
        """Whether the word before the phrase asks what, who or how many."""
        before = self.items[self.start - 1] if self.start > 0 else None
        return (
            before is not None
            and before.kind == "wh"
            and before.meta.get("question") in ASKING
        )

    def _modifiers(self, np: NounPhrase) -> int:
        """As many modifiers after the head as attach; returns the position past the last."""
        reader = ModifierReader(self.lex, self._nested)
        j = self.i + 1
        while j < len(self.items):
            used = reader(self.items, j, np)
            if not used:
                break
            j += used
        return j

    def _nested(self, items: list[Item], i: int) -> tuple[NounPhrase | None, int]:
        return PhraseReader(items, i, self.lex)()
