"""Which tokens after "of" are a run of proper names (spec 02): "the reservations of Luis
Soto" names Luis Soto by its words, up to the next known word, determiner, stop word,
preposition or dated literal.
"""

from __future__ import annotations

from pron.kernel.parts.item import Item
from pron.surface.phrases.phrase_words import PREDICATE_STOP

PREPOSITIONS = ("for", "on", "at")


def proper_run(items: list[Item], j: int) -> list[Item]:
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
