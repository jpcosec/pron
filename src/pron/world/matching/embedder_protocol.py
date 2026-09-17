"""The approximate-matching port (spec 11 §2): an application injects an Embedder; without
one, pron falls back to difflib and says so in the trace. It never executes anything, it
only ranks neighbors to offer.
"""

from __future__ import annotations

from typing import Protocol, Sequence


class Embedder(Protocol):
    def id(self) -> str: ...
    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...
