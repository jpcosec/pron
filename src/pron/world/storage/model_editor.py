"""Editing a registered model's own contract (spec 12 §4, spec 10 §3), as opposed to a
document's payload: the same door, the same legitimacy. A draft lives in the `.py.temp`
sibling sldb keeps next to the compiled model module until `model_promote` installs it,
reindexes, and bumps the version. No `MoveDoc` records any of this.
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

from sldb.cli.commands.model import ModelCLI
from sldb.cli.commands.models_fields import ModelsFieldsCLI
from sldb.cli.commands.models_template import ModelsTemplateCLI
from sldb.cli.commands.models_utils import (
    draft_path as _draft_path,
    registered_model_source,
)
from sldb.cli.commands.models_validate import ModelsValidateCLI
from sldb.core.exceptions import SLDBError

from pron.kernel.ids import LOCAL
from pron.world.storage.model_registry import ModelRegistry
from pron.world.store_error import StoreError


class ModelEditor(ModelRegistry):
    """Draft edits of a model (template, fields), their validation, and their promotion."""

    def _model_args(
        self, name: str, store: str | None, **extra: Any
    ) -> SimpleNamespace:
        return SimpleNamespace(
            model=name,
            store=str(self.sp_of(store)),
            pythonpath=self.pythonpath,
            **extra,
        )

    @staticmethod
    def _edit(edit: Callable[[SimpleNamespace], Any], args: SimpleNamespace) -> None:
        """Run one sldb draft edit; its errors are the store's."""
        try:
            edit(args)
        except SLDBError as exc:
            raise StoreError(str(exc)) from exc

    def _draft(self, edit: Callable[[SimpleNamespace], Any], args: SimpleNamespace) -> Path:
        """Run one sldb draft edit and return the `.py.temp` path it left."""
        self._edit(edit, args)
        return self._draft_of(args)

    @staticmethod
    def _draft_of(args: SimpleNamespace) -> Path:
        path, _, _ = registered_model_source(args)
        return _draft_path(path)

    def model_template_edit(
        self, name: str, content: str, store: str | None = LOCAL
    ) -> Path:
        """Write `content` as the draft template for `name`; returns the `.py.temp` path."""
        tmp = Path(tempfile.mkdtemp(prefix="pron-model-template-"))
        try:
            input_path = tmp / "template.md"
            input_path.write_text(content, encoding="utf-8")
            args = self._model_args(name, store, input=str(input_path))
            self._edit(ModelsTemplateCLI().edit_template, args)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return self._draft_of(args)

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
        args = self._model_args(
            name,
            store,
            field=field_name,
            field_type=field_type,
            description=description,
            default=default,
        )
        return self._draft(ModelsFieldsCLI().add_field, args)

    def model_fields_remove(
        self, name: str, field_name: str, store: str | None = LOCAL
    ) -> Path:
        args = self._model_args(name, store, field=field_name)
        return self._draft(ModelsFieldsCLI().remove_field, args)

    def model_validate_draft(
        self, name: str, store: str | None = LOCAL
    ) -> dict[str, Any]:
        """Validate the draft (or the active model if there is none), without promoting."""
        return self._run_validate(name, store, promote=False)

    def model_promote(self, name: str, store: str | None = LOCAL) -> dict[str, Any]:
        """Install a validated draft over the active model, reindex, bump version."""
        result = self._run_validate(name, store, promote=True)
        result["version"] = self.models_index(name, store).version
        if result.get("promoted"):
            self._invalidate_model_module(name, store)
        return result

    def _invalidate_model_module(self, name: str, store: str | None) -> None:
        """`resolve_model_ref` caches by module name in `sys.modules` (`importlib.import_module`);
        promote just rewrote that module's file on disk, so drop the cached module or every
        `model_type`/`schema` call in this same process keeps seeing the pre-promote class."""
        entry = self.model_entry(name, store)
        if entry is None:
            return
        module_name = entry.model_ref.split(":", 1)[0]
        sys.modules.pop(module_name, None)

    def _run_validate(
        self, name: str, store: str | None, promote: bool
    ) -> dict[str, Any]:
        args = self._model_args(name, store, promote=promote, format="json")
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                ModelsValidateCLI().validate(args, ModelCLI())
        except SLDBError as exc:
            raise StoreError(str(exc)) from exc
        return json.loads(buf.getvalue())
