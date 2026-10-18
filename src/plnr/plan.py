"""Running a plan: search to the end over an overlay, then hand over what to write.

This is the seam this package stops at. A plan is a goal; running it searches for one way
to satisfy it whole, over an overlay, touching nothing. What comes back is the bindings it
found, the writes it would make, and the trace that proves it. Committing those writes —
against a store's own verbs, its coercion, its roundtrip and its ledger — is outside, and
deliberately so: nothing in here can write.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from plnr.errors import Exhausted, GoalError, WorldError
from plnr.goals import Budget, Engine, Trace
from plnr.sexp import Sym, write
from plnr.terms import Bindings, Step, ground, variables
from plnr.theorems import Theorems
from plnr.world import Overlay, World


@dataclass
class Plan:
    """What a search concluded: whether it holds, with what values, and what it would write."""

    ok: bool
    bindings: Bindings | None
    writes: list[Any] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)
    reason: str = ""
    failure: str = ""  # "" | malformed | budget | world | absent | none
    spent: int = 0
    wanted: list[str] = field(default_factory=list)

    def value(self, var: str) -> Any:
        """What a variable of the plan came out as."""
        if self.bindings is None:
            raise KeyError(var)
        return ground(Sym(var), self.bindings)

    def answers(self) -> dict[str, Any]:
        """The variables of the goal as asked, and what they came out as.

        Only those: the engine renames a theorem's variables on every use, and those names
        are bookkeeping of the search, not part of the answer.
        """
        if self.bindings is None:
            return {}
        return {v: self.value(v) for v in self.wanted if Sym(v) in self.bindings}

    def as_forms(self) -> list[str]:
        return [write(w) for w in self.writes]

    def __bool__(self) -> bool:
        return self.ok


def run(
    goal: Any,
    world: World,
    theorems: Theorems | None = None,
    budget: int = 10_000,
    trace: bool = True,
    overlay: Overlay | None = None,
) -> Plan:
    """Search for one way to satisfy the goal; write nothing.

    A goal that cannot be satisfied comes back as a refusal with the trace that shows where
    it died, which is the same shape as a goal that ran out of budget: both are answers,
    neither is an exception to the caller.
    """
    entry = Overlay(world) if overlay is None else overlay
    inherited = len(entry.all_writes())
    wanted = variables(goal)
    engine = Engine(world, theorems, budget=Budget(budget), trace=Trace(enabled=trace))

    def refusal(reason: str, failure: str) -> Plan:
        """One shape of refusal, four reasons: no solution, malformed, out of budget, and a
        world that could not answer. All four are answers, none is an exception."""
        return Plan(
            False,
            None,
            trace=list(engine.trace),
            reason=reason,
            failure=failure,
            spent=engine.budget.spent,
            wanted=wanted,
        )

    try:
        found = engine.prove(goal, overlay=Overlay(entry))
    except Exhausted as e:
        return refusal(str(e), "budget")
    except WorldError as e:
        failure = "absent" if e.absent else "world"
        return refusal(f"the world could not answer: {e}", failure)
    except GoalError as e:
        return refusal(f"malformed goal: {e}", "malformed")
    if found is None:
        return refusal("the goal has no solution over this world", "none")
    bindings, ov = found
    return Plan(
        True,
        bindings,
        writes=ov.all_writes()[inherited:],
        trace=list(engine.trace),
        spent=engine.budget.spent,
        wanted=wanted,
    )


def solutions(
    goal: Any,
    world: World,
    theorems: Theorems | None = None,
    budget: int = 10_000,
    limit: int | None = None,
    overlay: Overlay | None = None,
) -> list[Bindings]:
    """Every way to satisfy a goal, for a reader that wants the whole set.

    Only the bindings come back: what each branch would write belongs to that branch, and a
    caller asking for all of them is reading, not planning.
    """
    entry = Overlay(world) if overlay is None else overlay
    engine = Engine(world, theorems, budget=Budget(budget))
    out: list[Bindings] = []
    stream: Iterator[Step] = engine.solve(goal, overlay=Overlay(entry))
    for bindings, _ in stream:
        out.append(bindings)
        if limit is not None and len(out) >= limit:
            break
    return out
