"""The goal language: what a form between an s-expression and a store can ask for.

Every goal evaluates to a stream of answers, and an answer is a pair: the bindings it
found, and the overlay of pending writes that come with it (terms.Step). The overlay is
threaded through the search instead of living on the engine, and that is what makes
backtracking correct: the next answer starts from the overlay the goal was entered with,
so the writes of the branch that failed are not there to be undone — they were never
shared.

    (and G ...)                  every one, threading bindings and overlay left to right
    (or G ...)                   the first that succeeds, then the next on backtracking
    (not G)                      succeeds once when G has no solution; binds nothing
    (goal PATTERN [(use N ...)]) prove PATTERN: primitives first, then theorems
    (find N VAR G)               N solutions of G; N is a number, all, or (at-least N)
    (bind VAR FORM)              bind VAR to FORM as it stands, grounded
    (fail) (succeed)             the two constants

The patterns that read the world are in primitives.py; the ones that leave a pending write
are in assertions.py. A goal with the head of a theorem is proved by that theorem. An
unknown head is an error rather than a failure, so a typo is never silently "no".
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import Any

from plnr import primitives
from plnr.assertions import ASSERTIONS, assert_pending
from plnr.errors import Exhausted, GoalError
from plnr.primitives import PRIMITIVES
from plnr.sexp import Sym, write
from plnr.terms import EMPTY, Bindings, Step, ground, is_var, refresh, unify
from plnr.theorems import Theorem, Theorems
from plnr.world import Overlay, World

__all__ = [
    "ASSERTIONS",
    "PRIMITIVES",
    "Budget",
    "Engine",
    "Exhausted",
    "GoalError",
    "Step",
    "Trace",
    "head_of",
]


def head_of(form: Any) -> str:
    if not isinstance(form, list) or not form or not isinstance(form[0], Sym):
        raise GoalError(f"not a goal: {write(form)}")
    return str(form[0])


@dataclass
class Trace:
    """What the search did, one line per step, and the depth it was at.

    This is the explanation of an answer: the tree of goals that proved it. It is kept as
    text on purpose — whoever records a move writes these lines down as the queries of
    that move.
    """

    lines: list[str] = field(default_factory=list)
    enabled: bool = True

    def enter(self, depth: int, text: str) -> None:
        if self.enabled:
            self.lines.append("  " * depth + text)

    def __iter__(self) -> Iterator[str]:
        return iter(self.lines)

    def __len__(self) -> int:
        return len(self.lines)


@dataclass
class Budget:
    """A cap on goals attempted, MicroPlanner's TIMID: a search that does not finish is a
    refusal with a reason, not a hang."""

    limit: int = 10_000
    spent: int = 0

    def charge(self) -> None:
        self.spent += 1
        if self.spent > self.limit:
            raise Exhausted(f"gave up after {self.limit} goals")


class Engine:
    """Goals over one world, with the theorems of that world and the pending writes of the
    branch being explored."""

    def __init__(
        self,
        world: World,
        theorems: Theorems | None = None,
        budget: Budget | None = None,
        trace: Trace | None = None,
    ):
        self.world = world
        self.theorems = theorems or Theorems()
        self.budget = budget or Budget()
        self.trace = trace if trace is not None else Trace()
        self._tag = 0

    # -- entry -----------------------------------------------------------------------

    def solve(
        self,
        goal: Any,
        b: Bindings | None = None,
        overlay: Overlay | None = None,
        depth: int = 0,
    ) -> Iterator[Step]:
        """Every way this goal succeeds, each with the pending writes of that way."""
        b = EMPTY if b is None else b
        ov = overlay if overlay is not None else Overlay(self.world)
        self.budget.charge()
        head = head_of(goal)
        method = _CONTROL.get(head)
        if method is not None:
            yield from method(self, goal, b, ov, depth)
        elif head in PRIMITIVES:
            yield from primitives.read(self, goal, b, ov, depth)
        elif head in ASSERTIONS:
            yield from assert_pending(self, goal, b, ov, depth)
        else:
            raise GoalError(f"unknown goal: ({head} …)")

    def prove(
        self, goal: Any, b: Bindings | None = None, overlay: Overlay | None = None
    ) -> Step | None:
        """The first way it succeeds, or None."""
        return next(self.solve(goal, b, overlay), None)

    def solutions(
        self, goal: Any, b: Bindings | None = None, overlay: Overlay | None = None
    ) -> list[Bindings]:
        return [bindings for bindings, _ in self.solve(goal, b, overlay)]

    def next_tag(self) -> int:
        """A fresh number for renaming one theorem's variables for one use of it."""
        self._tag += 1
        return self._tag

    # -- control -------------------------------------------------------------------

    def _and(self, goal: Any, b: Bindings, ov: Overlay, depth: int) -> Iterator[Step]:
        parts = goal[1:]
        if not parts:
            yield b, ov
            return
        rest = [Sym("and"), *parts[1:]]
        for b1, ov1 in self.solve(parts[0], b, ov, depth + 1):
            yield from self.solve(rest, b1, ov1, depth)

    def _or(self, goal: Any, b: Bindings, ov: Overlay, depth: int) -> Iterator[Step]:
        for alternative in goal[1:]:
            # each alternative is its own branch: it starts from the overlay as it was
            yield from self.solve(alternative, b, Overlay(ov), depth + 1)

    def _not(self, goal: Any, b: Bindings, ov: Overlay, depth: int) -> Iterator[Step]:
        if len(goal) != 2:
            raise GoalError("(not G) takes one goal")
        self.trace.enter(depth, f"not {write(goal[1])}")
        # into a fork, so proving a negation cannot leave a write behind it
        if next(self.solve(goal[1], b, Overlay(ov), depth + 1), None) is None:
            yield b, ov

    def _succeed(self, goal: Any, b: Bindings, ov: Overlay, depth: int) -> Iterator[Step]:
        yield b, ov

    def _fail(self, goal: Any, b: Bindings, ov: Overlay, depth: int) -> Iterator[Step]:
        return
        yield  # pragma: no cover - a generator that never yields

    def _bind(self, goal: Any, b: Bindings, ov: Overlay, depth: int) -> Iterator[Step]:
        if len(goal) != 3:
            raise GoalError("(bind VAR FORM) takes a variable and a form")
        var, form = goal[1], ground(goal[2], b)
        if not is_var(var):
            raise GoalError(f"(bind …) needs a variable, got {write(var)}")
        nxt = unify(var, form, b)
        if nxt is not None:
            yield nxt, ov

    def _find(self, goal: Any, b: Bindings, ov: Overlay, depth: int) -> Iterator[Step]:
        """(find N VAR G): the values VAR takes over N solutions of G, as a list.

        This is THFIND: how many are wanted is part of the goal, so "the table" and "all
        the tables" differ in the goal, not in the code that answers them. A find is a
        question: whatever its inner goal wrote stays in the fork it wrote to.
        """
        if len(goal) != 4:
            raise GoalError("(find N VAR G) takes a count, a variable and a goal")
        count, var, inner = goal[1], goal[2], goal[3]
        if not is_var(var):
            raise GoalError("(find …) needs a variable")
        wanted, at_least = _count(count)
        found: list[Any] = []
        self.trace.enter(depth, f"find {write(count)} {var} {write(inner)}")
        for b1, _ in self.solve(inner, b, Overlay(ov), depth + 1):
            value = ground(var, b1)
            if value not in found:
                found.append(value)
            # one more than asked for is what tells "the table" from "a table": an exact
            # count has to notice the second one before it can refuse.
            if wanted is not None and len(found) > wanted:
                break
            if at_least and wanted is not None and len(found) >= wanted:
                break
        if wanted is not None and at_least and len(found) < wanted:
            self.trace.enter(depth + 1, f"only {len(found)}, wanted {wanted} or more")
            return
        if wanted is not None and not at_least and len(found) != wanted:
            self.trace.enter(depth + 1, f"found {len(found)}, wanted exactly {wanted}")
            return
        self.trace.enter(depth + 1, f"→ {write(found)}")
        nxt = unify(var, found, b)
        if nxt is not None:
            yield nxt, ov

    def _goal(self, goal: Any, b: Bindings, ov: Overlay, depth: int) -> Iterator[Step]:
        """(goal PATTERN [(use NAME …)]): the world first, then the theorems."""
        if len(goal) < 2:
            raise GoalError("(goal PATTERN …) needs a pattern")
        pattern = goal[1]
        use = _use_clause(goal[2:])
        pattern_head = head_of(pattern)
        self.trace.enter(depth, f"goal {write(ground(pattern, b))}")
        rules = list(self.theorems.consequents(pattern_head, use))
        if pattern_head not in PRIMITIVES and not rules:
            raise GoalError(
                f"nothing proves ({pattern_head} …): no primitive and no theorem for it"
            )
        found = False
        if pattern_head in PRIMITIVES:
            for b1, ov1 in primitives.read(self, pattern, b, ov, depth + 1):
                found = True
                yield b1, ov1
        for theorem in rules:
            for b1, ov1 in self._apply(theorem, pattern, b, Overlay(ov), depth + 1):
                found = True
                yield b1, ov1
        if not found:
            self.trace.enter(depth + 1, "no")

    def _apply(
        self, theorem: Theorem, pattern: Any, b: Bindings, ov: Overlay, depth: int
    ) -> Iterator[Step]:
        """One consequent theorem tried against one goal, in the fork it was given."""
        tag = self.next_tag()
        opened = unify(refresh(theorem.pattern, tag), pattern, b)
        if opened is None:
            return
        self.trace.enter(depth, f"by {theorem.name}")
        body = [Sym("and"), *(refresh(x, tag) for x in theorem.body)]
        yield from self.solve(body, opened, ov, depth + 1)


def _count(count: Any) -> tuple[int | None, bool]:
    """How many solutions `find` wants: a number, `all`, or `(at-least N)`."""
    if isinstance(count, Sym) and str(count) == "all":
        return None, False
    if isinstance(count, bool):
        raise GoalError("(find …) count must be a number, all, or (at-least N)")
    if isinstance(count, int):
        return count, False
    if isinstance(count, list) and len(count) == 2 and str(count[0]) == "at-least":
        return int(count[1]), True
    raise GoalError(f"(find …) cannot count with {write(count)}")


def _use_clause(clauses: Iterable[Any]) -> list[str] | None:
    """`(use NAME …)`, MicroPlanner's THUSE: exactly which theorems may be tried."""
    names: list[str] | None = None
    for clause in clauses:
        if not isinstance(clause, list) or not clause or str(clause[0]) != "use":
            raise GoalError(f"unknown clause in a goal: {write(clause)}")
        names = [str(x) for x in clause[1:]]
    return names


_CONTROL = {
    "and": Engine._and,
    "or": Engine._or,
    "not": Engine._not,
    "goal": Engine._goal,
    "find": Engine._find,
    "bind": Engine._bind,
    "succeed": Engine._succeed,
    "fail": Engine._fail,
}
