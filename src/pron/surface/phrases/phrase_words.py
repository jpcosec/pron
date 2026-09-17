"""The few words a noun phrase is built around (spec 02): what a determiner means, which
item is a head, which pronouns an alias form can swallow, and the words that stop a
proper name or a value.
"""

from __future__ import annotations

from pron.kernel.parts.item import Item

PREDICATE_STOP = {"and", "to", "as", "with"}
PRONOUNS = {
    "it": "singular",
    "her": "singular",
    "him": "singular",
    "them": "plural",
    "those": "plural",
}


def det_kind(text: str) -> str:
    """`any`, `all` or `the`: what a determiner asks for."""
    t = text.lower()
    if t in ("a", "an", "one", "any"):
        return "any"
    if t in ("all", "every", "all the", "these", "those"):
        return "all"
    return "the"


def head_model(it: Item) -> str | None:
    """The model a word item names as a head (a model word or an alias for one), or None."""
    if it.kind != "word":
        return None
    for w in it.words:
        if w.kind in ("model", "alias-model"):
            return w.model
    return None
