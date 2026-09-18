"""The goal engine over an sldb world (spec 03, 13).

pron resolves a sentence into forms and evaluates them; this package adds one more way to
evaluate: a form whose head is `goal` is *searched*, with the rules the world declares as
TheoremDoc documents, over an overlay that writes nothing. That is where a transition, a
guard or a composed move can be a rule of the world instead of a case in the code.

The store is not touched by the search, and the commit goes through the same kernel verbs a
sentence uses: `pron.plnr.pron_world` is the world as the engine reads it, `theorem_load`
reads the rules, `commit` carries out what the plan promised, and `plan_part` is the part
the turn runs.
"""

from __future__ import annotations

from pron.plnr.commit import Commit
from pron.plnr.plan_execution import PlanExecutor
from pron.plnr.plan_planning import PlanPlanner
from pron.plnr.pron_world import PronWorld
from pron.plnr.theorem_load import TheoremLoad, load_theorems

__all__ = [
    "Commit",
    "PlanExecutor",
    "PlanPlanner",
    "PronWorld",
    "TheoremLoad",
    "load_theorems",
]
