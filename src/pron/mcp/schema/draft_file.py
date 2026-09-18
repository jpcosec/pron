"""The draft of a registered model (spec 12 §4): the `.py.temp` sibling sldb keeps next to
its module. A preview of `kb_model_extend` edits it, reads it and puts it back as it was, so
nothing stays written (spec 14 §4, nivel 3).
"""

from __future__ import annotations

from sldb.api import locate_model_source

from pron.world.storage.model_editor import ModelEditor


class DraftFile:
    """A model's draft path and what it held before an edit."""

    def __init__(self, store: ModelEditor, name: str) -> None:
        source = locate_model_source(store.sp, name, store.pythonpath)
        self.path = source.draft_path
        self.before = (
            self.path.read_text(encoding="utf-8") if self.path.exists() else None
        )

    def text(self) -> str:
        return self.path.read_text(encoding="utf-8") if self.path.exists() else ""

    def restore(self) -> None:
        """The draft as it was: its old text, or no draft at all."""
        if self.before is not None:
            self.path.write_text(self.before, encoding="utf-8")
        else:
            self.path.unlink(missing_ok=True)
