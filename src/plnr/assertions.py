"""The goals that write, which here means: leave a pending assertion in the overlay.

Three of them, and none touches the store. The overlay they write to is the one they were
handed for this branch, so a failed branch is simply an overlay nobody reads again — no
rollback, no trail, nothing to undo.

After an assertion, the world's antecedent theorems get their turn: the forward half of a
theorem, what follows *because* something was asserted. They run over the same overlay, so
what they conclude is pending like everything else, and they cannot undo the assertion that
woke them: forward chaining here adds, never retracts.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from plnr.errors import GoalError
from plnr.sexp import Sym, write
from plnr.terms import Bindings, Step, ground, is_var, refresh, unify, variables
from plnr.world import Overlay

if TYPE_CHECKING:
    from plnr.goals import Engine

ASSERTIONS = ("assert-edge", "assert-field", "assert-doc")

_ASSERTED = {"assert-edge": "edge", "assert-field": "field", "assert-doc": "is"}


def assert_pending(
    engine: Engine, goal: Any, b: Bindings, ov: Overlay, depth: int
) -> Iterator[Step]:
    """An assertion: check it is ground, leave it in the overlay, then let it fire."""
    head = str(goal[0])
    args = [ground(x, b) for x in goal[1:]]
    for a in args:
        if is_var(a) or variables(a):
            raise GoalError(f"({head} …) needs ground arguments: {write(goal)}")
    engine.trace.enter(depth, f"{head} {' '.join(write(a) for a in args)} (pending)")
    if head == "assert-edge":
        ov.link(str(args[0]), str(args[1]), str(args[2]))
    elif head == "assert-field":
        ov.set_field(str(args[0]), str(args[1]), args[2])
    else:
        ov.create(str(args[1]), str(args[0]))
    yield from _fire(engine, head, args, b, ov, depth)


def _fire(
    engine: Engine, head: str, args: list[Any], b: Bindings, ov: Overlay, depth: int
) -> Iterator[Step]:
    """Antecedent theorems (THANTE): every one that applies, in the order declared.

    A theorem that concludes something is a branch of the same search, so it gets a fork:
    if the rest of the plan later fails, what it concluded goes with the fork.
    """
    fact = [Sym(_ASSERTED[head]), *args]
    fired = list(engine.theorems.antecedents(str(fact[0])))
    if not fired:
        yield b, ov
        return
    streams: list[Step] = [(b, ov)]
    for theorem in fired:
        following: list[Step] = []
        for b0, ov0 in streams:
            tag = engine.next_tag()
            opened = unify(refresh(theorem.pattern, tag), fact, b0)
            if opened is None:
                following.append((b0, ov0))
                continue
            engine.trace.enter(depth + 1, f"then {theorem.name}")
            body = [Sym("and"), *(refresh(x, tag) for x in theorem.body)]
            applied = False
            for step in engine.solve(body, opened, Overlay(ov0), depth + 2):
                applied = True
                following.append(step)
            if not applied:
                # an antecedent that does not apply leaves the assertion standing
                engine.trace.enter(depth + 2, f"{theorem.name} did not apply")
                following.append((b0, ov0))
        streams = following
    yield from streams
