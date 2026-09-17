"""A ranked document of the corpus (spec 12 §5b): its export id, its score, and the payload
as sldb extracted it. Indexable by key too, for a consumer that expects rows.
"""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass


@dataclass(frozen=True)
class Hit:
    """A ranked document. `payload` is the document as sldb extracted it."""

    id: str
    model: str
    name: str
    score: float
    payload: dict[str, Any]
    tags: tuple[str, ...] = ()

    def __getitem__(self, key: str) -> Any:  # dict-ish, for consumers that expect rows
        return getattr(self, key)
