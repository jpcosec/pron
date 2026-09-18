"""The authored edges of one relation type (spec 03, 10 §2.2): its RelationDocs in every
store of the session's projection, read straight from sldb — the edges a change to the type
would judge (spec 14 §4, nivel 2).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.ids import export_id, qualify, scope
from pron.world.doc_id import DocId

if TYPE_CHECKING:
    from pron.session import Session


class RuleEdges:
    """Every RelationDoc of a relation type, as `{doc, source, target, condition}`."""

    def __init__(self, session: Session):
        self.session = session
        self.store = session.world.store

    def __call__(self, relation: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for s in self.session.verbs.stores:
            sc = scope(s, "RelationDoc", family=False)
            for address in self.store.find(sc, f'relation_type = "{relation}"'):
                out.append(self._edge(export_id(address)))
        return out

    def _edge(self, eid: str) -> dict[str, Any]:
        d = DocId.parse(eid)
        p = self.store.payload(d)
        here = None if d.store in (None, "local") else d.store
        return {
            "doc": eid,
            "source": qualify(p["source_id"], here),
            "target": qualify(p["target_id"], here),
            "condition": p.get("condition") or "",
        }
