"""Migration of v1 atoms (deskops AtomDoc markdown) into a world's Atom model (spec 08).

Per file: extract with the old template (the same as Atom's with `five_wh_one_plus`
instead of `question`), rename that key, retag system:knowledge → system:pron, drop the
impl: tags (that fact becomes an implements edge later), provenance null → "", create
with the new model under knowledge/atoms/ keeping the document name.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sldb.runtime.validation import extract_payload

from pron.models.atom import Atom
from pron.world import World

V1_TEMPLATE = Atom.__template__.replace("question: ⸢rev•question⸥", "five_wh_one_plus: ⸢rev•five_wh_one_plus⸥").replace(
    "provenance: ⸢rev•provenance⸥", "provenance: ⸢optrev•provenance⸥")


def convert(payload: dict[str, Any]) -> dict[str, Any]:
    tags = []
    for t in payload.get("tags") or []:
        if t.startswith("impl:"):
            continue
        tags.append("system:pron" if t == "system:knowledge" else t)
    return {
        "id": payload["id"],
        "title": payload["title"],
        "question": payload.get("five_wh_one_plus") or payload.get("question"),
        "answer": payload.get("answer", ""),
        "tags": tags,
        "provenance": payload.get("provenance") or "",
    }


def migrate_atoms(world: World, src_dir: Path) -> dict[str, Any]:
    store = world.store
    if "Atom" not in world.model_names():
        store.register_model("pron.models:Atom")
    done, skipped, failed = [], [], []
    for path in sorted(src_dir.glob("atom-*.md")):
        name = path.stem
        if store.doc("Atom", name) is not None:
            skipped.append(name); continue
        try:
            payload = convert(extract_payload(V1_TEMPLATE, path.read_text(encoding="utf-8")))
            impl_here = any(t == "impl:here" for t in (extract_payload(V1_TEMPLATE, path.read_text(encoding="utf-8")).get("tags") or []))
            store.create("Atom", name, payload, world.root / "knowledge" / "atoms" / path.name)
            done.append({"name": name, "impl_here": impl_here})
        except Exception as e:  # noqa: BLE001 - report, keep going
            failed.append({"name": name, "error": str(e)[:200]})
    return {"migrated": len(done), "skipped": len(skipped), "failed": failed, "impl_here": [d["name"] for d in done if d["impl_here"]]}
