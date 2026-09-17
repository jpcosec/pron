"""Ranking candidates for a query (spec 11 §2): with an Embedder when the application gave
one, difflib otherwise. `cosine` is the similarity over two vectors. Neither ever executes
anything: they only rank neighbors to offer.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Sequence

from pron.world.matching.difflib_matcher import DifflibMatcher
from pron.world.matching.embedder_protocol import Embedder


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


class Matcher:
    """Ranks candidates for a query with an Embedder when given, difflib otherwise."""

    def __init__(
        self, embedder: Embedder | None = None, cache_path: Path | None = None
    ):
        self.embedder = embedder
        self.fallback = DifflibMatcher()
        self._cache: dict[str, list[float]] = {}
        self.cache_path: Path | None = None
        self.bind_cache(cache_path)

    def bind_cache(self, path: Path | None) -> None:
        """Keep the vectors in a derived file (spec 11 §2: `.pron/lexicon.<hash>.<projection>.<embedder>.json`).
        Only with an Embedder; difflib has nothing to cache."""
        self.cache_path = path if self.embedder is not None else None
        self._cache = {}
        if self.cache_path is not None and self.cache_path.exists():
            try:
                self._cache = json.loads(self.cache_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                self._cache = {}

    def id(self) -> str:
        return self.embedder.id() if self.embedder else self.fallback.id()

    def rank(
        self,
        query: str,
        candidates: Sequence[tuple[str, str]],
        k: int = 3,
        threshold: float = 0.0,
    ) -> list[tuple[str, float]]:
        """candidates are (key, text). Returns [(key, score)] best first, above threshold."""
        if self.embedder is None:
            scored = [
                (key, self.fallback.similarity(query, text)) for key, text in candidates
            ]
        else:
            # an embedder adds meaning, it does not remove spelling: a typo ("fcts") stays
            # near by string similarity even when its vector lands nowhere near "facts"
            vectors = self._embed([query, *[t for _, t in candidates]])
            scored = [
                (key, max(cosine(vectors[0], v), self.fallback.similarity(query, text)))
                for (key, text), v in zip(candidates, vectors[1:])
            ]
        best: dict[str, float] = {}
        for key, score in scored:
            if score >= threshold and score > best.get(key, -1):
                best[key] = score
        return sorted(best.items(), key=lambda kv: -kv[1])[:k]

    def _embed(self, texts: list[str]) -> list[list[float]]:
        assert self.embedder is not None
        missing = [t for t in texts if t not in self._cache]
        if missing:
            for t, v in zip(missing, self.embedder.embed(missing)):
                self._cache[t] = v
            if self.cache_path is not None:
                try:
                    self.cache_path.parent.mkdir(parents=True, exist_ok=True)
                    self.cache_path.write_text(
                        json.dumps(self._cache), encoding="utf-8"
                    )
                except OSError:
                    pass
        return [self._cache[t] for t in texts]
