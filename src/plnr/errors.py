"""What this layer refuses, and why refusing is not the same as failing.

A goal that is not well formed, or whose head nobody defines, is an error: a caller has to
know that a typo is not an answer of "no". A search that runs out of budget is a refusal
with a reason, not a hang. Nothing else in this package raises.
"""

from __future__ import annotations


class GoalError(ValueError):
    """A goal that is not well formed, or a head nobody defines."""


class Exhausted(RuntimeError):
    """The step budget ran out: the search is not allowed to run forever."""
