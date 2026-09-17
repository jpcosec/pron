"""What a turn answers (spec 06): text, outcome, trace, the move that recorded it and its
record. Light on purpose: a client that talks to a running server imports only this."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Response:
    text: str
    outcome: str
    trace: list[str] = field(default_factory=list)
    move_id: str = ""
    record: dict[str, Any] = field(default_factory=dict)
