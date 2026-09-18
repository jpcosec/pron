"""The semantic plane (spec 14 §2.2): selectors that start with `@`, optionally after a model
that restricts them to itself and its family (`{Modelo+}`), composed with `&` as the
intersection of their sets (spec 02). Every selector is a predicate the world declares.
"""

from __future__ import annotations

from functools import reduce
from typing import Any

from pron.mcp.doc_entries import DocEntries
from pron.mcp.family_selector import FamilySelector
from pron.mcp.found import Found
from pron.mcp.literal_reads import model_ref
from pron.mcp.mount import Mount
from pron.mcp.value_selector import ValueSelector
from pron.mcp.walk import Walk


class SemanticReads:
    """A semantic address to a set of documents, each with its literal address."""

    def __init__(self, mount: Mount) -> None:
        self.mount = mount
        self.values = ValueSelector(mount)
        self.families = FamilySelector(mount)
        self.walk = Walk(mount)

    def __call__(self, segments: list[str]) -> dict[str, Any]:
        model = None if segments[0].startswith("@") else model_ref(segments[0])[1]
        path = "/".join(segments if model is None else segments[1:])
        found = reduce(Found.intersect, [self.one(p) for p in path.split("&")])
        if model is not None:
            found = found.restrict(self.family(model))
        return {"model": model, **found.answer(DocEntries(self.mount))}

    def one(self, selector: str) -> Found:
        """`@value`, `@family/name`, or `@doc/relation/…`."""
        if not selector.startswith("@"):
            raise ValueError(f"a selector starts with @: {selector!r}")
        head, *rest = selector[1:].split("/")
        if head == "family" and len(rest) == 1:
            return self.families(rest[0])
        if rest:
            return self.walk(head, rest)
        return self.values(head)

    def family(self, model: str) -> list[str]:
        """The model and the projection's models that extend it."""
        self.mount.require_model(model)
        world = self.mount.world
        return [m for m in self.mount.models() if model in world.family_of(m)]
