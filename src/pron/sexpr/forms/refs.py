"""What a word names, as a form (spec 05, 13). Every word of the lexicon has one: a model is
(model M), a field (field M f), a value (value M f v), a relation (relation R), a verb of the
kernel (action verb). An alias writes its own:

    (model Client)                                   a noun
    (field Client name)                              an attribute
    (where Table "capacity >= N")                    an adjective; N, X, Z and {field} are its slots
    (relation assigned_to)                           a transitive verb
    (change (it "it" Reservation) status "confirmed")   an action with a fixed field and value
    (doc "SurfaceDoc:surface-pron-infra-projector")  a proper name
    (move (create Reservation)                       a composed sentence: (created) is what the
          (assert booked_by (created) (it "her" Client))    create left, (it …) the referent of
          (assert assigned_to (created) (a Table)))         the sentence, (a M) its phrase of class M

The seven older string forms (model:M, field:M.f, predicate:M:<where>, relation:R,
action:<verb> M.f=v, doc:M:name, compose with steps) are read and turned into these.
"""

from __future__ import annotations

import re
from typing import Any

from pron.kernel.sexp.read_write import Sym, read_one, write
from pron.sexpr.forms.ref import Ref

KERNEL_WRITES = ("change", "add", "remove", "clean", "forget")


def parse(ref: str, steps: list[dict[str, Any]] | None = None) -> Ref:
    """A ref as an alias declares it, in either syntax."""
    text = str(ref).strip()
    if text.startswith("("):
        return of_form(read_one(text))
    return of_form(_legacy(text, steps or []))


def of_form(form: Any) -> Ref:
    head = _head(form)
    if head == "model":
        return Ref(form, "model", model=str(form[1]))
    if head == "field":
        return Ref(form, "field", model=str(form[1]), field_name=str(form[2]))
    if head == "value":
        return Ref(
            form, "value", model=str(form[1]), field_name=str(form[2]), value=form[3]
        )
    if head == "where":
        return Ref(form, "predicate", model=str(form[1]), where=str(form[2]))
    if head == "relation":
        return Ref(form, "relation", relation=str(form[1]))
    if head == "action":
        return Ref(form, "action", verb=str(form[1]))
    if head == "doc":
        eid = str(form[1])
        return Ref(form, "doc", model=eid.split(":", 1)[0])
    if head in KERNEL_WRITES:
        target = form[1]
        model = (
            str(target[2])
            if _head(target) in ("it", "them") and len(target) > 2
            else None
        )
        return Ref(
            form,
            "action",
            model=model,
            field_name=str(form[2]) if len(form) > 2 else None,
            verb=head,
            value=form[3] if len(form) > 3 else None,
        )
    if head in ("move", "create", "assert"):
        body = form[1:] if head == "move" else [form]
        return Ref(form, "compose", steps=[_step(s) for s in body])
    raise ValueError(f"not a ref: {write(form)}")


def _step(form: Any) -> dict[str, Any]:
    head = _head(form)
    if head == "create":
        return {"do": "create", "model": str(form[1]), "fields": "$literals"}
    if head == "assert":
        return {
            "do": "assert",
            "relation": str(form[1]),
            "source": _slot(form[2]),
            "target": _slot(form[3]),
        }
    if head == "change":
        return {
            "do": "change",
            "target": _slot(form[1]),
            "field": str(form[2]),
            "value": form[3],
        }
    raise ValueError(
        f"a composed sentence takes create, assert and change, not ({head} …)"
    )


def _slot(noun: Any) -> str:
    head = _head(noun)
    if head == "created":
        return "$created"
    if head in ("it", "them"):
        return f"$referent:{noun[2]}" if len(noun) > 2 else "$referent:"
    if head in ("a", "the", "all"):
        return f"$object:{noun[1]}"
    raise ValueError(
        f"a slot of a composed sentence is (created), (it …) or (a M), not ({head} …)"
    )


def _noun_of_slot(slot: str) -> Any:
    if slot == "$created":
        return [Sym("created")]
    kind, _, model = slot[1:].partition(":")
    if kind == "referent":
        return [Sym("it"), "it"] + ([Sym(model)] if model else [])
    return [Sym("a"), Sym(model)]


def _legacy(ref: str, steps: list[dict[str, Any]]) -> Any:
    head, _, rest = ref.partition(":")
    if head == "model":
        return [Sym("model"), Sym(rest)]
    if head == "field":
        m, f = rest.split(".", 1)
        return [Sym("field"), Sym(m), Sym(f)]
    if head == "value":
        mf, v = rest.split("=", 1)
        m, f = mf.split(".", 1)
        return [Sym("value"), Sym(m), Sym(f), v]
    if head == "predicate":
        m, where = rest.split(":", 1)
        return [Sym("where"), Sym(m), where]
    if head == "relation":
        return [Sym("relation"), Sym(rest)]
    if head == "doc":
        return [Sym("doc"), rest]
    if head == "action":
        verb, _, assign = rest.partition(" ")
        if not assign:
            return [Sym("action"), Sym(verb)]
        mf, value = assign.split("=", 1)
        m, f = mf.split(".", 1)
        return [Sym(verb), [Sym("it"), "it", Sym(m)], Sym(f), value]
    if ref == "compose":
        body = []
        for s in steps:
            if s.get("do") == "create":
                body.append([Sym("create"), Sym(s["model"])])
            elif s.get("do") == "assert":
                body.append(
                    [
                        Sym("assert"),
                        Sym(s["relation"]),
                        _noun_of_slot(s["source"]),
                        _noun_of_slot(s["target"]),
                    ]
                )
            elif s.get("do") == "change":
                body.append(
                    [
                        Sym("change"),
                        _noun_of_slot(s["target"]),
                        Sym(s["field"]),
                        s["value"],
                    ]
                )
        return [Sym("move"), *body]
    raise ValueError(f"not a ref: {ref!r}")


def _head(form: Any) -> str:
    if not isinstance(form, list) or not form or not isinstance(form[0], Sym):
        raise ValueError(f"not a form: {write(form)}")
    return str(form[0])


def models_and_relations(ref: Ref) -> tuple[set[str], set[str]]:
    """Every model and relation a ref names, for the projection check (spec 05)."""
    models = {ref.model} if ref.model else set()
    relations = {ref.relation} if ref.relation else set()
    for s in ref.steps:
        if s.get("model"):
            models.add(s["model"])
        if s.get("relation"):
            relations.add(s["relation"])
        for key in ("source", "target"):
            slot = s.get(key)
            if isinstance(slot, str) and ":" in slot and slot.split(":", 1)[1]:
                models.add(slot.split(":", 1)[1])
    return models, relations


SLOT_WORDS = re.compile(r"\b(N|X|Z|DAY|TIME)\b")
