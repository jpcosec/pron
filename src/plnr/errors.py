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


class WorldError(RuntimeError):
    """The world could not answer: an id it does not have, a model it does not know, a read
    that failed. The host raises this instead of letting its own exception — a ValueError, a
    StoreError — escape the search: a search that blows up is not an answer.

    `absent` tells the two apart for whoever answers: a name the world does not have is a
    noun that resolved to nothing (what pron calls missing), while a store that refused — an
    unparseable predicate, a read that failed — is an error.
    """

    def __init__(self, message: str, absent: bool = False):
        super().__init__(message)
        self.absent = absent
