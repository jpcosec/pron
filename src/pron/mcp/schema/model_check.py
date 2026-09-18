"""Whether a generated model module works before it is registered (spec 14 §4, nivel 3): it
imports, its class is a `StructuredNLDoc`, and an example payload survives render and
extraction (sldb's own roundtrip).
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import typing
from pathlib import Path
from typing import Any

from pydantic import BaseModel

EXAMPLES: dict[Any, Any] = {str: "example", int: 1, float: 1.5, bool: True}


class ModelCheck:
    """A module's source and its class name, checked in a scratch directory."""

    def __init__(self, source: str, name: str) -> None:
        self.source, self.name = source, name

    def __call__(self) -> dict[str, Any]:
        """{ok, payload, errors}; never raises for a module that fails."""
        with tempfile.TemporaryDirectory() as tmp:
            try:
                cls = self._load(Path(tmp) / "draft.py")
            except Exception as exc:  # noqa: BLE001 - whatever the module raises is the report
                return {"ok": False, "payload": {}, "errors": [f"import: {exc}"]}
        return self.roundtrip(cls)

    def _load(self, path: Path) -> type[BaseModel]:
        path.write_text(self.source, encoding="utf-8")
        key = f"_pron_model_check_{self.name}"
        spec = importlib.util.spec_from_file_location(key, path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(key, None)
        return getattr(module, self.name)

    @staticmethod
    def roundtrip(cls: type[BaseModel]) -> dict[str, Any]:
        """An example payload rendered to markdown and read back, as sldb validates it."""
        from sldb.runtime.validation import validate_model_data_roundtrip

        payload = example_payload(cls)
        try:
            ok, report = validate_model_data_roundtrip(cls, payload)
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "payload": payload, "errors": [f"roundtrip: {exc}"]}
        errors = [] if ok else [f"roundtrip: {report}"]
        return {"ok": ok, "payload": payload, "errors": errors}


def example_payload(cls: type[BaseModel]) -> dict[str, Any]:
    """One value per field, from its annotation."""
    return {name: example(info.annotation) for name, info in cls.model_fields.items()}


def example(annotation: Any) -> Any:
    origin = typing.get_origin(annotation)
    if origin is typing.Literal:
        return typing.get_args(annotation)[0]
    if origin is list:
        return ["example"]
    return EXAMPLES.get(annotation, "example")
