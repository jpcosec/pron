"""The kernel: the action verbs, each one an sldb write (spec 04), plus refresh and undo
(spec 11 §7). Every write is pre-validated, guarded by the document's hash_c, recorded
with its previous value, and followed by a re-evaluation of the conditions of the edges
around the document. Nothing here knows any model.

What each verb does lives in its own class under pron.kernel.actions (`CreateVerb` and the
registry's `Verb`s), the dry runs of a move in `DryRun`, undoing a move in `MoveUndo`, and
coercing a value to a field in `FieldCoercion`; the kernel holds the state they share —
the expected hashes, the warnings and notes of the turn — and the guards around every write.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.actions.create_verb import CreateVerb
from pron.kernel.actions.dry_run import DryRun
from pron.kernel.actions.move_undo import MoveUndo
from pron.kernel.actions.verb_registry import VERBS
from pron.kernel.actions.write import Write
from pron.kernel.field_coercion import FieldCoercion
from pron.sexpr.resolving.verbs import Verbs
from pron.world.doc_id import DocId
from pron.world.store_error import StoreError

__all__ = ["Kernel", "Write"]


class Kernel:
    def __init__(self, verbs: Verbs, projection: dict[str, Any]):
        self.verbs = verbs
        self.world, self.store = verbs.world, verbs.store
        self.projection = projection
        self.write_store = (
            verbs.write_store
        )  # where create puts a document: the projection's first store
        self.stores = list(verbs.stores)
        self.expected_hash: dict[str, str] = {}
        self.warnings: list[str] = []
        self.notes: list[str] = []  # what the last verbs verified, for the trace
        self.fields = FieldCoercion(self)
        self.dry = DryRun(self)

    def allowed(self, verb: str) -> bool:
        return verb in (self.projection.get("actions") or [])

    # -- guards ------------------------------------------------------------------------

    def expect(self, export_id: str) -> None:
        self.expected_hash[export_id] = self.store.hash_c(DocId.parse_plain(export_id))

    def _guard(self, export_id: str) -> None:
        expected = self.expected_hash.get(export_id)
        current = self.store.hash_c(DocId.parse_plain(export_id))
        if expected is not None and expected != current:
            raise StoreError(f"{export_id} changed since it was read; not writing")

    def _after_write(self, export_id: str, w: Write) -> None:
        """Replace the expected hash by the one sldb left, record it in the write for undo, and
        re-evaluate the conditions around the document."""
        current = self.store.hash_c(DocId.parse_plain(export_id))
        self.expected_hash[export_id] = w.extra["hash_c"] = current
        self.warnings += self.verbs.broken_conditions(export_id)

    def roundtrip(self, model: str, payload: dict[str, Any], store: str | None) -> None:
        """Refuse a payload sldb would not read back as itself."""
        ok, detail = self.store.validate(model, payload, store)
        if not ok:
            raise StoreError(f"{model} payload would not round-trip: {detail}")

    def dependents(self, export_id: str) -> list[dict[str, Any]]:
        """The authored edges that have this document as source or target."""
        return (
            self.verbs._edges_sldb("source_id", export_id, None).edges
            + self.verbs._edges_sldb("target_id", export_id, None).edges
        )

    # -- pre-validation (spec 11 §7) --------------------------------------------------------

    def dry_run(
        self,
        verb: str,
        export_id: str,
        field_name: str | None,
        value: Any,
        overlay: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """What a write would leave, without writing (spec 11 §7); each verb's `Verb.dry`
        (pron.kernel.actions.verb) knows its own coercion and transition."""
        return self.dry(verb, export_id, field_name, value, overlay)

    def dry_create(
        self, model: str, payload: dict[str, Any], overlay: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """The payload a create would leave, coerced and round-tripped, registered in the overlay
        as `Model:$created` so later steps of the move can be checked against it."""
        return CreateVerb().dry(self, model, payload, overlay)

    # -- coercion ---------------------------------------------------------------------------

    def schema(self, model: str) -> list[dict[str, Any]]:
        return self.fields.schema(model)

    def coerce(self, model: str, field_name: str, value: Any) -> Any:
        return self.fields.coerce(model, field_name, value)

    def required_missing(self, model: str, payload: dict[str, Any]) -> list[str]:
        return self.fields.required_missing(model, payload)

    # -- verbs -------------------------------------------------------------------------------

    def create(
        self,
        model: str,
        payload: dict[str, Any],
        related: dict[str, dict[str, Any]] | None = None,
        name: str | None = None,
    ) -> Write:
        return CreateVerb().execute(self, model, payload, related, name)

    def change(self, export_id: str, field_name: str, value: Any) -> Write:
        return VERBS["change"].execute(self, export_id, field_name, value)

    def add(self, export_id: str, field_name: str, value: Any) -> Write:
        return VERBS["add"].execute(self, export_id, field_name, value)

    def remove(self, export_id: str, field_name: str, value: Any = None) -> Write:
        return VERBS["remove"].execute(self, export_id, field_name, value)

    def clean(self, export_id: str, field_name: str) -> Write:
        return VERBS["clean"].execute(self, export_id, field_name, None)

    def forget(self, export_id: str) -> Write:
        return VERBS["forget"].execute(self, export_id, None, None)

    def refresh(self) -> dict[str, Any]:
        return self.world.refresh()

    # -- undo ---------------------------------------------------------------------------------

    def undo(self, move: dict[str, Any]) -> list[Write]:
        """Apply the inverses of a recorded move's writes, newest first (spec 11 §7). Before
        touching anything: a write whose document changed since the move (a different hash_c
        from the one the move left) is skipped and named; an inverse that would orphan a
        later relation rejects the whole undo."""
        return MoveUndo(self)(move)
