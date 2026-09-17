"""What every phase of a move shares (spec 06, 11): the session it works over.

Planning, pre-validating and executing a move are one class each, and each of them needs
the same handful of things — the world, the lexicon, the projection's kernel, the dialogue.
A collaborator keeps none of that: it holds the session and reads through it, so whatever
`Session._load` last left after a reload is what the phase sees, without a second copy to
keep current. Collaborators are built at the point of use and thrown away with the turn.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pron.session import Session


class Collaborator:
    """One phase of a move, working over the session that asked for it."""

    def __init__(self, session: "Session"):
        self.s = session
