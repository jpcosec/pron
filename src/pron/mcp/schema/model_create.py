"""`kb_model_create` (spec 14 §4, nivel 3): a model generated from its JSON declaration.

The substrate owns generation and registration now (ADR 2026-09-20, sldb-absorbs-kgdb):
pron builds the preview through sldb's `ModelSource`/`ModelCheck` and, with `confirm`,
writes through `sldb.api.create_model`. No MoveDoc and no undo (spec 12 §4).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from sldb.api import create_model as _sldb_create_model
from sldb.api.model_create.model_check import ModelCheck
from sldb.api.model_create.model_source import ModelSource
from sldb.core.exceptions import SLDBModelError

from pron.world.world import World

PACKAGE = "pron_generated"


class ModelCreate:
    """One world's new models, generated and registered by sldb's substrate."""

    def __init__(self, world: World, world_name: str) -> None:
        self.world = world
        self.package = re.sub(r"\W", "_", world_name) or "world"
        if not self.package.isidentifier():
            self.package = f"w_{self.package}"

    def __call__(
        self,
        name: str,
        fields: list,
        template: str | None = None,
        base: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        try:
            source, head = self._source(name, fields, template, base)
            text = source.module(head)
            check = ModelCheck(text, name)()
        except SLDBModelError as exc:
            return {"text": str(exc), "outcome": "error", "written": False}
        plan = {
            "model_ref": self._ref(source),
            "path": str(self._path(source)),
            "module": text,
            "check": check,
        }
        if not check["ok"]:
            return {
                "text": f"The module of {name} does not work; nothing was written.",
                "outcome": "error",
                "written": False,
                **plan,
            }
        if not confirm:
            return {
                "text": f"Would create model {name}. Send confirm: true to write it.",
                "outcome": "preview",
                "written": False,
                **plan,
            }
        return self._register(source, name, fields, template, base, plan)

    def _source(
        self, name: str, fields: list, template: str | None, base: str | None
    ) -> tuple[ModelSource, str | None]:
        if name in self.world.store.model_names():
            raise SLDBModelError(f"model {name} is already registered")
        if base is None:
            return ModelSource.of(name, fields, template, None), None
        try:
            cls = self.world.store.model_type(base)
        except Exception:  # noqa: BLE001 - an unknown base is the agent's error
            raise SLDBModelError(f"base {base!r} is not a registered model") from None
        head = str(getattr(cls, "__template__", "")).strip() or None
        return ModelSource.of(
            name, fields, template, (cls.__module__, cls.__name__)
        ), head

    def _register(
        self,
        source: ModelSource,
        name: str,
        fields: list,
        template: str | None,
        base: str | None,
        plan: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            _sldb_create_model(
                self.world.store.sp,
                name,
                fields,
                template=template,
                base=base,
                target_package=f"{PACKAGE}.{self.package}",
                pythonpath=self.world.store.pythonpath,
            )
        except SLDBModelError as exc:
            return {
                "text": f"sldb did not create {name}: {exc}",
                "outcome": "error",
                "written": False,
            }
        self.world.refresh()
        return {
            "text": f"Created model {name}.",
            "outcome": "unico",
            "written": True,
            **plan,
        }

    def _path(self, source: ModelSource) -> Path:
        return (
            Path(self.world.store.pythonpath)
            / PACKAGE
            / self.package
            / f"{source.snake}.py"
        )

    def _ref(self, source: ModelSource) -> str:
        return f"{PACKAGE}.{self.package}.{source.snake}:{source.name}"
