"""The shape of a form (spec 13): its head, the clauses it carries, the heads a noun and a
move may take, and a value as a form writes it — `(list …)` a list, a bare symbol its name.
The compiler, the refs of the lexicon and the renderer read forms through these.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.sexp.read_write import Sym, write
from pron.sexpr.forms.form_error import FormError

NOUN_HEADS = ("doc", "the", "a", "all", "find", "it", "them", "me")
REFERENT_HEADS = {"it": "singular", "them": "plural", "me": "speaker"}
MOVE_HEADS = (
    "show",
    "targets",
    "sources",
    "assert",
    "create",
    "change",
    "add",
    "remove",
    "clean",
    "forget",
    "say",
    "undo",
    "refresh",
    "why",
    "move",
)


def form_head(form: Any, error: type[ValueError] = FormError) -> str:
    """The head symbol of a form; `error` when it is not one."""
    if not isinstance(form, list) or not form or not isinstance(form[0], Sym):
        raise error(f"not a form: {write(form)}")
    return str(form[0])


def is_clause(form: Any, name: str) -> bool:
    return isinstance(form, list) and bool(form) and form[0] == Sym(name)


def unvalue(v: Any) -> Any:
    """A value as a form writes it, as Python holds it."""
    if isinstance(v, list) and v and v[0] == Sym("list"):
        return [unvalue(x) for x in v[1:]]
    if isinstance(v, Sym):
        return str(v)
    return v
