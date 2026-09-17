"""Writing a document's payload by address (spec 04), named the ways callers still name a
document: `(model, name, store)` and the `*_of(export_id)` forms. Every write re-renders,
round-trips, hashes and reindexes through sldb (spec 12 §4), and returns what the field
held before, for undo.

The writing itself is `PayloadWriterById`'s: these forms build a `DocId` and delegate.
"""

from __future__ import annotations

import builtins
from typing import Any

from pron.world.doc_id import LOCAL, DocId
from pron.world.storage.payload_writer_by_id import PayloadWriterById


class PayloadEditor(PayloadWriterById):
    """Field-level and whole-payload writes over the documents of this world's stores."""

    def replace(
        self, model: str, name: str, payload: dict, store: str | None = LOCAL
    ) -> None:
        self.replace_at(DocId.of(model, name, store), payload)

    def replace_of(self, export_id: str, payload: dict) -> None:
        self.replace_at(DocId.parse_plain(export_id), payload)

    def update_field(
        self,
        model: str,
        name: str,
        field_path: str,
        value: Any,
        create: bool = False,
        store: str | None = LOCAL,
    ) -> Any:
        """Set one field (dotted path into subfields and list items). Returns the previous value."""
        return self.update_field_at(
            DocId.of(model, name, store), field_path, value, create
        )

    def update_field_of(
        self, export_id: str, field_path: str, value: Any, create: bool = False
    ) -> Any:
        return self.update_field_at(
            DocId.parse_plain(export_id), field_path, value, create
        )

    def remove_field(
        self, model: str, name: str, field_path: str, store: str | None = LOCAL
    ) -> Any:
        return self.remove_field_at(DocId.of(model, name, store), field_path)

    def remove_field_of(self, export_id: str, field_path: str) -> Any:
        return self.remove_field_at(DocId.parse_plain(export_id), field_path)

    def append(
        self,
        model: str,
        name: str,
        field_path: str,
        value: Any,
        store: str | None = LOCAL,
    ) -> int:
        """Append to a list field. Returns the index of the new item."""
        return self.append_at(DocId.of(model, name, store), field_path, value)

    def append_of(self, export_id: str, field_path: str, value: Any) -> int:
        return self.append_at(DocId.parse_plain(export_id), field_path, value)

    def clean(
        self, model: str, name: str, field_path: str, store: str | None = LOCAL
    ) -> builtins.list:
        """Drop the empty and repeated items of a list field. Returns the list as it was."""
        return self.clean_at(DocId.of(model, name, store), field_path)

    def clean_of(self, export_id: str, field_path: str) -> builtins.list:
        return self.clean_at(DocId.parse_plain(export_id), field_path)
