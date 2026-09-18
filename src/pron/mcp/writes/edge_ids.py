"""The RelationDoc of an edge (spec 03, 10 §2.2, 14 §4): what `kb_edge_expire` forgets.

An edge a session asserted is a RelationDoc named with the projection's naming for
RelationDoc — by default `<relation>--<source>--<target>`, the ids written as the write store
reads itself — exactly as `EdgeAssertion.assert_edge` names it. A RelationDoc written some
other way (by hand, by another naming) is found by what it links: the authored edges from
the source, read straight from the RelationDocs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.ids import join_id, relativize
from pron.sexpr.resolving.edge_assertion import DEFAULT_NAMING

if TYPE_CHECKING:
    from pron.session import Session


class EdgeIds:
    """The export id of the RelationDoc behind `source -[relation]-> target`."""

    def __init__(self, session: Session):
        self.session = session

    def __call__(self, relation: str, source: str, target: str) -> str:
        """The authored RelationDoc if there is one, else the id `assert` would give it (and
        then the evaluation says there is no such document)."""
        return self.authored(relation, source, target) or self.named(
            relation, source, target
        )

    def named(self, relation: str, source: str, target: str) -> str:
        store = self.session.write_store
        naming = (self.session.projection.get("naming") or {}).get("RelationDoc")
        name = (naming or DEFAULT_NAMING).format(
            relation_type=relation,
            source_id=relativize(source, store),
            target_id=relativize(target, store),
        )
        return join_id(store, "RelationDoc", name)

    def authored(self, relation: str, source: str, target: str) -> str | None:
        reader = self.session.verbs.reader
        for e in reader.sldb("source_id", source, relation).edges:
            if e["target"] == target:
                meta = e["metadata"]
                store = meta.get("relation_store", "local")
                store = None if store == "local" else store
                return join_id(store, "RelationDoc", meta["relation_doc"])
        return None
