"""Narrowing what a read found by the predicates its extra modifiers left (spec 02, 07).

Each predicate is one `find` per store of the projection; the hits of a predicate are the
union over the stores, and the hits of several predicates are their intersection. Every
call is put in the trace exactly as it was made, so the answer can be checked by hand.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.ids import scope as _scope
from pron.sexpr.resolving.resolution import address_to_export_id

if TYPE_CHECKING:
    from pron.sexpr.turn.move_context import MoveContext
    from pron.world.lexicon import Lexicon
    from pron.world.world import World


class PredicateFilter:
    """The found set intersected with every predicate, over every store."""

    def __init__(self, world: World, lex: Lexicon):
        self.world, self.lex = world, lex

    def __call__(
        self,
        found: list[str],
        model: str | None,
        predicates: list[str],
        ctx: MoveContext,
    ) -> list[str]:
        assert model is not None
        keep: set[str] | None = None
        for where in predicates:
            hits = self._hits(model, where, ctx)
            keep = hits if keep is None else keep & hits
        return [e for e in found if e in (keep or set())]

    def _hits(self, model: str, where: str, ctx: MoveContext) -> set[str]:
        hits: set[str] = set()
        for sc in (_scope(s, model) for s in self.lex.stores):
            got = {address_to_export_id(a) for a in self.world.store.find(sc, where)}
            q = f"find '{sc}' --where '{where}' → {len(got)}"
            ctx.trace.append(q)
            ctx.record["queries"].append(q)
            hits |= got
        return hits
