"""Contrato de capas pron -> sldb: nadie importa capas interiores sin excepción documentada.

La regla vive en el docstring de `sldb/api/__init__.py` (repo sldb): la vía pública
de consumo es `sldb.api`; `sldb.store` / `sldb.runtime` / `sldb.core` son interiores.
Este test recorre `src/pron` y falla si aparece un import de una capa interior que
no esté en la lista explícita `ALLOWED` de abajo (mantenerla en sync con
`docs/contrato-de-capas.md`). También falla si una excepción permitida deja de
existir (sin reglas muertas).
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"

# Capas interiores de sldb: un import (directo o transitivo) de cualquiera de
# estas cruza el contrato salvo excepción documentada.
INTERIOR_LAYERS = ("store", "runtime", "core", "cli")

# Excepciones deliberadas: (archivo relativo a src/, módulo interior, nombres importados).
# Cada entrada corresponde a una fila de docs/contrato-de-capas.md, sección (b).
ALLOWED = {
    ("pron/docs_sync/generated_docs.py", "sldb.runtime.validation", frozenset({"extract_model_data", "render_model_markdown"})),
    ("pron/docs_sync/readme_render.py", "sldb.runtime.validation", frozenset({"render_model_markdown"})),
    ("pron/docs_sync/written_docs.py", "sldb.runtime.validation", frozenset({"extract_model_data"})),
    ("pron/lints.py", "sldb.store.diagnostics", frozenset({"diagnose_store"})),
    ("pron/mcp/schema/model_create.py", "sldb.core.exceptions", frozenset({"SLDBModelError"})),
    ("pron/mcp/schema/model_extend.py", "sldb.core.exceptions", frozenset({"SLDBModelError"})),
    ("pron/sexpr/resolving/pending_match.py", "sldb.store.query_engine.filter", frozenset({"DocumentFilter"})),
    ("pron/sexpr/resolving/pending_match.py", "sldb.store.query_engine.where_parse", frozenset({"WherePredicateError"})),
    ("pron/world/storage/document_reader.py", "sldb.store.io", frozenset({"load_documents_index"})),
    ("pron/world/storage/document_reader.py", "sldb.store.query", frozenset({"load_runtime_documents"})),
    ("pron/world/storage/document_tracker.py", "sldb.runtime.validation", frozenset({"render_model_markdown", "validate_model_data_roundtrip", "validate_model_input_roundtrip"})),
    ("pron/world/storage/linked_stores.py", "sldb.core.exceptions", frozenset({"SLDBStoreError"})),
    ("pron/world/storage/linked_stores.py", "sldb.store", frozenset({"documents_hash"})),
    ("pron/world/storage/linked_stores.py", "sldb.store.io", frozenset({"load_store_index"})),
    ("pron/world/storage/linked_stores.py", "sldb.store.layout", frozenset({"project_root", "store_exists"})),
    ("pron/world/storage/linked_stores.py", "sldb.store.runtime_cache", frozenset({"new_operation"})),
    ("pron/world/storage/model_editor.py", "sldb.core.exceptions", frozenset({"SLDBError"})),
    ("pron/world/storage/model_registry.py", "sldb.core.exceptions", frozenset({"SLDBModelError"})),
    ("pron/world/storage/model_registry.py", "sldb.store.io", frozenset({"load_documents_index", "load_models_index"})),
    ("pron/world/storage/payload_editor.py", "sldb.core.exceptions", frozenset({"SLDBPayloadSaveError"})),
    ("pron/world/storage/structural_query.py", "sldb.store.query", frozenset({"find_structural", "get_structural", "glob_structural", "list_structural"})),
    ("pron/world/storage/structural_query.py", "sldb.store.query_engine.filter", frozenset({"DocumentFilter"})),
    ("pron/world/storage/structural_query.py", "sldb.store.query_engine.where_parse", frozenset({"WherePredicateError"})),
}


def _interior_imports(py: Path) -> set[tuple[str, str, frozenset[str]]]:
    """(archivo relativo, módulo interior, nombres importados) para cada cruce de capa."""
    rel = py.relative_to(SRC).as_posix()
    tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
    found: set[tuple[str, str, frozenset[str]]] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("sldb."):
            layer = node.module.split(".")[1]
            if layer in INTERIOR_LAYERS:
                names = frozenset(a.name for a in node.names)
                found.add((rel, node.module, names))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("sldb."):
                    layer = alias.name.split(".")[1]
                    if layer in INTERIOR_LAYERS:
                        found.add((rel, alias.name, frozenset({alias.asname or alias.name})))
    return found


# La trampa: sldb/api/__init__.py re-exporta nombres directo desde sldb.store
# (EdgeIndex, JournalEntry, id builders...). Importarlos desde sldb.api sigue
# siendo conceptualmente interior: la capa api no los implementa, los pasa.
# La lista de abajo es el residuo aceptado hoy (documentado en contrato-de-capas.md);
# si alguien "arregla" un cruce moviendo el import a sldb.api y toma prestado uno
# de estos nombres, este test queda rojo salvo que se justifique expandir PASTHROUGH.
API_PASSTHROUGH_FROM_STORE = frozenset({
    "EdgeIndex",
    "EdgeNodeRecord",
    "EdgeRebuildReport",
    "EdgeRecord",
    "JournalEntry",
    "JournalVerifyReport",
    "anchor_node_id",
    "bare",
    "doc_node_id",
    "field_node_id",
    "kind",
    "model_node_id",
    "relation_type_node_id",
    "section_node_id",
    "tag_node_id",
})

# Residuo passthrough ya existente y aceptado (no es un arreglo; es deuda de superficie).
PASSTHROUGH_RESIDUAL = {
    ("pron/world/graph.py", frozenset({"EdgeIndex"})),
    ("pron/world/graph_ids.py", frozenset({"bare", "doc_node_id", "field_node_id", "kind", "model_node_id", "relation_type_node_id", "tag_node_id"})),
}


def _api_passthrough_imports(py: Path) -> set[tuple[str, frozenset[str]]]:
    """(archivo relativo, nombres) importados desde `sldb.api` que son passthrough de sldb.store."""
    rel = py.relative_to(SRC).as_posix()
    tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
    found: set[tuple[str, frozenset[str]]] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in ("sldb.api",):
            names = frozenset(a.name for a in node.names)
            leaked = names & API_PASSTHROUGH_FROM_STORE
            if leaked:
                found.add((rel, leaked))
    return found


def test_no_layer_leaks():
    actual = set()
    for py in SRC.rglob("*.py"):
        if py.is_file():
            actual |= _interior_imports(py)

    leaked = actual - ALLOWED
    stale = ALLOWED - actual

    assert not leaked, (
        "Imports de capas interiores de sldb sin excepción documentada:\n"
        + "\n".join(f"  {f}:{m} -> {sorted(n)}" for f, m, n in sorted(leaked))
        + "\nDocumentarlos en docs/contrato-de-capas.md y agregarlos a ALLOWED."
    )
    assert not stale, (
        "Excepciones permitidas que ya no existen en el árbol (reglas muertas):\n"
        + "\n".join(f"  {f}:{m} -> {sorted(n)}" for f, m, n in sorted(stale))
        + "\nQuitarlas de ALLOWED."
    )


def test_no_new_api_passthrough_leaks():
    """La trampa: `sldb.api` re-exporta nombres directo desde `sldb.store`.

    Importar esos nombres desde `sldb.api` no es un arreglo de capas: sigue siendo
    interior detrás de un passthrough. Este test fija el residuo actual
    (PASSTHROUGH_RESIDUAL) y falla si alguien toma prestado otro nombre passthrough.
    """
    actual = set()
    for py in SRC.rglob("*.py"):
        if py.is_file():
            actual |= _api_passthrough_imports(py)

    leaked = actual - PASSTHROUGH_RESIDUAL
    stale = PASSTHROUGH_RESIDUAL - actual

    assert not leaked, (
        "Nombres passthrough de sldb.store comprados a través de sldb.api (fuga conceptual):\n"
        + "\n".join(f"  {f} -> {sorted(n)}" for f, n in sorted(leaked))
        + "\nNo es un arreglo: sldb.api los re-exporta sin implementarlos. Justificar y mover a PASSTHROUGH_RESIDUAL."
    )
    assert not stale, (
        "Residuos passthrough que ya no se importan (reglas muertas):\n"
        + "\n".join(f"  {f} -> {sorted(n)}" for f, n in sorted(stale))
        + "\nQuitarlos de PASSTHROUGH_RESIDUAL."
    )