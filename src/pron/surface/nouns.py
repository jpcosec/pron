"""Noun phrases: from a run of classified items to a scope and predicates (spec 02).

A noun phrase is a head (a model word, an alias for a model, or a referent) with a
determiner before it and modifiers after it. Modifiers are, in order of trial:
a proper name ("the client Ana", "the bridges one"), a value word ("the pending
reservations"), a predicate alias with its slots ("on the terrace", "for 6"), or a
field word followed by a value ("with capacity 6"). Every modifier becomes one
sldb predicate. A modifier whose word belongs to a model outside the head's family
is skipped for this phrase and left for the sentence.

"of X" after the head, and "X's" before it, are complements: what X is gets decided
at resolution (spec 02), in this order: a value of a field of the head, a document of
another class the head is related to (then the phrase crosses the edges of that
relation with its own predicates), a proper name of the head itself.

A phrase is read by pron.surface.phrases.phrase_reader.PhraseReader; its modifiers by
ModifierReader and WordModifier there.
"""

from __future__ import annotations

from pron.kernel.parts.item import Item
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.surface.phrases.phrase_reader import PhraseReader
from pron.surface.phrases.word_modifier import WordModifier
from pron.world.lexicon import Lexicon


def find_noun_phrases(items: list[Item], lex: Lexicon) -> list[NounPhrase]:
    """Every noun phrase in the item list, left to right, non-overlapping."""
    phrases: list[NounPhrase] = []
    i = 0
    while i < len(items):
        np, used = _phrase_at(items, i, lex)
        if np is None:
            i += 1
            continue
        phrases.append(np)
        i += used
    return phrases


def _phrase_at(
    items: list[Item], i: int, lex: Lexicon
) -> tuple[NounPhrase | None, int]:
    return PhraseReader(items, i, lex)()


def _word_modifier(
    it: Item, following: list[Item] | None, np: NounPhrase, lex: Lexicon
) -> int:
    """One word item as a modifier of np: a value, a predicate alias, or a field with a value. Returns items used."""
    return WordModifier(lex)(it, following, np)
