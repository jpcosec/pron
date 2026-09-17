"""The constructions a sentence can match, and the small operations every one of them needs
(spec 06, 11 §1).

The constructions are fixed and listed in patterns.yaml; a world never adds one, it
adds words. A sentence coordinated with "and" is one move with several parts, and that
split, the search for a verb word among the items, and what is left unattached to any
noun phrase are all here — the constructions themselves are Interpreter's methods.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from pron.kernel.item import Item
from pron.kernel.noun_phrase import NounPhrase
from pron.kernel.part import Part
from pron.kernel.word import Word

PATTERNS = yaml.safe_load(
    (Path(__file__).parent / "patterns.yaml").read_text(encoding="utf-8")
)["constructions"]


def construction_names() -> list[str]:
    """The constructions pron tries, by name (spec 11 §1): world-agnostic, unlike a fixed
    example sentence, which would leak whatever world wrote patterns.yaml's docstrings into
    every other world's hint text."""
    return [c["name"] for c in PATTERNS]


def _split_on_and(items: list[Item]) -> list[list[Item]]:
    chunks: list[list[Item]] = []
    cur: list[Item] = []
    for it in items:
        if it.kind == "conj":
            if cur:
                chunks.append(cur)
            cur = []
        else:
            cur.append(it)
    if cur:
        chunks.append(cur)
    return chunks or [[]]


def _kernel(items: list[Item], verb: str) -> Word | None:
    for it in items:
        for w in it.words:
            if w.kind == "action" and w.payload.get("verb") == verb:
                return w
    return None


def _first(items: list[Item], *kinds: str) -> Word | None:
    for it in items:
        for w in it.words:
            if w.kind in kinds:
                return w
    return None


def _in_np(it: Item, nps: list[NounPhrase]) -> bool:
    return any(it is x for n in nps for x in n.items)


def _unattached(items: list[Item], nps: list[NounPhrase]) -> list[Item]:
    return [
        i
        for i in items
        if not _in_np(i, nps) and i.kind not in ("punct", "det", "conj", "of")
    ]


def _used(it: Item, parts: list[Part]) -> bool:
    for p in parts:
        for n in (p.subject, p.object):
            if n and any(it is x for x in n.items):
                return True
        if any(it is x for x in p.leftovers) and p.kind == "read":
            return True
    return False


def _proper_phrase(
    named: list[Item], types: set[str], nps: list[NounPhrase]
) -> NounPhrase | None:
    """A bare proper name on the other side of a relation takes that side's model."""
    other = next((n for n in nps if n.referent is not None), None)
    if other is not None:
        return other
    if not named or not types:
        return None
    model = sorted(types)[0]
    return NounPhrase(
        model, "the", "singular", proper=[named[0].text], items=[named[0]]
    )


def _implicit_it() -> NounPhrase:
    return NounPhrase(
        None,
        None,
        "singular",
        referent=Item(
            "referent",
            "it",
            number="singular",
            meta={"who": "singular", "implicit": True},
        ),
    )


def _slot_value(it: Item) -> Any:
    for key in ("N", "DAY", "TIME", "Z", "X"):
        if key in it.slots:
            return it.slots[key]
    return it.text
