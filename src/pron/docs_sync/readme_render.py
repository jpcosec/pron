"""README.md at the repo root (spec 08 step 9): the ReadmeDoc rendered, never edited by hand —
its parts composed by address. With check, the drift is reported and nothing is written.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from pron.docs_sync.written_docs import README_ID
from pron.world.world import World


class ReadmeRender:
    """Renders one world's ReadmeDoc over its README.md when they differ."""

    def __init__(self, world: World, check: bool) -> None:
        self.world = world
        self.check = check

    def __call__(self) -> list[str]:
        doc = self.world.store.doc("ReadmeDoc", README_ID)
        if doc is None:
            return []
        rendered = self._rendered(dict(doc.payload))
        readme = self.world.root / "README.md"
        current = readme.read_text(encoding="utf-8") if readme.exists() else ""
        if current == rendered:
            return []
        if not self.check:
            readme.write_text(rendered, encoding="utf-8")
        return ["README.md out of date"]

    def _rendered(self, payload: dict) -> str:
        from sldb.runtime.validation import render_model_markdown

        cwd = Path.cwd()
        try:
            os.chdir(self.world.root)  # composition child paths resolve from the process cwd
            rendered = render_model_markdown(self.world.store.model_type("ReadmeDoc"), payload)
        finally:
            os.chdir(cwd)
        rendered = re.sub(r"\n{3,}", "\n\n", rendered)  # the dropped parts list leaves a hole
        return rendered if rendered.endswith("\n") else rendered + "\n"
