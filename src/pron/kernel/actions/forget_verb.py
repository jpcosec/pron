"""The `forget` verb (spec 11 §7): untrack a document, and track its file again to undo.
Its dry-run is a preview only: a forgotten document has no payload for later steps of the
move to see.
"""

from __future__ import annotations

from pathlib import Path

from pron.kernel.ids import split_id
from pron.kernel.actions.write import Write
from pron.world.store_error import StoreError


class ForgetVerb:
    name = "forget"

    def dry(self, kernel, export_id, field_name, value, overlay):
        # forget's dry-run is a preview only: it never round-trips or joins the overlay,
        # since a forgotten document has no payload for later steps of the move to see.
        return kernel.dry.load(export_id, overlay)

    def execute(self, kernel, export_id, field_name, value):
        store, model, doc = split_id(export_id)
        path = kernel.store.doc_path(model, doc, store)
        payload = kernel.store.payload_of(export_id)
        dependents = kernel.dependents(export_id)
        if dependents:
            raise StoreError(
                f"{export_id} is an endpoint of {len(dependents)} relation(s); negate them first"
            )
        kernel._guard(export_id)
        kernel.store.untrack_of(export_id)
        return Write(
            "forget",
            export_id,
            before=payload,
            done=True,
            extra={
                "path": str(path),
                "hash_c": kernel.expected_hash.get(export_id, ""),
            },
        )

    def undo(self, kernel, write):
        path = Path(write.get("path", ""))
        store, model, doc = split_id(write["address"])
        if path.exists():
            kernel.store.track(path, model, doc, store)
            return Write(
                "undo",
                write["address"],
                None,
                None,
                write.get("before"),
                done=True,
                note="tracked again",
            )
        return Write(
            "undo", write["address"], None, None, None, done=False, note="file is gone"
        )
