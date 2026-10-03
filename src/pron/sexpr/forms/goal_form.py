"""`(goal PATRÓN …)` (spec 13): a form the world proves instead of pron resolving it.

Nothing is compiled here: the nouns of a goal are variables, not phrases, and who answers
them is the goal engine, over the theorems the world declares as documents. The form is kept
whole, so the move can record it and show it back.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.part import Part
from pron.sexpr.forms.form_error import FormError

if TYPE_CHECKING:
    from pron.sexpr.forms.compiler import Compiler


class GoalForm:
    head = "goal"

    def __call__(self, compiler: Compiler, goal: Any = None) -> Part:
        if goal is None or not isinstance(goal, list):
            raise FormError("(goal PATRÓN …) needs a goal: (goal (free ?t))")
        return Part("plan", payload={"goal": goal})
