"""What a move did, as forms (spec 07, 13): the form a part said with every noun replaced by
the documents it resolved to — a composition's slots too, with the alternatives an `any`
passed over — and `(why)` naming the document the dialogue meant.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from pron.kernel.parts.part import Part
from pron.kernel.sexp.read_write import Sym
from pron.sexpr.execution.why_executor import why_target
from pron.sexpr.forms.syntax import NOUN_HEADS, is_clause
from pron.sexpr.resolving.resolution import address_to_export_id

if TYPE_CHECKING:
    from pron.sexpr.turn.turn_tools import TurnTools

Plan = dict[str, Any]


class AddressedPart:
    """A said form, its nouns replaced in place by the addresses the plan resolved."""

    def __init__(self, tools: TurnTools):
        self.tools = tools

    def __call__(self, form: list[Any], part: Part, plan: Plan) -> list[Any]:
        if part.kind == "why":
            target = why_target(part, self.tools.dialogue)
            return [Sym("why"), [Sym("doc"), target]] if target else form
        if part.kind in FILLS:
            FILLS[part.kind](form, part, plan)
        return form


def _subject(form: list[Any], part: Part, plan: Plan) -> None:
    """(show NOUN), (verb NOUN …), or an action alias's (say alias NOUN); an action whose
    plan resolved no subject (a create) keeps its form."""
    if part.kind == "nominal" or "subject" in plan:
        form[2 if form[0] == Sym("say") else 1] = _doc(plan["subject"])


def _assert(form: list[Any], part: Part, plan: Plan) -> None:
    form[2], form[3] = _doc(plan["subject"]), _doc(plan["object"])


def _doc(res: Any) -> list[Any]:
    return [Sym("doc"), *res.export_ids()]


def _read(form: list[Any], part: Part, plan: Plan) -> None:
    role = "subject" if form[0] == Sym("targets") else "object"
    if role in plan and len(form) > 2 and _is_noun(form[2]):
        form[2] = _doc(plan[role])


def _compose(form: list[Any], part: Part, plan: Plan) -> None:
    by_slot = {}
    steps = part.verb.payload.get("steps", []) if part.verb else []
    for step, res_by_key in zip(steps, plan["steps"]):
        for key, res in res_by_key.items():
            by_slot[step[key]] = res
    for item in form[2:]:
        if is_clause(item, "slot") and item[1] in by_slot:
            _fill_slot(item, by_slot[item[1]])


def _fill_slot(item: list[Any], res: Any) -> None:
    item[2] = _doc(res)
    if res.candidates and res.note.startswith("any"):
        item.append(
            [Sym("alternatives"), *[address_to_export_id(c) for c in res.candidates]]
        )


def _is_noun(form: Any) -> bool:
    return (
        isinstance(form, list)
        and bool(form)
        and isinstance(form[0], Sym)
        and str(form[0]) in NOUN_HEADS
    )


FILLS: dict[str, Callable[[list[Any], Part, Plan], None]] = {
    "nominal": _subject,
    "action": _subject,
    "read": _read,
    "assert": _assert,
    "compose": _compose,
}
