"""`@family/{familia}` (spec 14 §2.2): the documents of the models whose `__family__` or
class semantics (`__semantics__`) name that family. Read from the models, never assumed.
"""

from __future__ import annotations

from pron.mcp.found import Found
from pron.mcp.mount import Mount
from pron.world.doc_id import DocId


class FamilySelector:
    """A family name to the documents of the models that declare it."""

    def __init__(self, mount: Mount) -> None:
        self.mount = mount

    def __call__(self, family: str) -> Found:
        found = Found()
        for model in self.models(family):
            for store in self.mount.stores():
                for record in self.mount.world.store.docs_of(model, store):
                    found.add(DocId.of(model, record.name, store), f"family:{model}")
        if not found.docs:
            found.notes.append(f"@family/{family}: no model of this world declares it")
        return found

    def models(self, family: str) -> list[str]:
        return [m for m in self.mount.models() if family in self.declared(m)]

    def declared(self, model: str) -> list[str]:
        """The family names a model declares: its `__family__` and its semantics' values."""
        cls = self.mount.world.model_type(model)
        names = [getattr(cls, "__family__", None)]
        for values in (getattr(cls, "__semantics__", None) or {}).values():
            names.extend(values if isinstance(values, list) else [values])
        return [str(n) for n in names if n]
