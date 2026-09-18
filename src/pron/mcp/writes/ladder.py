"""The ladder of mutability at a tool's door (spec 14 §5): a tool of a level higher than the
session's answers `error` without evaluating anything, and says which level it would need.
The level is the session's, out of its projection; never an argument of the tool.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.world.mutability import NAMES, level_of

if TYPE_CHECKING:
    from pron.session import Session


class Ladder:
    """One session's level, and the check a tool makes against it."""

    def __init__(self, session: Session):
        self.session = session

    @property
    def level(self) -> int:
        """read_only is level 0 (its load wrote that into its projection); else the
        projection's `mutability`, 1 when absent."""
        return level_of(self.session.projection)

    def requires(self, needed: int) -> dict[str, Any] | None:
        """None when the session may; else the tool's answer, an error."""
        have = self.level
        if have >= needed:
            return None
        return {
            "text": f"This needs level {needed} ({NAMES[needed]}) of mutability; "
            f"this session is at level {have} ({NAMES[have]}).",
            "outcome": "error",
            "move_id": "",
            "writes": [],
            "level": {"needed": needed, "session": have},
        }
