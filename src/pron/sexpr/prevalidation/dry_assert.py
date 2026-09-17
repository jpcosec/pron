"""Simulating a new edge (spec 11 §7, spec 03): would this relation hold?

The projection has to allow asserting it at all, the classes of both sides have to be the
ones the relation type declares, the cardinality has to leave room for one more, and the
relation type's condition has to hold over the payloads this move would leave. A side that
is still `$created` has no document yet, so cardinality is not asked of it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.ids import model_of
from pron.world.store_error import StoreError

if TYPE_CHECKING:
    from pron.kernel.kernel import Kernel
    from pron.sexpr.resolving.verbs import Verbs
    from pron.world.lexicon import Lexicon


class DryAssert:
    """Every source × target pair of one assert, checked without writing."""

    def __init__(self, verbs: Verbs, lex: Lexicon, kernel: Kernel):
        self.verbs, self.lex, self.kernel = verbs, lex, kernel

    def __call__(
        self,
        rel: str,
        sources: list[str],
        targets: list[str],
        overlay: dict[str, dict[str, Any]],
    ) -> None:
        rt = self.verbs.relation_type(rel)
        if "assert" not in self.lex.relation_types.get(rel, {}).get("mode", "read"):
            raise StoreError(
                f"in this session I can tell you about {rel}, not assert it"
            )
        for s in sources:
            for t in targets:
                self._pair(rel, rt, s, t, overlay)

    def _pair(
        self,
        rel: str,
        rt: dict[str, Any],
        s: str,
        t: str,
        overlay: dict[str, dict[str, Any]],
    ) -> None:
        ok, why = self.verbs.applies(rel, model_of(s), model_of(t))
        if not ok:
            raise StoreError(why)
        if not s.endswith(":$created") and not t.endswith(":$created"):
            self._cardinality(rel, s, t)
        if rt.get("condition"):
            self._condition(rt["condition"], s, t, overlay)

    def _cardinality(self, rel: str, s: str, t: str) -> None:
        ok, why = self.verbs.cardinality_ok(rel, s, t)
        if not ok:
            raise StoreError(why)

    def _condition(
        self, condition: str, s: str, t: str, overlay: dict[str, dict[str, Any]]
    ) -> None:
        holds, query = self.verbs.condition_holds(
            condition, s, over=t, overlay=overlay
        )
        self.kernel.notes.append(query)
        if not holds:
            raise StoreError(
                f"condition '{condition}' does not hold for {s} → {t} ({query})"
            )
