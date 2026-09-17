"""What a said value becomes in a field (spec 04, spec 11 §7): the field looked up in the
model's schema over the projection's stores, and the value coerced to its kind — a whole
number, a number, a boolean, one of an enum — before any write or dry run sees it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.world.store_error import StoreError

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.kernel.kernel import Kernel

TRUE_WORDS = ("true", "yes", "on", "1")


class FieldCoercion:
    """The schema of a model as the kernel sees it, and values coerced to its fields."""

    def __init__(self, kernel: "Kernel") -> None:
        self.kernel = kernel

    def schema(self, model: str) -> list[dict[str, Any]]:
        return self.kernel.world.schema(model, self.kernel.stores)

    def coerce(self, model: str, field_name: str, value: Any) -> Any:
        f = self._field(model, field_name)
        kind = f["kind"]
        if kind == "integer":
            return self._integer(field_name, value)
        if kind == "number":
            return float(value)
        if kind == "boolean":
            return str(value).lower() in TRUE_WORDS
        if kind == "enum" and f.get("enum") and value not in f["enum"]:
            raise StoreError(
                f"{field_name} is one of {', '.join(map(str, f['enum']))}, not {value!r}"
            )
        return value

    def _field(self, model: str, field_name: str) -> dict[str, Any]:
        """The schema entry of the field a (dotted) name starts with."""
        f = next(
            (x for x in self.schema(model) if x["name"] == field_name.split(".")[0]),
            None,
        )
        if f is None:
            raise StoreError(
                f"{model} has no field '{field_name}'; it has {', '.join(x['name'] for x in self.schema(model))}"
            )
        return f

    @staticmethod
    def _integer(field_name: str, value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            raise StoreError(f"{field_name} takes a whole number, not {value!r}")

    def coerced(self, model: str, payload: dict[str, Any]) -> dict[str, Any]:
        """The payload's fields the model has, in schema order, each coerced."""
        return {
            f["name"]: self.coerce(model, f["name"], payload[f["name"]])
            for f in self.schema(model)
            if f["name"] in payload
        }

    def required_missing(self, model: str, payload: dict[str, Any]) -> list[str]:
        return [
            f["name"]
            for f in self.schema(model)
            if f["required"] and f["name"] not in payload
        ]
