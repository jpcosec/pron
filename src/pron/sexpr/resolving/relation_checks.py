"""A verb verified against its RelationTypeDoc (spec 03): the relation type exists in this
world, the subject and object are of the classes it takes, and a new edge does not break its
cardinality — read from the RelationDocs in sldb, the edges as authored.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.world.store_error import StoreError

if TYPE_CHECKING:
    from pron.sexpr.resolving.edge_reader import EdgeReader
    from pron.world.lexicon import Lexicon

# a subject relates to one object at most; an object is related from one subject at most
ONE_TARGET = ("one_to_one", "many_to_one")
ONE_SOURCE = ("one_to_one", "one_to_many")


class RelationChecks:
    """Whether an edge of a relation type may exist, before it is written."""

    def __init__(self, lex: Lexicon, reader: EdgeReader):
        self.lex, self.world, self.reader = lex, lex.world, reader

    def relation_type(self, name: str) -> dict[str, Any]:
        rt = self.lex.relation_types.get(name)
        if rt is None:
            raise StoreError(f"'{name}' is not a relation type of this world")
        return rt

    def applies(
        self, name: str, source_model: str, target_model: str
    ) -> tuple[bool, str]:
        rt = self.relation_type(name)
        why = self._takes(name, rt.get("source_types"), source_model, "subject")
        why = why or self._takes(name, rt.get("target_types"), target_model, "object")
        return (False, why) if why else (True, "")

    def _takes(self, name: str, types: list[str] | None, model: str, role: str) -> str:
        """Why the relation does not take `model` in `role`; empty when it does."""
        if types and not set(self.world.family_of(model)) & set(types):
            return f"{name} takes {', '.join(types)} as {role}, not {model}"
        return ""

    def cardinality_ok(self, name: str, source: str, target: str) -> tuple[bool, str]:
        card = self.relation_type(name).get("cardinality", "many_to_many")
        why = (
            self._other_target(name, source, target, card) if card in ONE_TARGET else ""
        )
        if not why and card in ONE_SOURCE:
            why = self._other_source(name, source, target, card)
        return (False, why) if why else (True, "")

    def _other_target(self, name: str, source: str, target: str, card: str) -> str:
        edges = self.reader.sldb("source_id", source, name).edges
        existing = [e for e in edges if e["target"] != target]
        if not existing:
            return ""
        return f"{source} already has {name} → {existing[0]['target']} and cardinality is {card}"

    def _other_source(self, name: str, source: str, target: str, card: str) -> str:
        edges = self.reader.sldb("target_id", target, name).edges
        existing = [e for e in edges if e["source"] != source]
        if not existing:
            return ""
        return f"{target} already is {name} of {existing[0]['source']} and cardinality is {card}"
