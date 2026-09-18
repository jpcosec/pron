"""`kb_model_create` (spec 14 §4, nivel 3): a model generated from its JSON declaration as a
module under `<pythonpath>/pron_generated/<world>/<snake>.py` and registered in the world as
`pron_generated.<world>.<snake>:<Name>`. Without `confirm` it answers the module and its
check and writes nothing; with it, it writes and registers only a module that imports and
roundtrips. No MoveDoc and no undo: schema edits have no form (spec 12 §4).
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path
from typing import Any

from pron.mcp.schema.model_check import ModelCheck
from pron.mcp.schema.model_source import ModelSource
from pron.mcp.writes.arg_error import ArgError
from pron.world.world import World

PACKAGE = "pron_generated"


class ModelCreate:
    """One world's new models, generated where its pythonpath imports them from."""

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
        except ArgError as exc:
            return {"text": str(exc), "outcome": "error", "written": False}
        text, check = source.module(head), ModelCheck(source.module(head), name)()
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
        return {**plan, **self._register(source, text)}

    def _source(
        self, name: str, fields: list, template: str | None, base: str | None
    ) -> tuple[ModelSource, str | None]:
        if name in self.world.store.model_names():
            raise ArgError(f"model {name} is already registered")
        if base is None:
            return ModelSource.of(name, fields, template, None), None
        try:
            cls = self.world.store.model_type(base)
        except Exception:  # noqa: BLE001 - an unknown base is the agent's error
            raise ArgError(f"base {base!r} is not a registered model") from None
        head = str(getattr(cls, "__template__", "")).strip() or None
        return ModelSource.of(
            name, fields, template, (cls.__module__, cls.__name__)
        ), head

    def _path(self, source: ModelSource) -> Path:
        return (
            Path(self.world.store.pythonpath)
            / PACKAGE
            / self.package
            / f"{source.snake}.py"
        )

    def _ref(self, source: ModelSource) -> str:
        return f"{PACKAGE}.{self.package}.{source.snake}:{source.name}"

    def _register(self, source: ModelSource, text: str) -> dict[str, Any]:
        path = self._path(source)
        for pkg in (path.parent.parent, path.parent):
            pkg.mkdir(parents=True, exist_ok=True)
            (pkg / "__init__.py").touch()
        path.write_text(text, encoding="utf-8")
        _forget_generated(str(self.world.store.pythonpath))
        if not self.world.store.register_model(self._ref(source)):
            return {
                "text": f"sldb did not register {source.name}.",
                "outcome": "error",
                "written": True,
            }
        self.world.refresh()
        return {
            "text": f"Created model {source.name}.",
            "outcome": "unico",
            "written": True,
        }


def _forget_generated(pythonpath: str) -> None:
    """A module written after the import system looked is found only after this; and the
    generated package is the one under this world's pythonpath."""
    if pythonpath in sys.path:
        sys.path.remove(pythonpath)
    sys.path.insert(0, pythonpath)
    importlib.invalidate_caches()
    for key in [k for k in sys.modules if k == PACKAGE or k.startswith(PACKAGE + ".")]:
        del sys.modules[key]
