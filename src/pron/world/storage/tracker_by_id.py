"""Bringing one document into a store and out of it, by its `DocId` (spec 04): a new
document rendered, round-tripped and tracked, an existing file tracked again, a document
untracked (spec 11 §7).

This is the one form; `DocumentTracker` names the same document the older ways and
delegates here.
"""

from __future__ import annotations

import json
from pathlib import Path

from sldb.api import track_document_file, untrack_document
from sldb.runtime.validation import (
    render_model_markdown,
    validate_model_input_roundtrip,
)

from pron.world.doc_id import DocId
from pron.world.storage.document_reader import DocumentReader
from pron.world.storage.documents_by_id import in_store
from pron.world.store_error import StoreError


class TrackerById(DocumentReader):
    """Creates, tracks and untracks one document of this world's stores, by its `DocId`."""

    def create_at(self, doc_id: DocId, payload: dict, path: Path) -> DocId:
        """Render, validate and track one new document in its store. Returns the same id."""
        root = self.root_of(doc_id.store)
        model_type = self.registration(doc_id.model, doc_id.store).model_type
        if self.doc_at(doc_id) is not None:
            raise StoreError(
                f"a {doc_id.model} named '{doc_id.name}' already exists"
                + in_store(doc_id)
            )
        rendered = self._rendered(model_type, doc_id.model, doc_id.name, payload)
        path = self._under(root, path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")
        self._track_registered(doc_id, path)
        return doc_id

    @staticmethod
    def _rendered(model_type, model: str, name: str, payload: dict) -> str:
        """The document's markdown, refused unless it reads back as the same payload."""
        rendered = render_model_markdown(model_type, payload)
        ok, details = validate_model_input_roundtrip(model_type, rendered)
        if not ok:
            raise StoreError(
                f"{model} '{name}' would not round-trip: {json.dumps(details.get('extracted_payload'), default=str)[:200]}"
            )
        return rendered

    @staticmethod
    def _under(root: Path, path: Path) -> Path:
        """A relative document path is relative to the store's root, never to the process cwd:
        sldb records paths relative to the root, so a cwd-relative file would be tracked as missing."""
        path = Path(path)
        return path if path.is_absolute() else root / path

    def track_at(self, doc_id: DocId, path: Path) -> None:
        # imports the model; a linked store's, from its root
        self.registration(doc_id.model, doc_id.store)
        self._track_registered(doc_id, self._under(self.root_of(doc_id.store), path))

    def _track_registered(self, doc_id: DocId, path: Path) -> None:
        """Track a file of a model already imported (`registration`). Never re-checked here: a
        new document was round-tripped when rendered, and `track_at` takes the file as it is."""
        track_document_file(
            self.sp_of(doc_id.store),
            doc_id.model,
            path,
            doc_id.name,
            self.pythonpath,
            force=True,
        )

    def untrack_at(self, doc_id: DocId) -> None:
        self._untrack_named(doc_id.name, doc_id.store)

    def _untrack_named(self, name: str, store: str | None) -> None:
        """sldb untracks by name alone: no model is consulted."""
        untrack_document(self.sp_of(store), name, self.pythonpath)
