"""plnr — the layer between s-expressions and a document store, as a goal search.

Read a form, prove it against a world, and come back with what it would write. Between
those two ends there is nothing else: no grammar, no dialogue, no store. The point of the
package is that the rules live in the world as theorems, and the search — with
backtracking, an explicit theorem list per goal, and a step budget — is what replaces a
fixed table of cases.

    >>> from plnr import MemoryWorld, Theorems, read_one, run
    >>> world = MemoryWorld({"t12": ("Table", {"capacity": 6, "zone": "terrace"})})
    >>> plan = run(read_one('(goal (where ?t "capacity >= 6"))'), world)
    >>> bool(plan), plan.value("?t")
    (True, 't12')
"""

from __future__ import annotations

from plnr.errors import Exhausted, GoalError, WorldError
from plnr.goals import Budget, Engine, Trace
from plnr.plan import Plan, run, solutions
from plnr.sexp import SexpError, Sym, read_all, read_one, write
from plnr.terms import EMPTY, Bindings, ground, is_var, unify, variables
from plnr.theorems import Theorem, TheoremError, Theorems, read_theorem
from plnr.world import Edge, MemoryWorld, Overlay, World, payload_matches

__all__ = [
    "Bindings",
    "Budget",
    "EMPTY",
    "Edge",
    "Engine",
    "Exhausted",
    "GoalError",
    "MemoryWorld",
    "Overlay",
    "Plan",
    "SexpError",
    "Sym",
    "Theorem",
    "TheoremError",
    "Theorems",
    "Trace",
    "World",
    "WorldError",
    "ground",
    "is_var",
    "payload_matches",
    "read_all",
    "read_one",
    "read_theorem",
    "run",
    "solutions",
    "unify",
    "variables",
    "write",
]
