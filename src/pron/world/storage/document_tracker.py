"""Bringing documents into a store and out of it, each named by its `DocId` (spec 04): a
new document rendered, round-tripped and tracked, an existing file tracked again, a document
untracked, and a payload checked against its model's roundtrip before any of that (spec 11 §7).
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError
from pydantic_core import ErrorDetails
from sldb.api import track_document_file, untrack_document
from sldb.runtime.validation import (
    render_model_markdown,
    validate_model_data_roundtrip,
    validate_model_input_roundtrip,
)

from pron.world.doc_id import LOCAL, DocId
from pron.world.storage.document_reader import DocumentReader, in_store
from pron.world.store_error import StoreError


def _reason(error: ErrorDetails) -> str:
    """One pydantic complaint as `field: message`."""
    return f"{'.'.join(map(str, error['loc']))}: {error['msg']}"


class DocumentTracker(DocumentReader):
    """Creates, tracks and untracks the documents of this world's stores."""

    def validate(
        self, model: str, payload: dict, store: str | None = LOCAL
    ) -> tuple[bool, str]:
        """Whether sldb reads the payload back as itself; a payload the model rejects
        outright (a required field missing) is not valid either, with pydantic's reasons."""
        try:
            ok, details = validate_model_data_roundtrip(
                self.model_type(model, store), payload
            )
        except ValidationError as e:
            return False, "; ".join(_reason(err) for err in e.errors())[:200]
        return ok, "" if ok else json.dumps(
            details.get("extracted_payload"), default=str
        )[:200]

    def create(self, doc_id: DocId, payload: dict, path: Path) -> DocId:
        """Render, validate and track one new document in its store. Returns the same id."""
        root = self.root_of(doc_id.store)
        model_type = self.registration(doc_id.model, doc_id.store).model_type
        if self.doc(doc_id) is not None:
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

    def track(self, doc_id: DocId, path: Path) -> None:
        # imports the model; a linked store's, from its root
        self.registration(doc_id.model, doc_id.store)
        self._track_registered(doc_id, self._under(self.root_of(doc_id.store), path))

    def _track_registered(self, doc_id: DocId, path: Path) -> None:
        """Track a file of a model already imported (`registration`). Never re-checked here: a
        new document was round-tripped when rendered, and `track` takes the file as it is."""
        track_document_file(
            self.sp_of(doc_id.store),
            doc_id.model,
            path,
            doc_id.name,
            self.pythonpath,
            force=True,
        )

    def untrack(self, doc_id: DocId) -> None:
        """sldb untracks by name alone: the model of the id is not consulted."""
        untrack_document(self.sp_of(doc_id.store), doc_id.name, self.pythonpath)
