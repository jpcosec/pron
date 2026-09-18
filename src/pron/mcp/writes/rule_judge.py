"""Whether the authored edges of a relation type hold under one version of it (spec 03,
14 §4): their source and target of the types it takes, its cardinality, and its condition —
the edge's own condition when it has one — evaluated with sldb as the checks of an assert
evaluate it (`ConditionCheck.holds`).
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Any

from pron.kernel.ids import model_of
from pron.sexpr.resolving.relation_checks import ONE_SOURCE, ONE_TARGET

if TYPE_CHECKING:
    from pron.session import Session

Edge = dict[str, Any]


class RuleJudge:
    """What would be wrong with each edge under a relation type's payload."""

    def __init__(self, session: Session):
        self.world, self.verbs = session.world, session.verbs

    def __call__(self, rule: dict[str, Any], edges: list[Edge]) -> dict[str, list[str]]:
        """RelationDoc id → why it would break; an edge that holds has no entry."""
        crowded = _crowded(rule.get("cardinality") or "many_to_many", edges)
        out: dict[str, list[str]] = {}
        for e in edges:
            why = self._types(rule, e) + self._condition(rule, e)
            why += [
                c for c in (crowded.get(e["source"]), crowded.get(e["target"])) if c
            ]
            if why:
                out[e["doc"]] = why
        return out

    def _types(self, rule: dict[str, Any], e: Edge) -> list[str]:
        return [
            f"{role} {e[role]} is not one of {', '.join(types)}"
            for role, types in (
                ("source", rule.get("source_types") or []),
                ("target", rule.get("target_types") or []),
            )
            if types and not set(self.world.family_of(model_of(e[role]))) & set(types)
        ]

    def _condition(self, rule: dict[str, Any], e: Edge) -> list[str]:
        cond = e["condition"] or rule.get("condition") or ""
        holds, query = self.verbs.condition_holds(cond, e["source"], over=e["target"])
        return [] if holds else [f"condition '{cond}' would not hold ({query})"]


def _crowded(card: str, edges: list[Edge]) -> dict[str, str]:
    """The endpoints that would have more edges of the type than its cardinality allows."""
    out: dict[str, str] = {}
    for role, other, ones in (
        ("source", "targets", ONE_TARGET),
        ("target", "sources", ONE_SOURCE),
    ):
        counts = Counter(e[role] for e in edges)
        if card in ones:
            out.update(
                {
                    n: f"{n} would have several {other} under {card}"
                    for n, k in counts.items()
                    if k > 1
                }
            )
    return out
