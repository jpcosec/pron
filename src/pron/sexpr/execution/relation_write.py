"""Writing one new edge in a move (spec 07, spec 11 §7, spec 04).

Asserting a relation writes a RelationDoc; a composition that asserts one writes the same
document the same way. Both go through here: the document is created with the naming
template the projection gives RelationDoc, the call is traced, and the write is recorded
in the move in one shape, so `undo` can invert either of them without knowing which said it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.ids import join_id

if TYPE_CHECKING:
    from pron.sexpr.resolving.verbs import Verbs
    from pron.sexpr.turn.move_context import MoveContext


class EdgeWriter:
    """The RelationDocs of a move, written with the projection's naming for them."""

    def __init__(self, projection: dict[str, Any], verbs: Verbs, write_store: str | None):
        self.projection, self.verbs, self.write_store = projection, verbs, write_store

    def __call__(self, relation: str, source: str, target: str, ctx: MoveContext) -> None:
        """Create the RelationDoc for one edge, trace it, and record it for undo."""
        naming = (self.projection.get("naming") or {}).get("RelationDoc")
        doc_name, _ = self.verbs.assert_edge(relation, source, target, naming)
        ctx.trace.append(f"docs create --model RelationDoc {doc_name}")
        ctx.record["writes"].append(
            relation_write(self.write_store, relation, source, target, doc_name)
        )


def relation_write(
    write_store: str | None, relation: str, source: str, target: str, doc_name: str
) -> dict[str, Any]:
    """What the move records about the RelationDoc an assert just created."""
    return {
        "verb": "assert",
        "address": join_id(write_store, "RelationDoc", doc_name),
        "after": {
            "source_id": source,
            "target_id": target,
            "relation_type": relation,
        },
        "done": True,
    }
