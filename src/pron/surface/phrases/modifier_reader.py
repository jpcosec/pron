"""The modifiers after a noun phrase's head (spec 02), in order of trial: a date or time
literal (with its preposition), a proper name, a number, an "of" complement — a value of a
field of the head, a nested phrase, or a run of proper-name tokens — and a word modifier.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from pron.kernel.parts.item import Item
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.surface.phrases.phrase_words import PREDICATE_STOP, head_model
from pron.surface.phrases.word_modifier import WordModifier

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon

PREPOSITIONS = ("for", "on", "at")
ReadPhrase = Callable[[list[Item], int], "tuple[NounPhrase | None, int]"]


class ModifierReader:
    """Attaches the modifier at one position to a phrase; `read_phrase` reads a nested one."""

    def __init__(self, lex: "Lexicon", read_phrase: ReadPhrase) -> None:
        self.lex = lex
        self.read_phrase = read_phrase
        self.word_modifier = WordModifier(lex)

    def __call__(self, items: list[Item], j: int, np: NounPhrase) -> int:
        """Returns the items used: 0 when the item at `j` does not modify the phrase."""
        it = items[j]
        if it.kind in ("literal", "unknown"):
            return self._literal_or_unknown(items, j, np)
        if it.kind == "number":
            np.proper.append(str(it.meta["value"]))
            np.items.append(it)
            return 1
        if it.kind == "of":
            return self._of(items, j, np) if j + 1 < len(items) else 0
        if it.kind == "word":
            return self.word_modifier(it, items[j + 1 :], np)
        return 0

    def _literal_or_unknown(self, items: list[Item], j: int, np: NounPhrase) -> int:
        it = items[j]
        if it.kind == "literal" and it.meta.get("kind") in ("date", "time"):
            return self._dated(it, np)
        if _dated_after_preposition(items, j):
            return self._prepositioned(it, items[j + 1], np)
        if it.kind == "unknown" or (not it.meta.get("marker") and not it.meta.get("kind")):
            return self._proper(it, np)
        return 0

    def _prepositioned(self, preposition: Item, dated: Item, np: NounPhrase) -> int:
        used = self._dated(dated, np)
        if used:
            np.items.append(preposition)  # the preposition belongs to the phrase too
        return 1 + used if used else 0

    @staticmethod
    def _proper(it: Item, np: NounPhrase) -> int:
        """A proper name in name position: "the client Ana", "the bridges one"."""
        if it.kind == "unknown" and it.text.lower() in PREDICATE_STOP:
            return 0
        np.proper.append(it.text)
        np.items.append(it)
        return 1

    def _dated(self, it: Item, np: NounPhrase) -> int:
        """A date or time literal as a modifier: the head's field of that kind, or named so."""
        assert np.model is not None
        kind = it.meta.get("kind")
        for f in self.lex.world.schema(np.model, self.lex.stores):
            if f["name"] == kind or f["kind"] == kind:
                np.predicates.append(f'{f["name"]} = "{it.meta["value"]}"')
                np.items.append(it)
                return 1
        return 0

    def _of(self, items: list[Item], j: int, np: NounPhrase) -> int:
        it, nxt = items[j], items[j + 1]
        if (
            nxt.kind == "word"
            and head_model(nxt) is None
            and self.word_modifier(nxt, items[j + 2 :], np)
        ):
            np.items.append(it)  # "of pron": a value of a field of the head
            return 2
        nested = nxt.kind == "det" or head_model(nxt) is not None
        return (self._nested(items, j, np) if nested else 0) or self._named(items, j, np)

    def _nested(self, items: list[Item], j: int, np: NounPhrase) -> int:
        """"of the reservations of Luis": a nested phrase."""
        inner, used = self.read_phrase(items, j + 1)
        if inner is None:
            return 0
        np.complements.append(inner)
        np.items += [items[j], *inner.items]
        return 1 + used

    def _named(self, items: list[Item], j: int, np: NounPhrase) -> int:
        run = _proper_run(items, j + 1)
        if not run:
            return 0
        np.complements.append([x.text for x in run])
        np.items += [items[j], *run]
        return 1 + len(run)


def _dated_after_preposition(items: list[Item], j: int) -> bool:
    it = items[j]
    return (
        it.kind == "unknown"
        and it.text.lower() in PREPOSITIONS
        and j + 1 < len(items)
        and items[j + 1].kind == "literal"
        and items[j + 1].meta.get("kind") in ("date", "time")
    )


def _proper_run(items: list[Item], j: int) -> list[Item]:
    """The unknown, number and plain-literal items after "of", up to the next known word, determiner,
    stop word or dated literal."""
    run: list[Item] = []
    while j < len(items) and _proper_token(items[j]):
        run.append(items[j])
        j += 1
    return run


def _proper_token(it: Item) -> bool:
    if it.kind == "unknown":
        return it.text.lower() not in PREDICATE_STOP | set(PREPOSITIONS)
    return it.kind == "number" or (
        it.kind == "literal" and not it.meta.get("marker") and not it.meta.get("kind")
    )
