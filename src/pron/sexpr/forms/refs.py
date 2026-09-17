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
action:<verb> M.f=v, doc:M:name, compose with steps) are read and turned into these
(pron.sexpr.forms.legacy_ref); the steps of a composed sentence are pron.sexpr.forms.composed_steps.
"""

from __future__ import annotations

import re
from typing import Any, Callable

from pron.kernel.sexp.read_write import read_one, write
from pron.sexpr.forms.composed_steps import step_of
from pron.sexpr.forms.legacy_ref import legacy_form
from pron.sexpr.forms.ref import Ref
from pron.sexpr.forms.syntax import form_head

KERNEL_WRITES = ("change", "add", "remove", "clean", "forget")


def parse(ref: str, steps: list[dict[str, Any]] | None = None) -> Ref:
    """A ref as an alias declares it, in either syntax."""
    text = str(ref).strip()
    if text.startswith("("):
        return of_form(read_one(text))
    return of_form(legacy_form(text, steps or []))


def of_form(form: Any) -> Ref:
    head = form_head(form, ValueError)
    if head not in KINDS:
        raise ValueError(f"not a ref: {write(form)}")
    return KINDS[head](form)


def _kernel_write(form: Any) -> Ref:
    """(change (it "it" M) field value): the model is the referent's class, when it names one."""
    target = form[1]
    model = (
        str(target[2])
        if form_head(target, ValueError) in ("it", "them") and len(target) > 2
        else None
    )
    return Ref(
        form,
        "action",
        model=model,
        field_name=str(form[2]) if len(form) > 2 else None,
        verb=str(form[0]),
        value=form[3] if len(form) > 3 else None,
    )


def _compose(form: Any) -> Ref:
    body = form[1:] if form_head(form, ValueError) == "move" else [form]
    return Ref(form, "compose", steps=[step_of(s) for s in body])


KINDS: dict[str, Callable[[Any], Ref]] = {
    "model": lambda f: Ref(f, "model", model=str(f[1])),
    "field": lambda f: Ref(f, "field", model=str(f[1]), field_name=str(f[2])),
    "value": lambda f: Ref(
        f, "value", model=str(f[1]), field_name=str(f[2]), value=f[3]
    ),
    "where": lambda f: Ref(f, "predicate", model=str(f[1]), where=str(f[2])),
    "relation": lambda f: Ref(f, "relation", relation=str(f[1])),
    "action": lambda f: Ref(f, "action", verb=str(f[1])),
    "doc": lambda f: Ref(f, "doc", model=str(f[1]).split(":", 1)[0]),
    **{verb: _kernel_write for verb in KERNEL_WRITES},
    **{head: _compose for head in ("move", "create", "assert")},
}


def models_and_relations(ref: Ref) -> tuple[set[str], set[str]]:
    """Every model and relation a ref names, for the projection check (spec 05)."""
    models = {ref.model} if ref.model else set()
    relations = {ref.relation} if ref.relation else set()
    for s in ref.steps:
        if s.get("model"):
            models.add(s["model"])
        if s.get("relation"):
            relations.add(s["relation"])
        models |= _slot_models(s)
    return models, relations


def _slot_models(step: dict[str, Any]) -> set[str]:
    """The classes the source and target slots of a step name, `$object:M` → M."""
    slots = (step.get(key) for key in ("source", "target"))
    return {
        slot.split(":", 1)[1]
        for slot in slots
        if isinstance(slot, str) and ":" in slot and slot.split(":", 1)[1]
    }


SLOT_WORDS = re.compile(r"\b(N|X|Z|DAY|TIME)\b")
