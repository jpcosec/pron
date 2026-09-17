"""Writing a document's payload by address (spec 04): set, remove, append to and clean one
field, or rewrite the whole payload. Every write re-renders, round-trips, hashes and
reindexes through sldb (spec 12 §4); each returns what the field held before, for undo.
"""

from __future__ import annotations

import builtins
from typing import Any

from sldb.cli.commands.fields_save import save_payload
from sldb.cli.dict_utils import deep_delete, deep_get, deep_set

from pron.kernel.ids import LOCAL, split_id
from pron.world.storage.cleaned_list import without_empty_or_repeated
from pron.world.storage.document_reader import DocumentReader
from pron.world.store_error import StoreError


class PayloadEditor(DocumentReader):
    """Field-level and whole-payload writes over the documents of this world's stores."""

    def _save(
        self, model: str, name: str, payload: dict, store: str | None = LOCAL
    ) -> None:
        d = self.doc(model, name, store)
        if d is None:
            raise StoreError(f"no {model} named '{name}'")
        save_payload(d, payload, str(self.sp_of(store)), self.pythonpath)

    def replace(
        self, model: str, name: str, payload: dict, store: str | None = LOCAL
    ) -> None:
        """Whole-payload rewrite: re-render, roundtrip, hash, reindex — same door as
        update_field, for callers that already hold a full payload (spec 12 §4)."""
        self._save(model, name, payload, store)

    def replace_of(self, export_id: str, payload: dict) -> None:
        store, model, name = split_id(export_id)
        self.replace(model, name, payload, store)

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
        p = self.payload(model, name, store)
        try:
            before = deep_get(p, field_path)
        except (KeyError, IndexError):
            before = None
        deep_set(p, field_path, value, create=create)
        self._save(model, name, p, store)
        return before

    def update_field_of(
        self, export_id: str, field_path: str, value: Any, create: bool = False
    ) -> Any:
        store, model, name = split_id(export_id)
        return self.update_field(model, name, field_path, value, create, store)

    def remove_field(
        self, model: str, name: str, field_path: str, store: str | None = LOCAL
    ) -> Any:
        p = self.payload(model, name, store)
        before = deep_get(p, field_path)
        deep_delete(p, field_path)
        self._save(model, name, p, store)
        return before

    def remove_field_of(self, export_id: str, field_path: str) -> Any:
        store, model, name = split_id(export_id)
        return self.remove_field(model, name, field_path, store)

    def append(
        self,
        model: str,
        name: str,
        field_path: str,
        value: Any,
        store: str | None = LOCAL,
    ) -> int:
        """Append to a list field. Returns the index of the new item."""
        p = self.payload(model, name, store)
        lst = deep_get(p, field_path)
        if not isinstance(lst, list):
            raise StoreError(f"{field_path} is not a list field")
        lst.append(value)
        self._save(model, name, p, store)
        return len(lst) - 1

    def append_of(self, export_id: str, field_path: str, value: Any) -> int:
        store, model, name = split_id(export_id)
        return self.append(model, name, field_path, value, store)

    def clean(
        self, model: str, name: str, field_path: str, store: str | None = LOCAL
    ) -> builtins.list:
        """Drop the empty and repeated items of a list field. Returns the list as it was."""
        p = self.payload(model, name, store)
        lst = deep_get(p, field_path)
        before = list(lst)
        deep_set(p, field_path, without_empty_or_repeated(lst))
        self._save(model, name, p, store)
        return before

    def clean_of(self, export_id: str, field_path: str) -> builtins.list:
        store, model, name = split_id(export_id)
        return self.clean(model, name, field_path, store)
