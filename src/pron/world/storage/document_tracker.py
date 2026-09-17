"""Bringing documents into a store and out of it (spec 04): a new document rendered,
round-tripped and tracked, an existing file tracked again, a document untracked, and a
payload checked against its model's roundtrip before any of that (spec 11 §7).
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from pydantic import ValidationError
from sldb.cli.commands.doc import DocCLI
from sldb.cli.model_utils import resolve_model_ref
from sldb.runtime.validation import (
    render_model_markdown,
    validate_model_data_roundtrip,
    validate_model_input_roundtrip,
)
from sldb.store.ops import track_document

from pron.kernel.ids import LOCAL, is_local, join_id, split_id
from pron.world.storage.document_reader import DocumentReader
from pron.world.store_error import StoreError


def _reason(error: dict) -> str:
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

    def create(
        self,
        model: str,
        name: str,
        payload: dict,
        path: Path,
        store: str | None = LOCAL,
    ) -> str:
        """Render, validate and track one new document in a store. Returns the export id."""
        root = self.root_of(store)
        registration = self.registration(model, store)
        if self.doc(model, name, store) is not None:
            raise StoreError(
                f"a {model} named '{name}' already exists"
                + ("" if is_local(store) else f" in store '{store}'")
            )
        rendered = self._rendered(registration[0], model, name, payload)
        path = self._under(root, path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")
        self._track_registered(registration, path, name, store)
        return join_id(store, model, name)

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

    def track(
        self, path: Path, model: str, name: str, store: str | None = LOCAL
    ) -> None:
        root = self.root_of(store)
        registration = self.registration(model, store)
        self._track_registered(registration, self._under(root, path), name, store)

    def _track_registered(
        self, registration: tuple, path: Path, name: str, store: str | None
    ) -> None:
        model_type, entry, idx = registration
        track_document(
            self.sp_of(store),
            self.root_of(store),
            idx,
            model_type,
            entry,
            path,
            name,
            resolve_model_ref,
            self.pythonpath,
        )

    def untrack(self, name: str, store: str | None = LOCAL) -> None:
        DocCLI().untrack(
            SimpleNamespace(
                doc=name, store=str(self.sp_of(store)), pythonpath=self.pythonpath
            )
        )

    def untrack_of(self, export_id: str) -> None:
        store, _, name = split_id(export_id)
        self.untrack(name, store)
