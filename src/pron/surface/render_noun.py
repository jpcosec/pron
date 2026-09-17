"""A noun phrase written back as the noun form it says (spec 02, 13): the documents it was
given, the referent of the dialogue it names, or the model with its determiner and clauses —
the inverse of pron.sexpr.forms.noun_compiler.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.parts.noun_phrase import NounPhrase
from pron.kernel.sexp.read_write import Sym
from pron.sexpr.forms.syntax import value_form
from pron.sexpr.resolving.resolution import address_to_export_id

HEADS = {"any": "a", "all": "all"}  # determiner → head; any other is (the …)


def noun_form(np: NounPhrase | None, model: str | None = None) -> list[Any]:
    """`model` is the class the role needs, for a referent that does not name one."""
    if np is None:
        return [Sym("it"), "it"] + ([Sym(model)] if model else [])
    if np.given:
        return [Sym("doc"), *[address_to_export_id(a) for a in np.given]]
    if np.referent is not None:
        return _referent(np, model)
    assert np.model is not None
    head = HEADS.get(np.determiner or "the", "the")
    return [Sym(head), Sym(np.model), *_clauses(np, head)]


def _referent(np: NounPhrase, model: str | None) -> list[Any]:
    assert np.referent is not None
    who = np.referent.meta.get("who")
    head = "me" if who == "speaker" else ("them" if np.number == "plural" else "it")
    form: list[Any] = [Sym(head), np.referent.text]
    hint = np.hint or model
    if head != "me" and hint:
        form.append(Sym(hint))
    return form


def _clauses(np: NounPhrase, head: str) -> list[Any]:
    form: list[Any] = []
    if head == "the" and np.number == "plural":
        form.append([Sym("plural")])
    if np.interrogated:
        form.append([Sym("asked")])
    form += [[Sym("where"), w] for w in np.predicates]
    form += [[Sym("named"), n] for n in np.proper]
    form += [_complement(comp) for comp in np.complements]
    form += [[Sym("set"), Sym(k), value_form(v)] for k, v in np.captures.items()]
    form += [[Sym("not-a-value"), Sym(m), Sym(f), t] for m, f, t in np.unknown_values]
    return form


def _complement(comp: Any) -> list[Any]:
    if isinstance(comp, NounPhrase):
        return [Sym("of"), noun_form(comp)]
    return [Sym("of-name"), *comp]
