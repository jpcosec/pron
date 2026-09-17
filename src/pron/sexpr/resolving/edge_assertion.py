"""Asserting and negating an edge (spec 03). To assert is to create the RelationDoc, once the
relation type takes both classes, the cardinality allows it and the type's condition holds;
it is written in the session's write store, naming the documents as that store reads them.
To negate is to untrack the RelationDoc; an edge written in prose is edited in the text.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.ids import model_of, relativize
from pron.world.store_error import StoreError

if TYPE_CHECKING:
    from pron.sexpr.resolving.condition_check import ConditionCheck
    from pron.sexpr.resolving.edge_reader import EdgeReader
    from pron.sexpr.resolving.relation_checks import RelationChecks

DEFAULT_NAMING = "{relation_type}--{source_id}--{target_id}"


class EdgeAssertion:
    """RelationDocs created and untracked, checked first."""

    def __init__(
        self,
        reader: EdgeReader,
        checks: RelationChecks,
        conditions: ConditionCheck,
        write_store: str | None,
    ):
        self.reader, self.checks, self.conditions = reader, checks, conditions
        self.store, self.write_store = reader.store, write_store

    def assert_edge(
        self, name: str, source: str, target: str, naming: str | None = None
    ) -> tuple[str, str]:
        """Create the RelationDoc for source -[name]-> target. Returns (doc name, export id)."""
        self._check(name, source, target)
        src, tgt = (
            relativize(source, self.write_store),
            relativize(target, self.write_store),
        )  # written as the store reads itself
        doc_name = (naming or DEFAULT_NAMING).format(
            relation_type=name, source_id=src, target_id=tgt
        )
        path = self.store.root_of(self.write_store) / "relations" / f"{doc_name}.md"
        payload = _payload(name, src, tgt)
        return doc_name, self.store.create(
            "RelationDoc", doc_name, payload, path, self.write_store
        )

    def _check(self, name: str, source: str, target: str) -> None:
        rt = self.checks.relation_type(name)
        ok, why = self.checks.applies(name, model_of(source), model_of(target))
        if ok:
            ok, why = self.checks.cardinality_ok(name, source, target)
        if not ok:
            raise StoreError(why)
        if rt.get("condition"):
            self._check_condition(rt["condition"], source, target)

    def _check_condition(self, condition: str, source: str, target: str) -> None:
        holds, query = self.conditions.holds(condition, source, over=target)
        if not holds:
            raise StoreError(
                f"condition '{condition}' does not hold for {source} → {target} ({query})"
            )

    def negate_edge(
        self, name: str, source: str, target: str
    ) -> tuple[str | None, str]:
        for e in self.reader.sldb("source_id", source, name).edges:
            if e["target"] == target:
                rel_doc = e["metadata"]["relation_doc"]
                self.store.untrack(
                    rel_doc, e["metadata"].get("relation_store", "local")
                )
                return rel_doc, "untracked"
        for e in self.reader.edges_from(source, name).edges:
            if e["target"] == target and e["metadata"].get("origin") == "link":
                return (
                    None,
                    f"that edge is written in prose ({e['metadata']}); edit the text",
                )
        return None, "no such edge"


def _payload(name: str, src: str, tgt: str) -> dict[str, Any]:
    return {
        "title": f"{src} {name} {tgt}",
        "source_id": src,
        "target_id": tgt,
        "relation_type": name,
        "condition": "",
        "notes": "",
    }
