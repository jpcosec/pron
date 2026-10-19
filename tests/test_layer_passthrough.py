"""Contrato de capas pron -> sldb, segunda mitad: los passthrough de `sldb.api`.

`sldb/api/__init__.py` re-exporta nombres directo desde `sldb.store`; importarlos desde
`sldb.api` sigue siendo interior. Separado de `test_layer_contract.py` (cruces directos a
capas interiores) por el límite de 100 líneas de código por archivo.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"


# La trampa: sldb/api/__init__.py re-exporta nombres directo desde sldb.store
# (EdgeIndex, JournalEntry, id builders...). Importarlos desde sldb.api sigue
# siendo conceptualmente interior: la capa api no los implementa, los pasa.
# La lista de abajo es el residuo aceptado hoy (documentado en contrato-de-capas.md);
# si alguien "arregla" un cruce moviendo el import a sldb.api y toma prestado uno
# de estos nombres, este test queda rojo salvo que se justifique expandir PASTHROUGH.
# fmt: off
API_PASSTHROUGH_FROM_STORE = frozenset({
    "EdgeIndex", "EdgeNodeRecord", "EdgeRebuildReport", "EdgeRecord", "JournalEntry", "JournalVerifyReport",
    "anchor_node_id", "bare", "doc_node_id", "field_node_id", "kind", "model_node_id",
    "relation_type_node_id", "section_node_id", "tag_node_id",
})

# Residuo passthrough ya existente y aceptado (no es un arreglo; es deuda de superficie).
PASSTHROUGH_RESIDUAL = {
    ("pron/world/graph.py", frozenset({"EdgeIndex"})),
    ("pron/world/graph_ids.py", frozenset({"bare", "doc_node_id", "field_node_id", "kind", "model_node_id", "relation_type_node_id", "tag_node_id"})),
}
# fmt: on


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
