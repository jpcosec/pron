"""The other direction of the surface (spec 06, 13): a compiled Part written back as the
forms it says. `said` is what a sentence said, with every noun still a phrase; `resolved` is
what the move did, with every noun replaced by the addresses it resolved to — evaluating that
on the same world in the same state leaves the same writes, without the dialogue.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.noun_phrase import NounPhrase
from pron.kernel.parts.part import Part
from pron.kernel.sexp.read_write import Sym
from pron.sexpr.execution.why_executor import why_target
from pron.sexpr.forms.compiler import NOUN_HEADS, _is_clause
from pron.sexpr.forms.form_error import FormError
from pron.sexpr.planning.compose_slots import ComposeSlots
from pron.sexpr.planning.needed_model import needed_model
from pron.sexpr.resolving.leftover_predicates import LeftoverPredicates
from pron.sexpr.resolving.resolution import address_to_export_id

if TYPE_CHECKING:
    from pron.sexpr.turn.turn_tools import TurnTools


# -- what a sentence says: parts → forms, nouns unresolved -------------------------------------


def said(parts: list[Part], tools: TurnTools) -> Any:
    """tools: the lexicon, world and dialogue of the move, for the class each role needs,
    the slots of a composition and the predicates a read left over."""
    forms = [said_part(p, tools) for p in parts]
    return forms[0] if len(forms) == 1 else [Sym("move"), *forms]


def said_part(part: Part, tools: TurnTools) -> list[Any]:
    k = part.kind
    if k == "nominal":
        return [
            Sym("show"),
            noun_form(part.subject, needed_model(part, "subject", tools.lex)),
        ]
    if k == "read":
        assert part.verb is not None and part.verb.relation is not None
        asked = part.payload.get("asked", "object")
        head = (
            "targets" if asked == "object" and part.subject is not None else "sources"
        )
        given, given_role = (
            (part.subject, "subject") if head == "targets" else (part.object, "object")
        )
        form: list[Any] = [Sym(head), Sym(part.verb.relation)]
        if given is not None:
            form.append(noun_form(given, needed_model(part, given_role, tools.lex)))
        asked_np = part.subject if asked == "subject" else part.object
        if asked_np is not None and asked_np is not given:
            if asked_np.model:
                form.append([Sym("of"), Sym(asked_np.model)])
            for where in LeftoverPredicates(tools.world, tools.lex)(asked_np, part.leftovers):
                form.append([Sym("where"), where])
        return form
    if k == "assert":
        assert part.verb is not None and part.verb.relation is not None
        return [
            Sym("assert"),
            Sym(part.verb.relation),
            noun_form(part.subject, needed_model(part, "subject", tools.lex)),
            noun_form(part.object, needed_model(part, "object", tools.lex)),
        ]
    if k == "action":
        verb = part.payload.get(
            "verb", part.verb.payload.get("verb") if part.verb else None
        )
        if verb == "create":
            assert part.subject is not None and part.subject.model is not None
            named = (
                [[Sym("as"), part.payload["name"]]] if part.payload.get("name") else []
            )
            return [
                Sym("create"),
                Sym(part.subject.model),
                *named,
                *_fields(part.payload["fields"]),
            ]
        subject = noun_form(part.subject, needed_model(part, "subject", tools.lex))
        if part.payload.get("alias") and part.verb is not None:
            return [Sym("say"), Sym(part.verb.payload["symbol"]), subject]
        form = [Sym(verb), subject]
        if part.field_name is not None:
            form.append(Sym(part.field_name))
        if verb in ("change", "add") or (verb == "remove" and part.value is not None):
            form.append(_value(part.value))
        return form
    if k == "compose":
        assert part.verb is not None
        form = [Sym("say"), Sym(part.verb.payload["symbol"])]
        for slot, np in ComposeSlots(tools.world)(part).items():
            model = slot[1:].partition(":")[2]
            form.append([Sym("slot"), slot, noun_form(np, model or None)])
        if part.payload.get("_name"):
            form.append([Sym("as"), part.payload["_name"]])
        literals = {
            key: v for key, v in part.payload.items() if not key.startswith("_")
        }
        form.extend(_fields(literals))
        return form
    if k == "why":
        target = part.payload.get("target")
        return [Sym("why"), [Sym("doc"), target]] if target else [Sym("why")]
    if k in ("undo", "refresh"):
        return [Sym(k)]
    raise FormError(f"a part of kind {k} has no form")


def noun_form(np: NounPhrase | None, model: str | None = None) -> list[Any]:
    if np is None:
        return [Sym("it"), "it"] + ([Sym(model)] if model else [])
    if np.given:
        return [Sym("doc"), *[address_to_export_id(a) for a in np.given]]
    if np.referent is not None:
        who = np.referent.meta.get("who")
        head = "me" if who == "speaker" else ("them" if np.number == "plural" else "it")
        form: list[Any] = [Sym(head), np.referent.text]
        hint = np.hint or model
        if head != "me" and hint:
            form.append(Sym(hint))
        return form
    assert np.model is not None
    head = {"any": "a", "all": "all"}.get(np.determiner or "the", "the")
    form = [Sym(head), Sym(np.model)]
    if head == "the" and np.number == "plural":
        form.append([Sym("plural")])
    if np.interrogated:
        form.append([Sym("asked")])
    form += [[Sym("where"), w] for w in np.predicates]
    form += [[Sym("named"), n] for n in np.proper]
    for comp in np.complements:
        if isinstance(comp, NounPhrase):
            form.append([Sym("of"), noun_form(comp)])
        else:
            form.append([Sym("of-name"), *comp])
    form += [[Sym("set"), Sym(k), _value(v)] for k, v in np.captures.items()]
    form += [[Sym("not-a-value"), Sym(m), Sym(f), t] for m, f, t in np.unknown_values]
    return form


# -- what a move did: every noun as the addresses it resolved to -------------------------------


def resolved(parts: list[Part], plans: list[dict[str, Any]], tools: TurnTools) -> Any:
    """Evaluating this on the same world in the same state leaves the same writes, without the
    dialogue."""
    forms = [
        _by_address(said_part(p, tools), p, plan, tools)
        for p, plan in zip(parts, plans)
    ]
    return forms[0] if len(forms) == 1 else [Sym("move"), *forms]


def _by_address(
    form: list[Any], part: Part, plan: dict[str, Any], tools: TurnTools
) -> list[Any]:
    def doc(res: Any) -> list[Any]:
        return [Sym("doc"), *res.export_ids()]

    k = part.kind
    if k == "nominal" or (k == "action" and "subject" in plan):
        form[1 if k == "nominal" else (2 if form[0] == Sym("say") else 1)] = doc(
            plan["subject"]
        )
    elif k == "read":
        role = "subject" if form[0] == Sym("targets") else "object"
        if role in plan and len(form) > 2 and _is_noun(form[2]):
            form[2] = doc(plan[role])
    elif k == "assert":
        form[2], form[3] = doc(plan["subject"]), doc(plan["object"])
    elif k == "compose":
        by_slot = {}
        steps = part.verb.payload.get("steps", []) if part.verb else []
        for step, res_by_key in zip(steps, plan["steps"]):
            for key, res in res_by_key.items():
                by_slot[step[key]] = res
        for item in form[2:]:
            if _is_clause(item, "slot") and item[1] in by_slot:
                res = by_slot[item[1]]
                item[2] = doc(res)
                if res.candidates and res.note.startswith("any"):
                    item.append(
                        [
                            Sym("alternatives"),
                            *[address_to_export_id(c) for c in res.candidates],
                        ]
                    )
    elif k == "why":
        target = why_target(part, tools.dialogue)
        return [Sym("why"), [Sym("doc"), target]] if target else form
    return form


def _is_noun(form: Any) -> bool:
    return (
        isinstance(form, list)
        and bool(form)
        and isinstance(form[0], Sym)
        and str(form[0]) in NOUN_HEADS
    )


def _fields(fields: dict[str, Any]) -> list[Any]:
    return [[Sym(k), _value(v)] for k, v in fields.items()]


def _value(v: Any) -> Any:
    if isinstance(v, (list, tuple)):
        return [Sym("list"), *[_value(x) for x in v]]
    return v
