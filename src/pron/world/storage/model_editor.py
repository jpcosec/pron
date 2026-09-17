"""Editing a registered model's own contract (spec 12 §4, spec 10 §3), as opposed to a
document's payload: the same door, the same legitimacy. A draft lives in the `.py.temp`
sibling sldb keeps next to the compiled model module until `model_promote` installs it,
reindexes, and bumps the version. No `MoveDoc` records any of this.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from sldb.api import (
    add_model_field,
    edit_model_template,
    promote_model_draft,
    remove_model_field,
    validate_model_draft,
)
from sldb.core.exceptions import SLDBError

from pron.kernel.ids import LOCAL
from pron.world.storage.model_registry import ModelRegistry
from pron.world.store_error import StoreError


class ModelEditor(ModelRegistry):
    """Draft edits of a model (template, fields), their validation, and their promotion."""

    def _sldb(
        self, operation: Callable[..., Any], name: str, store: str | None, *args: Any
    ) -> Any:
        """Run one sldb model operation on `name` in a store; its errors are the store's."""
        try:
            return operation(self.sp_of(store), name, *args, pythonpath=self.pythonpath)
        except SLDBError as exc:
            raise StoreError(str(exc)) from exc

    def model_template_edit(
        self, name: str, content: str, store: str | None = LOCAL
    ) -> Path:
        """Write `content` as the draft template for `name`; returns the `.py.temp` path."""
        return self._sldb(edit_model_template, name, store, content).draft_path

    def model_fields_add(
        self,
        name: str,
        field_name: str,
        field_type: str = "str",
        description: str = "",
        default: Any = None,
        store: str | None = LOCAL,
    ) -> Path:
        """Add a field to the draft, `.py.temp` sibling of the compiled model module."""
        draft = self._sldb(
            add_model_field, name, store, field_name, field_type, description, default
        )
        return draft.draft_path

    def model_fields_remove(
        self, name: str, field_name: str, store: str | None = LOCAL
    ) -> Path:
        return self._sldb(remove_model_field, name, store, field_name).draft_path

    def model_validate_draft(
        self, name: str, store: str | None = LOCAL
    ) -> dict[str, Any]:
        """Validate the draft (or the active model if there is none), without promoting."""
        report = self._sldb(validate_model_draft, name, store)
        return report.model_dump(mode="json", exclude={"version"})

    def model_promote(self, name: str, store: str | None = LOCAL) -> dict[str, Any]:
        """Install a validated draft over the active model, reindex, bump version. sldb drops
        the promoted model's modules from `sys.modules`, so every `model_type`/`schema` call
        in this same process sees the new class."""
        return self._sldb(promote_model_draft, name, store).model_dump(mode="json")
