"""`kb_find`'s selection (spec 14 §3): the documents of a model and its family inside the
projection, narrowed by sldb `--where` predicates, one set per predicate, intersected (02).
An unparseable predicate is an error, never an empty set.
"""

from __future__ import annotations

from pron.kernel.ids import export_id, scope
from pron.mcp.mount import Mount
from pron.world.doc_id import DocId


class Finder:
    """A model and predicates to export ids, in the store's order."""

    def __init__(self, mount: Mount) -> None:
        self.mount = mount
        self.store = mount.world.store

    def __call__(self, model: str, where: list[str]) -> list[str]:
        self.mount.require_model(model)
        ids = self.family_ids(model)
        for predicate in where:
            keep = self.matching(model, predicate)
            ids = [i for i in ids if i in keep]
        return ids

    def family_ids(self, model: str) -> list[str]:
        family = [
            m for m in self.mount.models() if model in self.mount.world.family_of(m)
        ]
        out = []
        for r in self.store.docs():
            doc_id = DocId.of(r.model_name or "", r.name, r.store_name)
            if doc_id.model in family and self.mount.admits(doc_id):
                out.append(str(doc_id))
        return out

    def matching(self, model: str, predicate: str) -> set[str]:
        found: set[str] = set()
        for store in self.mount.stores():
            for address in self.store.find(scope(store, model), predicate):
                found.add(export_id(address))
        return found
