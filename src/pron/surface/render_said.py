"""What one part of a sentence said, as a form (spec 06, 13): one renderer per kind of part,
every noun still the phrase it was — the inverse of the move forms of pron.sexpr.forms. A
role without a phrase is the referent of the class that role needs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from pron.kernel.parts.noun_phrase import NounPhrase
from pron.kernel.parts.part import Part
from pron.kernel.sexp.read_write import Sym
from pron.sexpr.forms.form_error import FormError
from pron.sexpr.forms.syntax import fields_form, value_form
from pron.sexpr.planning.compose_slots import ComposeSlots
from pron.sexpr.planning.needed_model import needed_model
from pron.sexpr.resolving.leftover_predicates import LeftoverPredicates
from pron.surface.render_noun import noun_form

if TYPE_CHECKING:
    from pron.sexpr.turn.turn_tools import TurnTools


class SaidPart:
    """A part as the form a sentence said."""

    def __init__(self, tools: TurnTools):
        self.tools = tools
        self.kinds: dict[str, Callable[[Part], list[Any]]] = {
            "nominal": lambda p: [Sym("show"), self._noun(p, "subject")],
            "read": self._read,
            "assert": self._assert,
            "action": self._action,
            "compose": self._compose,
            # a goal is a form of its own (spec 13): it was never resolved into nouns
            "plan": lambda p: [Sym("goal"), p.payload["goal"]],
            "why": _why,
            "undo": lambda p: [Sym(p.kind)],
            "refresh": lambda p: [Sym(p.kind)],
        }

    def __call__(self, part: Part) -> list[Any]:
        if part.kind not in self.kinds:
            raise FormError(f"a part of kind {part.kind} has no form")
        return self.kinds[part.kind](part)

    def _noun(self, part: Part, role: str) -> list[Any]:
        return noun_form(getattr(part, role), needed_model(part, role, self.tools.lex))

    def _read(self, part: Part) -> list[Any]:
        assert part.verb is not None and part.verb.relation is not None
        asked = part.payload.get("asked", "object")
        targets = asked == "object" and part.subject is not None
        given_role = "subject" if targets else "object"
        given = getattr(part, given_role)
        form: list[Any] = [
            Sym("targets" if targets else "sources"),
            Sym(part.verb.relation),
        ]
        form += [self._noun(part, given_role)] if given is not None else []
        asked_np = part.subject if asked == "subject" else part.object
        if asked_np is not None and asked_np is not given:
            form += self._asked(part, asked_np)
        return form

    def _asked(self, part: Part, asked_np: NounPhrase) -> list[Any]:
        """The class asked about and the predicates the read's leftovers put on it."""
        of = [[Sym("of"), Sym(asked_np.model)]] if asked_np.model else []
        leftovers = LeftoverPredicates(self.tools.world, self.tools.lex)
        return of + [[Sym("where"), w] for w in leftovers(asked_np, part.leftovers)]

    def _assert(self, part: Part) -> list[Any]:
        assert part.verb is not None and part.verb.relation is not None
        subject, obj = self._noun(part, "subject"), self._noun(part, "object")
        return [Sym("assert"), Sym(part.verb.relation), subject, obj]

    def _action(self, part: Part) -> list[Any]:
        verb = part.payload.get(
            "verb", part.verb.payload.get("verb") if part.verb else None
        )
        if verb == "create":
            return _create(part)
        subject = self._noun(part, "subject")
        if part.payload.get("alias") and part.verb is not None:
            return [Sym("say"), Sym(part.verb.payload["symbol"]), subject]
        form: list[Any] = [Sym(verb), subject]
        if part.field_name is not None:
            form.append(Sym(part.field_name))
        if verb in ("change", "add") or (verb == "remove" and part.value is not None):
            form.append(value_form(part.value))
        return form

    def _compose(self, part: Part) -> list[Any]:
        assert part.verb is not None
        form: list[Any] = [Sym("say"), Sym(part.verb.payload["symbol"])]
        for slot, np in ComposeSlots(self.tools.world)(part).items():
            model = slot[1:].partition(":")[2]
            form.append([Sym("slot"), slot, noun_form(np, model or None)])
        if part.payload.get("_name"):
            form.append([Sym("as"), part.payload["_name"]])
        literals = {
            key: v for key, v in part.payload.items() if not key.startswith("_")
        }
        return form + fields_form(literals)


def _create(part: Part) -> list[Any]:
    assert part.subject is not None and part.subject.model is not None
    named = [[Sym("as"), part.payload["name"]]] if part.payload.get("name") else []
    return [
        Sym("create"),
        Sym(part.subject.model),
        *named,
        *fields_form(part.payload["fields"]),
    ]


def _why(part: Part) -> list[Any]:
    target = part.payload.get("target")
    return [Sym("why"), [Sym("doc"), target]] if target else [Sym("why")]
