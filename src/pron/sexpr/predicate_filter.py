"""Narrowing what a read found by the predicates its extra modifiers left (spec 02, 07).

Each predicate is one `find` per store of the projection; the hits of a predicate are the
union over the stores, and the hits of several predicates are their intersection. Every
call is put in the trace exactly as it was made, so the answer can be checked by hand.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.ids import scope as _scope
from pron.sexpr.collaborator import Collaborator
from pron.sexpr.resolution import address_to_export_id


class PredicateFilter(Collaborator):
    """The found set intersected with every predicate, over every store."""

    def __call__(
        self,
        found: list[str],
        model: str | None,
        predicates: list[str],
        trace: list[str],
        record: dict[str, Any],
    ) -> list[str]:
        assert model is not None
        keep: set[str] | None = None
        for where in predicates:
            hits = self._hits(model, where, trace, record)
            keep = hits if keep is None else keep & hits
        return [e for e in found if e in (keep or set())]

    def _hits(
        self, model: str, where: str, trace: list[str], record: dict[str, Any]
    ) -> set[str]:
        hits: set[str] = set()
        for sc in (_scope(s, model) for s in self.s.lex.stores):
            got = {
                address_to_export_id(a) for a in self.s.world.store.find(sc, where)
            }
            q = f"find '{sc}' --where '{where}' → {len(got)}"
            trace.append(q)
            record["queries"].append(q)
            hits |= got
        return hits
