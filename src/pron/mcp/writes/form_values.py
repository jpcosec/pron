"""The atoms of a compiled form (spec 13, 14 §4): a name the form reads as a symbol, a value
as a form writes it, and a document by id. JSON never becomes form text by concatenation: a
symbol must be a plain identifier, a value one of the types forms have, and the printer
escapes every string (spec 13, `pron.kernel.sexp.read_write.write`).
"""

from __future__ import annotations

import re
from typing import Any

from pron.kernel.sexp.read_write import Sym
from pron.mcp.writes.arg_error import ArgError
from pron.sexpr.forms.syntax import value_form

IDENTIFIER = re.compile(r"[A-Za-z_][\w]*\+?")
ATOMS = (str, int, float, bool, type(None))


def symbol(name: Any, what: str = "name") -> Sym:
    """A model, field or relation name, as the bare symbol a form reads."""
    if not isinstance(name, str) or not IDENTIFIER.fullmatch(name):
        raise ArgError(f"{what} must be an identifier, got {name!r}")
    return Sym(name)


def value(v: Any) -> Any:
    """A JSON value as a form writes it: a string, number, bool or null, or a list of them
    (`(list …)`); an object has no form."""
    if isinstance(v, (list, tuple)):
        return value_form([value(x) for x in v])
    if not isinstance(v, ATOMS):
        raise ArgError(f"a value is a string, number, bool, null or list; got {v!r}")
    return v


def doc(export_id: Any) -> list[Any]:
    """`(doc "Model:name")`: a document by its export id."""
    if not isinstance(export_id, str) or ":" not in export_id:
        raise ArgError(f"a document id is 'Model:name', got {export_id!r}")
    return [Sym("doc"), export_id]
