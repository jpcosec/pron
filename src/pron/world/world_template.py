"""A world template (spec 01 §Plantilla): the words, projections and relation types a world
is born with, copied into its knowledge/ folder and tracked as documents.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from pron.world.store import Store

TEMPLATE_DIRS = {
    "anchors": ("AnchorDoc", "anchor-"),
    "projections": ("ProjectionDoc", "projection-"),
    "relations/types": ("RelationTypeDoc", "rt-"),
    "relations": ("RelationDoc", ""),
}


class WorldTemplate:
    """Copies a template's documents into one world, leaving the ones it already has alone."""

    def __init__(self, root: str | Path, pythonpath: str | None = None) -> None:
        self.root = Path(root).resolve()
        self.store = Store(self.root, pythonpath)

    def __call__(self, template: str | Path) -> list[str]:
        """Every template folder whose model the world registers, copied. Returns the export
        ids added."""
        template = Path(template).resolve()
        added: list[str] = []
        for sub, (model, prefix) in TEMPLATE_DIRS.items():
            src_dir = template / sub
            if src_dir.is_dir() and model in self.store.model_names():
                added += self._copy_folder(src_dir, sub, model, prefix)
        if added:
            self.store.update_index()
        return added

    def _copy_folder(
        self, src_dir: Path, sub: str, model: str, prefix: str
    ) -> list[str]:
        added: list[str] = []
        for src in sorted(src_dir.glob("*.md")):
            name = prefix + src.stem
            if self.store.doc(model, name) is not None:
                continue
            dst = self.root / "knowledge" / sub / src.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            self.store.track(dst, model, name)
            self.store.invalidate()
            added.append(f"{model}:{name}")
        return added


def apply_template(
    root: str | Path, template: str | Path, pythonpath: str | None = None
) -> list[str]:
    """Copy a world template into a world and track its documents (spec 01 §Plantilla):
    `anchors/*.md` as AnchorDoc, `projections/*.md` as ProjectionDoc, `relations/types/*.md`
    as RelationTypeDoc, `relations/*.md` as RelationDoc, each under <root>/knowledge/.
    A document whose name the world already has is left alone. Returns the export ids
    added."""
    return WorldTemplate(root, pythonpath)(template)
