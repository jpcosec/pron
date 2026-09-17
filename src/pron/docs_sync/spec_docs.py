"""A SpecDoc per chapter of the specification (spec 08 step 9): each `NN-….md` file of
source/spec, tracked where it lives, with its chapter number for the implements edges.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

SPEC_DIR = Path("source") / "spec"


class SpecDocs:
    """The SpecDoc payloads of one repo's chapters, in file order."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def __call__(self) -> list[dict[str, Any]]:
        return [self._spec(path) for path in sorted((self.root / SPEC_DIR).glob("[0-9][0-9]*.md"))]

    @staticmethod
    def _spec(path: Path) -> dict[str, Any]:
        text = path.read_text(encoding="utf-8").strip()
        first, _, body = text.partition("\n")
        chapter = path.stem.split("-", 1)[0]
        return {
            "id": f"spec-{chapter}",
            "title": first.lstrip("# ").strip(),
            "body": body.strip(),
            "_path": path,
            "_chapter": chapter.lower(),
        }
