"""The values a string field actually holds (spec 05 §Calce aproximado, PLAN 11 P1–P3):
read straight from the documents of a projection's stores, distinct, in the order they
are met. Free text never becomes a word except for `system` and `tags`; these values are
what a value suggestion ranks against.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class DocumentValues:
    """Distinct non-empty strings of one field across the lexicon's stores and some models."""

    def __init__(self, lex: "Lexicon") -> None:
        self.lex = lex

    def __call__(
        self, models: Iterable[str], field_name: str, stringlist: bool = False
    ) -> list[str]:
        """Store by store, model by model; a `stringlist` field contributes each item."""
        seen: set[str] = set()
        out: list[str] = []
        for s in self.lex.stores:
            for model in models:
                for v in self._values(model, s, field_name, stringlist):
                    if isinstance(v, str) and v and v not in seen:
                        seen.add(v)
                        out.append(v)
        return out

    def _values(
        self, model: str, store: str, field_name: str, stringlist: bool
    ) -> list[Any]:
        try:
            docs = self.lex.world.store.docs_of(model, store)
        except Exception:  # noqa: BLE001 - a model missing from a store has no docs there
            return []
        out: list[Any] = []
        for d in docs:
            raw = d.payload.get(field_name)
            out += (raw or []) if stringlist else [raw]
        return out
