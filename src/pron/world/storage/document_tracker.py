"""Bringing documents into a store and out of it (spec 04), named the ways callers still
name a document — `(model, name, store)` and `untrack_of(export_id)` — and a payload
checked against its model's roundtrip before any of that (spec 11 §7).

The tracking itself is `TrackerById`'s: these forms build a `DocId` and delegate.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError
from pydantic_core import ErrorDetails
from sldb.runtime.validation import validate_model_data_roundtrip

from pron.world.doc_id import LOCAL, DocId
from pron.world.storage.tracker_by_id import TrackerById


def _reason(error: ErrorDetails) -> str:
    """One pydantic complaint as `field: message`."""
    return f"{'.'.join(map(str, error['loc']))}: {error['msg']}"


class DocumentTracker(TrackerById):
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
        return str(self.create_at(DocId.of(model, name, store), payload, path))

    def track(
        self, path: Path, model: str, name: str, store: str | None = LOCAL
    ) -> None:
        self.track_at(DocId.of(model, name, store), path)

    def untrack(self, name: str, store: str | None = LOCAL) -> None:
        self._untrack_named(name, store)

    def untrack_of(self, export_id: str) -> None:
        self.untrack_at(DocId.parse_plain(export_id))
