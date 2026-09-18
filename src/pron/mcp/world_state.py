"""The state of a mounted world (spec 14 §2.3): its schema, its recent ledger, its store's
integrity and the legal transitions from a state. Read-only views over what the world
already declares and records.
"""

from __future__ import annotations

from typing import Any

from pron.mcp.doc_entries import DocEntries
from pron.mcp.mount import Mount
from pron.mcp.transitions import Transitions
from pron.world.doc_id import DocId

RELATION_KEYS = (
    "name",
    "source_types",
    "target_types",
    "cardinality",
    "direction",
    "axis",
    "condition",
    "description",
)
RECENT = 20


class WorldState:
    """`_schema`, `_ledger/recent`, `_store/integrity`, `_transitions/{Model}/{state}`."""

    def __init__(self, mount: Mount) -> None:
        self.mount = mount
        self.world = mount.world

    def __call__(self, segments: list[str]) -> dict[str, Any]:
        path = "/".join(segments[:2])
        if path == "_schema" and len(segments) == 1:
            return self.schema()
        if path == "_ledger/recent":
            return self.ledger()
        if path == "_store/integrity":
            return self.integrity()
        if segments[0] == "_transitions" and len(segments) == 3:
            return Transitions(self.mount)(segments[1], segments[2])
        raise LookupError(f"no state address /{'/'.join(segments)}")

    def schema(self) -> dict[str, Any]:
        """The projection's models with their fields, and every relation type (spec 14 §2.3)."""
        models = [
            {
                "name": m,
                "family": self.world.family_of(m),
                "fields": self.world.schema(m),
            }
            for m in self.mount.models()
        ]
        relations = [
            {k: rt.get(k) for k in RELATION_KEYS}
            for rt in self.world.relation_types().values()
        ]
        return {"models": models, "relation_types": relations}

    def ledger(self) -> dict[str, Any]:
        """The last moves, newest first: who, which form, what it read and wrote, the hashes."""
        docs = self.world.store.docs_of("MoveDoc", "*")
        docs.sort(key=lambda d: d.payload.get("at", ""), reverse=True)
        return {"moves": [self._move(d) for d in docs[:RECENT]]}

    def _move(self, record: Any) -> dict[str, Any]:
        p, doc_id = record.payload, DocId.of("MoveDoc", record.name, record.store_name)
        r = p.get("record") or {}
        return {
            "uri": DocEntries(self.mount).uri(doc_id),
            **{k: p.get(k) for k in ("id", "at", "speaker", "outcome", "sentence")},
            "reads": {"queries": r.get("queries", []), "edges": r.get("edges", [])},
            "writes": r.get("writes", []),
            "hash_before": p.get("hash_before"),
            "hash_after": p.get("hash_after"),
        }

    def integrity(self) -> dict[str, Any]:
        """What `pron check` would say, and the edge index's own problems (spec 14 §2.3)."""
        from sldb.api import check_edges

        from pron.lints import run_lints

        edges = check_edges(
            self.world.store.sp, exclude_tags=self.world.graph.exclude_tags
        )
        lints = run_lints(self.world)
        return {
            "ok": not lints and not edges.errors and not edges.stale,
            "lints": lints,
            "edges": edges.model_dump(),
        }
