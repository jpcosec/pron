"""Read operations: check, next, return. No mutation, always refs.

Implements atom-the-canonical-operations-are-check-next-assert-create-ingest-return
(read half) and atom-every-read-response-carries-refs-for-auditability.
"""

from __future__ import annotations

from knowledge.core.results import OperationResult, Resolved


def check(evaluator, args: list, projection):
    """Read without mutation: docs sets, single docs, or rel traversals."""
    from knowledge.core.evaluator import project_payload

    if not args:
        return OperationResult(status="error", payload="check requiere un argumento")
    target = args[0]

    if isinstance(target, Resolved):
        return OperationResult(
            status="ok",
            payload=project_payload(target.payload, projection),
            refs=[target.path],
        )

    if isinstance(target, dict) and target.get("kind") == "docs":
        docs = target["docs"]
        return OperationResult(
            status="ok",
            payload=[project_payload(dict(d.payload), projection) for d in docs],
            refs=[str(d.path) for d in docs],
        )

    if isinstance(target, dict) and target.get("kind") == "rel":
        return _check_rel(evaluator, target, projection)

    if isinstance(target, dict) and target.get("kind") == "nodes":
        payloads, refs = [], []
        for nid in target["node_ids"]:
            schema = evaluator.kgdb.node(nid) or {}
            semantics = schema.get("semantics") or {}
            payloads.append(
                project_payload(dict(semantics), projection) or {"node_id": nid}
            )
            refs.append(nid)
        return OperationResult(status="ok", payload=payloads, refs=refs)

    return OperationResult(
        status="error", payload=f"check no sabe leer {type(target).__name__}"
    )


def _check_rel(evaluator, rel: dict, projection):
    """Traverse a kgdb relation from a resolved source document."""
    from knowledge.core.evaluator import project_payload

    anchor, source = rel["anchor"], rel["source"]
    if not isinstance(source, Resolved):
        return OperationResult(
            status="error", payload="rel requiere un doc resuelto como origen"
        )
    if not evaluator.kgdb.available():
        return OperationResult(
            status="error",
            payload="no hay grafo materializado; corre: knowledge project",
        )
    if evaluator.kgdb.is_stale(evaluator.sldb.store_hash()):
        return OperationResult(
            status="error",
            payload="el grafo está desactualizado respecto al store; corre: knowledge project",
        )

    ref = anchor.ref.removeprefix("edge:")
    relation, _, direction = ref.partition(":")
    node_id = evaluator.kgdb.document_node_id(source.model, source.name)

    if direction == "in":
        node_ids = evaluator.kgdb.edges_to(node_id, relation)
    else:
        node_ids = [
            e["target_id"] for e in evaluator.kgdb.edges_from(node_id, relation)
        ]

    payloads, refs = [], [source.path]
    for nid in node_ids:
        schema = evaluator.kgdb.node(nid) or {}
        semantics = schema.get("semantics") or {}
        payloads.append(project_payload(dict(semantics), projection))
        refs.append(nid)
    return OperationResult(status="ok", payload=payloads, refs=refs)


def next_(evaluator, args: list, projection):
    """The next document by state order (model-defined; default: name order)."""
    from knowledge.core.evaluator import project_payload

    if not args or not (isinstance(args[0], dict) and args[0].get("kind") == "docs"):
        return OperationResult(status="error", payload="next requiere (docs <model>)")
    docs = sorted(args[0]["docs"], key=_state_order)
    open_docs = [d for d in docs if _status(d) not in ("done", "complete", "closed")]
    if not open_docs:
        return OperationResult(status="ok", payload=None, refs=[])
    chosen = open_docs[0]
    return OperationResult(
        status="ok",
        payload=project_payload(dict(chosen.payload), projection),
        refs=[str(chosen.path)],
    )


def return_(evaluator, args: list, projection):
    """Query stored facts; alias of check over its argument for the read core."""
    return check(evaluator, args, projection)


def _status(doc) -> str:
    return str(doc.payload.get("status", "")).lower()


_STATE_RANK = {"active": 0, "in_progress": 0, "ready": 1, "pending": 2, "": 3}


def _state_order(doc) -> tuple[int, str]:
    return (_STATE_RANK.get(_status(doc), 3), doc.name)
