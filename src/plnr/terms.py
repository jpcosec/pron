"""Variables, bindings and unification over the forms of sexp.py.

A variable is a symbol that starts with '?'. A binding is an immutable mapping from
variable name to a ground value, and an answer of the search is a binding plus the overlay
of pending writes that comes with it (Step). Nothing is shared between one answer and the
next, so backtracking is simply not reading the branch that failed: there is no trail and
no rollback, because there is nothing to undo.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, Any

from plnr.sexp import Sym, is_symbol, write

if TYPE_CHECKING:
    from plnr.world import Overlay

# An answer of the search: the bindings it found and the pending writes that come with it.
# Backtracking is pulling the next one, so the writes of a branch never outlive it.
Step = tuple["Bindings", "Overlay"]


class Bindings(Mapping[str, Any]):
    """An immutable variable → value map, extended by making a new one."""

    __slots__ = ("_d",)

    def __init__(self, d: Mapping[str, Any] | None = None):
        self._d: dict[str, Any] = dict(d or {})

    def __getitem__(self, k: str) -> Any:
        return self._d[k]

    def __iter__(self) -> Iterator[str]:
        return iter(self._d)

    def __len__(self) -> int:
        return len(self._d)

    def with_(self, name: str, value: Any) -> Bindings:
        d = dict(self._d)
        d[name] = value
        return Bindings(d)

    def __repr__(self) -> str:
        inner = " ".join(f"{k}={write(v)}" for k, v in sorted(self._d.items()))
        return f"<{inner}>" if inner else "<>"


EMPTY = Bindings()


def is_var(x: Any) -> bool:
    """A variable is a symbol whose name starts with '?', whoever read the form."""
    return is_symbol(x) and str(x).startswith("?")


def ground(form: Any, b: Bindings) -> Any:
    """The form with every bound variable replaced; unbound variables stay as they are."""
    if is_var(form):
        return ground(b[form], b) if form in b else form
    if isinstance(form, list):
        return [ground(x, b) for x in form]
    return form


def is_ground(form: Any) -> bool:
    if is_var(form):
        return False
    if isinstance(form, list):
        return all(is_ground(x) for x in form)
    return True


def walk(form: Any, b: Bindings) -> Any:
    """A variable followed to what it is bound to, one chain at a time."""
    while is_var(form) and form in b:
        form = b[form]
    return form


def occurs(name: str, form: Any, b: Bindings) -> bool:
    """Does this variable occur in the form, following what is already bound?"""
    form = walk(form, b)
    if is_var(form):
        return str(form) == name
    if isinstance(form, list):
        return any(occurs(name, x, b) for x in form)
    return False


def unify(left: Any, right: Any, b: Bindings) -> Bindings | None:
    """The binding that makes the two forms equal, or None when there is none.

    Two-way: a goal and a theorem's pattern both carry variables. Values read from the
    world arrive ground, so against them this is plain matching.

    A variable is never bound to a form that contains it — the occurs check, and not a
    nicety: `(find all ?x (goal …))` with ?x in nothing would bind ?x to a list holding ?x,
    and following that binding is a stack that never ends.
    """
    left, right = walk(left, b), walk(right, b)
    if is_var(left):
        if left == right:
            return b
        return None if occurs(str(left), right, b) else b.with_(left, right)
    if is_var(right):
        return None if occurs(str(right), left, b) else b.with_(right, left)
    if isinstance(left, list) or isinstance(right, list):
        if not (isinstance(left, list) and isinstance(right, list)):
            return None
        if len(left) != len(right):
            return None
        for x, y in zip(left, right, strict=False):
            nxt = unify(x, y, b)
            if nxt is None:
                return None
            b = nxt
        return b
    if isinstance(left, Sym) or isinstance(right, Sym):
        return b if str(left) == str(right) else None
    if isinstance(left, bool) != isinstance(right, bool):
        return None
    return b if left == right else None


def refresh(form: Any, tag: int) -> Any:
    """The form with every variable renamed for one use of a theorem, so the variables of
    the rule never collide with the variables of the goal that called it."""
    if is_var(form):
        return Sym(f"{form}#{tag}")
    if isinstance(form, list):
        return [refresh(x, tag) for x in form]
    return form


def variables(form: Any) -> list[str]:
    """Every variable of a form, in the order it appears, without repeats."""
    out: list[str] = []

    def walk(f: Any) -> None:
        if is_var(f):
            if f not in out:
                out.append(str(f))
        elif isinstance(f, list):
            for x in f:
                walk(x)

    walk(form)
    return out
