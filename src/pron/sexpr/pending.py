"""A pending question of the dialogue (spec 06), of one of two kinds: a `choice` between
candidates the session already resolved, or the `data` a write still needs. It carries the
move that opened it, the sentence that did, and whatever state the session needs to resume.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Pending:
    kind: str  # choice | data
    move_id: str  # the move that opened it
    sentence: str
    candidates: list[str] = field(default_factory=list)  # addresses (choice)
    labels: list[str] = field(default_factory=list)  # natural names, same order
    slot: str = ""  # what the answer fills: "subject" / "object" / a field name
    field_name: str | None = None  # data: the missing field
    model: str | None = None
    state: dict[str, Any] = field(
        default_factory=dict
    )  # whatever the session needs to resume
