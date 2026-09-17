"""The documents written where they live (spec 07, spec 08 step 9) — explanations, anchors,
projections, the moves of the ledger and the ReadmeDoc — tracked from their files like the
spec chapters; one is re-tracked when its payload changed. This is what lets the whole store
be rebuilt from the repo.
"""

from __future__ import annotations

from pathlib import Path

from pron.docs_sync.doc_drift import drifted
from pron.world.world import World

EXPLANATIONS_DIR = Path("knowledge") / "explanations"
README_PATH = Path("knowledge") / "readme.md"
README_ID = "readme"
# documents written where they live, by hand or by a turn: (folder, model, id prefix)
WRITTEN_FOLDERS = [
    (EXPLANATIONS_DIR, "ExplanationDoc", ""),
    (Path("knowledge") / "anchors", "AnchorDoc", "anchor-"),
    (Path("knowledge") / "projections", "ProjectionDoc", "projection-"),
    (Path("ledger"), "MoveDoc", ""),
]


class WrittenDocs:
    """Re-tracks, in one world, the written documents whose files changed."""

    def __init__(self, world: World, check: bool) -> None:
        self.world = world
        self.check = check

    def __call__(self) -> list[str]:
        changed = []
        for model, doc_id, path in self._documents():
            if self._retrack(model, doc_id, path):
                changed.append(f"{model} {doc_id}")
        return changed

    def _documents(self) -> list[tuple[str, str, Path]]:
        root = self.world.root
        written = [
            (model, f"{prefix}{path.stem}", path)
            for folder, model, prefix in WRITTEN_FOLDERS
            for path in sorted((root / folder).glob("*.md"))
        ]
        if (root / README_PATH).is_file():
            written.append(("ReadmeDoc", README_ID, root / README_PATH))
        return written

    def _retrack(self, model: str, doc_id: str, path: Path) -> bool:
        """Whether the document drifted from its file; unless checking, track it again."""
        from sldb.runtime.validation import extract_model_data

        store = self.world.store
        existing = store.doc(model, doc_id)
        canonical = extract_model_data(
            store.model_type(model), path.read_text(encoding="utf-8")
        )
        if not drifted(existing, canonical):
            return False
        if not self.check:
            if existing is not None:
                store.untrack(doc_id)
            store.track(path, model, doc_id)
        return True
