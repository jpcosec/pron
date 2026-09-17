"""How a session reads its projection (spec 01, 05, 11 §8): which projection, from which home
store, whether read-only, whether a refresh waits for the end of a move, and the date a
sentence's relative dates are read against. Fixed for the session's life.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectionSettings:
    """How a session reads its projection (spec 01, 05, 11 §8): fixed for its life."""

    name: str
    home: str | None
    read_only: bool
    defer_refresh: bool
    now: object
