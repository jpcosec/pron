"""anchor add: declare a new grammar symbol as a tracked AnchorDoc.

Implements atom-the-anchor-table-is-declared-as-sldb-documents-not-code and
atom-anchor-ref-is-a-typed-string-with-a-scheme-per-kind: the anchor table
grows by writing SLDB documents, never by editing code.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from knowledge.core.anchors import KINDS
from knowledge.infra.projector import project

# atom-anchor-kinds-partition-what-a-symbol-can-refer-to: the closed kind
# partition, each with its typed-ref scheme.
REF_PATTERNS: dict[str, str] = {
    "model": r"model:[A-Z][A-Za-z0-9_]*",
    "doc": r"doc:[a-z0-9][a-z0-9_-]*",
    "relation": r"edge:[a-z][a-z0-9_]*(:out|:in)?",
    "operation": r"op:[a-z][a-z0-9_]*",
    "projection": r"(fields:[a-z][a-z0-9_]*(,[a-z][a-z0-9_]*)*|view:[a-z][a-z0-9_]*)",
}

SYMBOL_PATTERN = r"^[a-z][a-z0-9_-]*$"

ANCHOR_TAGS = [
    "system:knowledge",
    "entity:anchor",
    "domain:knowledge_representation",
    "kind:software",
    "impl:here",
]

ANCHORDOC_MODEL = "AnchorDoc"


class AnchorAddError(ValueError):
    """Invalid anchor declaration: explicit error, no partial write."""


def validate_ref(kind: str, ref: str) -> None:
    """The ref must match the scheme declared for its kind."""
    if kind not in KINDS:
        raise AnchorAddError(
            f"kind inválido: '{kind}'. Kinds válidos: {'|'.join(KINDS)}"
        )
    if not re.fullmatch(REF_PATTERNS[kind], ref):
        raise AnchorAddError(
            f"ref inválido para kind '{kind}': '{ref}'. "
            f"Esquema esperado: {REF_PATTERNS[kind]}"
        )


def anchor_add(root: Path, symbol: str, kind: str, ref: str, motive: str) -> tuple[bool, str]:
    """Write the AnchorDoc, track it in sldb, and rebuild the graph."""
    root = Path(root)
    if not re.fullmatch(SYMBOL_PATTERN, symbol):
        return False, (
            f"símbolo inválido: '{symbol}'. Debe coincidir con {SYMBOL_PATTERN}"
        )
    try:
        validate_ref(kind, ref)
    except AnchorAddError as e:
        return False, str(e)
    if not motive.strip():
        return False, "motive requerido: --motive '<texto>'"

    doc_path = root / "knowledge" / "anchors" / f"anchor-{symbol}.md"
    if doc_path.exists():
        return False, f"ya existe un anchor para '{symbol}': {doc_path}"

    tags_block = "\n".join(f"- {t}" for t in ANCHOR_TAGS)
    content = (
        "---\n"
        f"id: anchor-{symbol}\n"
        f"symbol: {symbol}\n"
        f"kind: {kind}\n"
        f"ref: {ref}\n"
        "tags:\n"
        f"{tags_block}\n"
        f"provenance: knowledge anchor add ({symbol})\n"
        "---\n\n"
        f"# {symbol}\n\n"
        "## Motive\n\n"
        f"{motive.strip()}\n"
    )
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(content)

    cmd = [
        sys.executable,
        "-m",
        "sldb",
        "docs",
        "track",
        str(doc_path),
        "--model",
        ANCHORDOC_MODEL,
        "--store",
        str(root / ".sldb"),
        "--pythonpath",
        str(root),
        "--force",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        doc_path.unlink(missing_ok=True)
        out = (r.stderr or r.stdout).strip().splitlines()
        return False, out[-1] if out else "sldb docs track falló"

    ok, msg = project(root)
    if not ok:
        return False, f"anchor escrito pero el rebuild del grafo falló: {msg}"
    return True, f"anchor '{symbol}' declarado ({kind} {ref}) y grafo regenerado."
