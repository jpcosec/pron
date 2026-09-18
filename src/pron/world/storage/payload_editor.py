"""Writing a document's payload, the document named by its `DocId` (spec 04): set, remove,
append to and clean one field, or rewrite the whole payload. Every write re-renders,
round-trips, hashes and reindexes through sldb (spec 12 §4); each returns what the field
held before, for undo.
"""

from __future__ import annotations

import builtins
from typing import Any

from sldb.api import deep_delete, deep_get, deep_set, save_document_payload
from sldb.core.exceptions import SLDBPayloadSaveError

from pron.world.doc_id import DocId
from pron.world.storage.cleaned_list import without_empty_or_repeated
from pron.world.storage.document_reader import DocumentReader
from pron.world.store_error import StoreError


class PayloadEditor(DocumentReader):
    """Field-level and whole-payload writes over the documents of this world's stores."""

    def replace(self, doc_id: DocId, payload: dict) -> None:
        """Whole-payload rewrite: re-render, roundtrip, hash, reindex — same door as
        update_field, for callers that already hold a full payload (spec 12 §4)."""
        d = self.doc(doc_id)
        if d is None:
            raise StoreError(f"no {doc_id.model} named '{doc_id.name}'")
        try:
            save_document_payload(
                self.sp_of(doc_id.store), d.model_name, d.name, payload, self.pythonpath
            )
        except (
            SLDBPayloadSaveError
        ) as exc:  # exits with sldb's message, as `fields` always has
            raise SystemExit(str(exc)) from exc

    def update_field(
        self, doc_id: DocId, field_path: str, value: Any, create: bool = False
    ) -> Any:
        """Set one field (dotted path into subfields and list items). Returns the previous value."""
        p = self.payload(doc_id)
        try:
            before = deep_get(p, field_path)
        except (KeyError, IndexError):
            before = None
        deep_set(p, field_path, value, create=create)
        self.replace(doc_id, p)
        return before

    def remove_field(self, doc_id: DocId, field_path: str) -> Any:
        p = self.payload(doc_id)
        before = deep_get(p, field_path)
        deep_delete(p, field_path)
        self.replace(doc_id, p)
        return before

    def append(self, doc_id: DocId, field_path: str, value: Any) -> int:
        """Append to a list field. Returns the index of the new item."""
        p = self.payload(doc_id)
        lst = deep_get(p, field_path)
        if not isinstance(lst, list):
            raise StoreError(f"{field_path} is not a list field")
        lst.append(value)
        self.replace(doc_id, p)
        return len(lst) - 1

    def clean(self, doc_id: DocId, field_path: str) -> builtins.list:
        """Drop the empty and repeated items of a list field. Returns the list as it was."""
        p = self.payload(doc_id)
        lst = deep_get(p, field_path)
        before = list(lst)
        deep_set(p, field_path, without_empty_or_repeated(lst))
        self.replace(doc_id, p)
        return before
