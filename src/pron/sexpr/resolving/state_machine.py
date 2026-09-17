"""Transitions as guarded field changes (spec 03): the State documents whose `machine` is
`Model.field` name the values the field may take, their `transitions_to` edges the legal
moves between them, and an edge's condition is evaluated over the subject — over the payload
the move is about to leave, when there is one.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.ids import join_id

if TYPE_CHECKING:
    from pron.sexpr.resolving.condition_check import ConditionCheck, Overlay
    from pron.sexpr.resolving.edge_reader import EdgeReader

Verdict = tuple[bool, str, list[str]]


class StateMachine:
    """Whether changing a field from one value to another is legal."""

    def __init__(
        self, reader: EdgeReader, conditions: ConditionCheck, stores: list[str]
    ):
        self.reader, self.conditions, self.stores = reader, conditions, stores
        self.world, self.store = reader.world, reader.store

    def machine(self, model: str, fld: str) -> dict[str, str]:
        """value -> State export id for Model.field, empty when the field has no state documents."""
        out: dict[str, str] = {}
        for s in self.stores:
            if "State" not in self.world.model_names(s):
                continue
            for d in self.store.docs_of("State", s):
                if d.payload.get("machine") == f"{model}.{fld}":
                    out.setdefault(
                        str(d.payload.get("name")),
                        join_id(None if s == "local" else s, "State", d.name),
                    )
        return out

    def transition(
        self,
        model: str,
        fld: str,
        subject: str,
        current: Any,
        new: Any,
        overlay: Overlay | None = None,
    ) -> Verdict:
        """Is changing Model.field from current to new legal for subject? (legal, reason, queries).
        With `overlay`, the condition is evaluated over the payload the move is about to leave."""
        states = self.machine(model, fld)
        if not states:
            return True, "no state machine on this field", []
        src, tgt = states.get(str(current)), states.get(str(new))
        if src is None or tgt is None:
            return (
                False,
                f"no state document for {current!r} or {new!r} on {model}.{fld}",
                [],
            )
        read = self.reader.sldb("source_id", src, "transitions_to")
        queries = list(read.queries)
        edge = next((e for e in read.edges if e["target"] == tgt), None)
        if edge is None:
            return False, f"no transition {current} → {new} on {model}.{fld}", queries
        return self._guarded(
            edge["metadata"].get("condition", ""),
            subject,
            current,
            new,
            overlay,
            queries,
        )

    def _guarded(
        self,
        cond: str,
        subject: str,
        current: Any,
        new: Any,
        overlay: Overlay | None,
        queries: list[str],
    ) -> Verdict:
        """The edge exists: legal when its condition holds over the subject."""
        ok, q = self.conditions.holds(cond, subject, overlay=overlay)
        if q:
            queries.append(q)
        if not ok:
            return (
                False,
                f"cannot go {current} → {new}: the condition is {cond}",
                queries,
            )
        return (
            True,
            f"{current} → {new} is legal" + (f" ({cond})" if cond else ""),
            queries,
        )
