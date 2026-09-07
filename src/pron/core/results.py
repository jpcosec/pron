"""Typed result values shared across components.

Implements atom-resolution-outcomes-are-typed-values-not-exceptions: outcomes
are values, exceptions are reserved for bugs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Resolved:
    """A noun resolved to exactly one document."""

    name: str
    model: str
    path: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class Ambiguous:
    """A noun with several candidates; produces dialogue, not failure."""

    question: str
    candidates: list[str]


@dataclass(frozen=True)
class Missing:
    """A noun with no referent; motive explains what was looked for."""

    motive: str
    nearest: list[str]


@dataclass(frozen=True)
class SemanticError:
    """A symbol without anchor or an expression the evaluator cannot ground."""

    symbol: str
    message: str
    hint: str = ""


@dataclass(frozen=True)
class OperationResult:
    """The envelope every operation returns."""

    status: str  # ok | ambiguous | missing | error
    payload: Any = None
    refs: list[str] = field(default_factory=list)
    provenance: str = ""


def to_dict(value: object) -> dict[str, Any]:
    """Project any result value to a JSON-serializable dict."""
    from dataclasses import asdict, is_dataclass

    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    raise TypeError(f"not a result value: {type(value).__name__}")
