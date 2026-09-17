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
    from pron.session import Session


def write_edge(
    session: "Session",
    relation: str,
    source: str,
    target: str,
    trace: list[str],
    record: dict[str, Any],
) -> None:
    """Create the RelationDoc for one edge, trace it, and record it for undo."""
    naming = (session.projection.get("naming") or {}).get("RelationDoc")
    doc_name, _ = session.verbs.assert_edge(relation, source, target, naming)
    trace.append(f"docs create --model RelationDoc {doc_name}")
    record["writes"].append(
        relation_write(session.write_store, relation, source, target, doc_name)
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
