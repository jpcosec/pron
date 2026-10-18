"""The goals that read the world: the only place in this package that asks the store.

Five of them, and the store answers all five: a class, a predicate, a field, an edge, and
a comparison. A world's rules are built out of these; nothing else is available to them.

A read never writes, so it hands back the overlay it was given, unchanged.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from plnr.errors import GoalError
from plnr.sexp import Sym, write
from plnr.terms import Bindings, Step, ground, is_var, unify

if TYPE_CHECKING:
    from plnr.goals import Engine
    from plnr.world import Overlay

PRIMITIVES = ("is", "where", "field", "edge", "compare")
COMPARISONS = ("=", "!=", ">", "<", ">=", "<=")


def read(engine: Engine, goal: Any, b: Bindings, ov: Overlay, depth: int) -> Iterator[Step]:
    """One read of the world. Every row handed back is charged to the budget, so a scan
    over a big class is as answerable-for as a deep chain of theorems."""
    head = str(goal[0])
    reader = _READERS.get(head)
    if reader is None:
        raise GoalError(f"not a primitive: ({head} …)")
    for b1 in reader(engine, goal, b, ov, depth):
        engine.budget.charge()
        yield b1, ov


def _is(engine: Engine, goal: Any, b: Bindings, ov: Overlay, depth: int) -> Iterator[Bindings]:
    if len(goal) != 3:
        raise GoalError("(is DOC MODEL) takes two arguments")
    doc, model = ground(goal[1], b), ground(goal[2], b)
    if not is_var(doc):
        actual = ov.model_of(doc)
        if actual is None:
            return
        nxt = unify(goal[2], Sym(actual), b)
        if nxt is not None:
            yield nxt
        return
    for name in ov.docs(None if is_var(model) else str(model)):
        nxt = unify(goal[1], Sym(name), b)
        if nxt is None:
            continue
        nxt = unify(goal[2], Sym(str(ov.model_of(name))), nxt)
        if nxt is not None:
            yield nxt


def _where(
    engine: Engine, goal: Any, b: Bindings, ov: Overlay, depth: int
) -> Iterator[Bindings]:
    if len(goal) != 3:
        raise GoalError("(where DOC PREDICATE) takes two arguments")
    doc, predicate = ground(goal[1], b), ground(goal[2], b)
    if is_var(predicate):
        raise GoalError("(where …) needs a ground predicate")
    if is_var(doc):
        for name in ov.docs():
            if ov.matches(name, str(predicate)):
                nxt = unify(goal[1], Sym(name), b)
                if nxt is not None:
                    yield nxt
        return
    if ov.matches(str(doc), str(predicate)):
        yield b


def _field(
    engine: Engine, goal: Any, b: Bindings, ov: Overlay, depth: int
) -> Iterator[Bindings]:
    if len(goal) != 4:
        raise GoalError("(field DOC NAME VALUE) takes three arguments")
    doc, name = ground(goal[1], b), ground(goal[2], b)
    docs = [str(doc)] if not is_var(doc) else list(ov.docs())
    for d in docs:
        payload = ov.payload(d)
        for f in [str(name)] if not is_var(name) else list(payload):
            if f not in payload:
                continue
            nxt = unify(goal[1], Sym(d), b)
            nxt = None if nxt is None else unify(goal[2], Sym(f), nxt)
            nxt = None if nxt is None else unify(goal[3], payload[f], nxt)
            if nxt is not None:
                yield nxt


def _edge(
    engine: Engine, goal: Any, b: Bindings, ov: Overlay, depth: int
) -> Iterator[Bindings]:
    if len(goal) != 4:
        raise GoalError("(edge RELATION SRC TGT) takes three arguments")
    rel, src, tgt = (ground(x, b) for x in goal[1:4])
    for r, s, t in ov.edges(
        None if is_var(rel) else str(rel),
        None if is_var(src) else str(src),
        None if is_var(tgt) else str(tgt),
    ):
        nxt = unify(goal[1], Sym(r), b)
        nxt = None if nxt is None else unify(goal[2], Sym(s), nxt)
        nxt = None if nxt is None else unify(goal[3], Sym(t), nxt)
        if nxt is not None:
            yield nxt


def _compare(
    engine: Engine, goal: Any, b: Bindings, ov: Overlay, depth: int
) -> Iterator[Bindings]:
    """The one primitive that reads nothing: comparing two numbers is not knowledge about a
    world, so it lives here instead of in every world's rules."""
    if len(goal) != 4:
        raise GoalError("(compare OP A B) takes three arguments")
    op, left, right = (ground(x, b) for x in goal[1:4])
    if str(op) not in COMPARISONS:
        raise GoalError(f"(compare …) cannot use {write(op)}")
    if is_var(left) or is_var(right):
        raise GoalError("(compare …) needs both sides ground")
    if holds(str(op), left, right):
        yield b


def holds(op: str, left: Any, right: Any) -> bool:
    if op in ("=", "!="):
        same = left == right or str(left) == str(right)
        return same if op == "=" else not same
    try:
        lt, rt = float(left), float(right)
    except (TypeError, ValueError):
        return False
    return {">": lt > rt, "<": lt < rt, ">=": lt >= rt, "<=": lt <= rt}[op]


_READERS = {
    "is": _is,
    "where": _where,
    "field": _field,
    "edge": _edge,
    "compare": _compare,
}
