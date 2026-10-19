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
# fmt: off
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
# fmt: on


def _is_interior(module: str | None) -> bool:
    """El módulo es de una capa interior de sldb (sldb.<capa>... con capa en INTERIOR_LAYERS)."""
    return (
        module is not None
        and module.startswith("sldb.")
        and module.split(".")[1] in INTERIOR_LAYERS
    )


def _crossings(node: ast.AST) -> list[tuple[str, frozenset[str]]]:
    """(módulo interior, nombres importados) que un nodo import/from-import trae de sldb."""
    if (
        isinstance(node, ast.ImportFrom)
        and node.module is not None
        and _is_interior(node.module)
    ):
        return [(node.module, frozenset(a.name for a in node.names))]
    if isinstance(node, ast.Import):
        return [
            (a.name, frozenset({a.asname or a.name}))
            for a in node.names
            if _is_interior(a.name)
        ]
    return []


def _interior_imports(py: Path) -> set[tuple[str, str, frozenset[str]]]:
    """(archivo relativo, módulo interior, nombres importados) para cada cruce de capa."""
    rel = py.relative_to(SRC).as_posix()
    tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
    return {
        (rel, module, names)
        for node in ast.walk(tree)
        for module, names in _crossings(node)
    }


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
