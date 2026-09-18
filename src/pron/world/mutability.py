"""The ladder of mutability (spec 14 §5): how far a session may change its world, declared per
projection in its `mutability` field. 0 reads, 1 writes documents and edges, 2 also relation
types, 3 also models. A projection without the field is level 1, what a projection allowed
before the ladder; a read-only session is level 0 whatever its projection says (the load
writes that into the projection it reads through, spec 05).
"""

from __future__ import annotations

from typing import Any

CONTENT, RULES, MODELS = 1, 2, 3
NAMES = {0: "reads", CONTENT: "content", RULES: "rules", MODELS: "models"}

# the internal models a form may name from a level up, though they are no words of the lexicon
FORM_MODELS = {RULES: ("RelationTypeDoc",)}


def level_of(projection: dict[str, Any]) -> int:
    """The level a (loaded) projection declares; absent or empty is level 1."""
    v = projection.get("mutability")
    return CONTENT if v is None or v == "" else int(v)


def form_models(level: int) -> frozenset[str]:
    """The internal models the forms of a session of this level may name."""
    return frozenset(m for lv, ms in FORM_MODELS.items() if level >= lv for m in ms)
