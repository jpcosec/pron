"""One document of the corpus (spec 12 §5b), identified as the world exports it: the export
id (`Model:doc`, `store:Model:doc`), never the bare name — two stores of a federated world
may hold the same document name.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CorpusEntry:
    """One document of the corpus, identified as the world exports it."""

    id: str
    model: str
    name: str
    store: str | None
    text: str
    hash: str
    payload: dict[str, Any] = field(default_factory=dict)
    tags: tuple[str, ...] = ()
