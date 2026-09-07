"""Write operations: create, assert, ingest. Every write carries provenance.

Implements atom-the-canonical-operations-are-check-next-assert-create-ingest-return
(write half) and atom-write-operations-record-provenance-of-the-command-that-produced-them:
each write goes through sldb document operations and records the full evaluated
s-expression (plus a UTC timestamp) as the provenance of the produced doc.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from pron.core.results import OperationResult, SemanticError


def create(evaluator, args: list, projection, command: str = ""):
    """(create <model-sym> "name" <key> <value> ...): define a tracked doc.

    Entity creation for symbols/relations/models is the anchor/model infra
    (pron anchor add / model add); create here defines doc entities of
    any registered model.
    """
    if len(args) < 2:
        return OperationResult(
            status="error",
            payload="create requiere (create <model> \"name\" <key> <value> ...)",
        )
    anchor = evaluator._model_anchor(args[0])
    if isinstance(anchor, SemanticError):
        return OperationResult(status="error", payload=anchor.message)
    name = args[1]
    if not isinstance(name, str) or not name.strip():
        return OperationResult(
            status="error", payload="create requiere un nombre (string) como segundo argumento"
        )
    payload, error = _pairs(args[2:])
    if error:
        return OperationResult(status="error", payload=error)
    model_ref = anchor.ref.removeprefix("model:")
    return _write_doc(evaluator, payload, name.strip(), model_ref, command)


def assert_(evaluator, args: list, projection, command: str = ""):
    """(assert "hecho" <key> <value> ...): añade un hecho como verdadero."""
    if not args or not isinstance(args[0], str) or not args[0].strip():
        return OperationResult(
            status="error", payload="assert requiere el hecho como string: (assert \"...\")"
        )
    fact = args[0].strip()
    extra, error = _pairs(args[1:])
    if error:
        return OperationResult(status="error", payload=error)
    extra["fact"] = fact
    name = f"fact-{_slug(fact)}-{_stamp()}"
    return _write_doc(evaluator, extra, name, "pron.bridges.write_models:FactDoc", command)


def ingest(evaluator, args: list, projection, command: str = ""):
    """(ingest "título" "cuerpo"): registra una proposición/documento."""
    if len(args) < 2 or not all(isinstance(a, str) and a.strip() for a in args[:2]):
        return OperationResult(
            status="error",
            payload="ingest requiere título y cuerpo: (ingest \"título\" \"cuerpo\")",
        )
    title, body = args[0].strip(), args[1].strip()
    extra, error = _pairs(args[2:])
    if error:
        return OperationResult(status="error", payload=error)
    extra["title"] = title
    extra["proposition"] = body
    name = f"proposition-{_stamp()}"
    return _write_doc(evaluator, extra, name, "pron.bridges.write_models:PropositionDoc", command)


def _pairs(args: list) -> tuple[dict, str | None]:
    """Consume trailing key value pairs (Symbol key, literal value)."""
    from pron.core.sexpr import Symbol

    if len(args) % 2 != 0:
        return {}, "los pares clave-valor deben venir en pares"
    payload: dict = {}
    for i in range(0, len(args), 2):
        key, value = args[i], args[i + 1]
        if not isinstance(key, Symbol):
            return {}, f"clave inválida: {key!r} (debe ser un símbolo)"
        payload[key.name] = value.name if isinstance(value, Symbol) else value
    return payload, None


def _write_doc(
    evaluator, payload: dict, name: str, model_ref: str, command: str
) -> OperationResult:
    """Write one doc via sldb document operations, with provenance + rebuild."""
    root: Path = evaluator.sldb.root
    if ":" not in model_ref:
        model_ref = evaluator.sldb.registered_model_ref(model_ref)
        if model_ref is None:
            return OperationResult(
                status="error", payload=f"modelo no registrado en el store: '{model_ref}'"
            )
    try:
        model_type = evaluator.sldb.resolve_model(model_ref)
    except Exception as e:  # noqa: BLE001 - surfaced as explicit result, not crash
        return OperationResult(status="error", payload=f"modelo no resoluble '{model_ref}': {e}")

    model_name = model_type.__name__
    payload = {**payload, "id": payload.get("id", name)}
    fields = model_type.model_fields
    if "provenance" in fields:
        payload.setdefault("provenance", command or f"(write {name})")
        payload.setdefault("provenance_at", _utc_now())

    doc_path = _doc_path(root, model_type, name)
    try:
        evaluator.sldb.create_doc(payload, model_type, name, doc_path)
    except Exception as e:  # noqa: BLE001 - surfaced as explicit result, not crash
        return OperationResult(status="error", payload=f"sldb docs create falló: {e}")

    # fresh reads must see the new doc; indexes and graph must follow the store
    evaluator.sldb._docs = None
    from pron.infra.projector import refresh

    ok, msg = refresh(root)
    if not ok:
        return OperationResult(
            status="error", payload=f"doc escrito pero el rebuild del grafo falló: {msg}"
        )
    return OperationResult(
        status="ok",
        payload={"created": name, "model": model_name, "provenance": payload.get("provenance", "")},
        refs=[str(doc_path)],
    )


def _doc_path(root: Path, model_type, name: str) -> Path:
    """Where the produced doc lives: the model's declared workspace."""
    workspace = (getattr(model_type, "__semantics__", {}) or {}).get("workspace") or [
        "knowledge",
        "docs",
    ]
    return root.joinpath(*workspace) / f"{name}.md"


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]
    return slug or "nota"


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
