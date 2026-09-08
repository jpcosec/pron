"""Track and verify the executable documentation in SLDB.

Implements atom-pron-cli-and-modules-are-documented-from-source: every base CLI
command and every public module surface is a tracked, checkable SLDB document,
not free-floating prose. Reuses SldbBridge and the infra layer instead of
talking to sldb on its own, so this stays one write operation among the rest.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import cast

import yaml
from deskops.models import AtomDoc
from pydantic import BaseModel, JsonValue
from sldb.models.knowledge_surface import CliCommandDoc, SurfaceDoc
from sldb.runtime.validation import extract_model_data, render_model_markdown

from ..bridges.sldb_bridge import SldbBridge
from ..documentation import DocumentSpec, describe_public_surfaces
from ..infra.projector import model_add, refresh


def synchronize_documentation(root: Path, *, check: bool) -> tuple[bool, str]:
    """Regenerate or check the tracked docs and their SLDB roundtrip and integrity."""
    root = Path(root).resolve()
    sldb = SldbBridge(root)
    try:
        atoms = _read_atoms(root)
        specs = describe_public_surfaces(root, atoms)
        if not check:
            ok, msg = _write_specs(root, sldb, specs)
            if not ok:
                return False, msg
            sldb = SldbBridge(root)  # writes above staled the cached bridge
        return _verify(root, sldb, specs)
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as error:
        return False, f"documentation: {error}"


def _read_atoms(root: Path) -> dict[str, str]:
    atoms = {}
    for path in (root / "knowledge/atoms").glob("*.md"):
        if path.name == "tag-namespaces.yaml":
            continue
        model = AtomDoc.model_validate(
            extract_model_data(AtomDoc, path.read_text(encoding="utf-8"))
        )
        atoms[model.id] = model.answer
    return atoms


def _render(spec: DocumentSpec) -> str:
    model = CliCommandDoc if spec.model == "CliCommandDoc" else SurfaceDoc
    return cast(
        str,
        render_model_markdown(
            model, model.model_validate(spec.payload).model_dump(mode="json")
        ),
    )


def _write_specs(
    root: Path, sldb: SldbBridge, specs: tuple[DocumentSpec, ...]
) -> tuple[bool, str]:
    registered = set(sldb.model_names())
    for name in ("CliCommandDoc", "SurfaceDoc"):
        if name not in registered:
            ok, msg = model_add(root, f"sldb.models.knowledge_surface:{name}")
            if not ok:
                return False, msg
    tracked = {(doc.model_name, doc.name) for doc in sldb.documents()}
    for spec in specs:
        path = root / "knowledge" / spec.folder / f"{spec.name}.md"
        model = CliCommandDoc if spec.model == "CliCommandDoc" else SurfaceDoc
        if (spec.model, spec.name) not in tracked:
            path.parent.mkdir(parents=True, exist_ok=True)
            sldb.create_doc(spec.payload, model, spec.name, path)
        else:
            path.write_text(_render(spec) + "\n", encoding="utf-8")
    return refresh(root)


def _verify(
    root: Path, sldb: SldbBridge, specs: tuple[DocumentSpec, ...]
) -> tuple[bool, str]:
    for spec in specs:
        path = root / "knowledge" / spec.folder / f"{spec.name}.md"
        expected = _render(spec) + "\n"
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            return False, f"documentation_drift: regenerate with `pron docs` ({path})"
    loaded = sldb.documents()
    tracked = {(doc.model_name, doc.name) for doc in loaded}
    if any((spec.model, spec.name) not in tracked for spec in specs):
        return False, "documentation_tracking: generated documentation is not tracked in SLDB"
    tracked_paths = {Path(doc.path).resolve() for doc in loaded}
    for path in (root / "knowledge").rglob("*.md"):
        if path.resolve() not in tracked_paths:
            return False, f"documentation_tracking: authored document not tracked ({path})"
    namespaces = yaml.safe_load(
        (root / "knowledge/atoms/tag-namespaces.yaml").read_text()
    )["namespaces"]
    models: dict[str, type[BaseModel]] = {}
    for name in {doc.model_name for doc in loaded}:
        ref = sldb.registered_model_ref(name)
        if ref:
            models[name] = sldb.resolve_model(ref)
    generated = {(spec.model, spec.name) for spec in specs}
    for document in loaded:
        if (document.model_name, document.name) not in generated:
            continue  # pre-existing atom quality is a separate concern from this feature
        if not _valid_tags(document.payload.get("tags"), namespaces):
            return False, f"documentation_tags: {document.name}"
        if not document.payload.get("provenance"):
            return False, f"documentation_provenance: {document.name}"
        model = models.get(document.model_name)
        if model is None:
            continue
        markdown = render_model_markdown(model, document.payload)
        roundtrip = model.model_validate(
            extract_model_data(model, markdown)
        ).model_dump(mode="json")
        if roundtrip != document.payload:
            return False, f"documentation_roundtrip: {document.name}"
    ok, out = _stores_check(root)
    if not ok:
        return False, out
    if "PASS: store integrity" not in out:
        return False, out.strip()
    return True, f"{len(loaded)} documentos verificados, store íntegro."


def _valid_tags(tags: JsonValue, namespaces: dict[str, dict[str, object]]) -> bool:
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        return False
    strings = [tag for tag in tags if isinstance(tag, str)]
    if any(
        sum(tag.startswith(f"{required}:") for tag in strings) != 1
        for required in ("domain", "kind", "impl")
    ):
        return False
    for tag in strings:
        namespace, separator, value = tag.partition(":")
        if not separator or namespace not in namespaces:
            return False
        allowed = namespaces[namespace].get("values")
        if isinstance(allowed, dict) and value not in allowed:
            return False
    return True


def _stores_check(root: Path) -> tuple[bool, str]:
    """Read-only integrity check; no bridge/infra wrapper exists for this yet."""
    result = subprocess.run(
        [sys.executable, "-m", "sldb", "stores", "check", "--store", str(root / ".sldb")],
        capture_output=True,
        text=True,
    )
    out = (result.stdout + result.stderr).strip()
    if result.returncode:
        return False, out.splitlines()[-1] if out else "sldb stores check falló"
    return True, out
