"""The approximate-matching port and its no-network fallback.

An application injects an Embedder (spec 11 §2). Without one, pron matches with
difflib over accent-stripped strings, and says so in the trace. Neither ever
executes anything: they only rank neighbors to offer.
"""

from __future__ import annotations

import json
import math
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Protocol, Sequence


class Embedder(Protocol):
    def id(self) -> str: ...
    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


def normalize(text: str) -> str:
    stripped = "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")
    return " ".join(stripped.lower().split())


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


class DifflibMatcher:
    """Fallback similarity: the best SequenceMatcher ratio between the query and the
    candidate string or any of its words."""

    def id(self) -> str:
        return "difflib"

    def similarity(self, query: str, candidate: str) -> float:
        q, c = normalize(query), normalize(candidate)
        if not q or not c:
            return 0.0
        best = SequenceMatcher(None, q, c).ratio()
        for word in c.split():
            best = max(best, SequenceMatcher(None, q, word).ratio())
        return best


class Matcher:
    """Ranks candidates for a query with an Embedder when given, difflib otherwise."""

    def __init__(self, embedder: Embedder | None = None, cache_path: Path | None = None):
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

    def rank(self, query: str, candidates: Sequence[tuple[str, str]], k: int = 3, threshold: float = 0.0) -> list[tuple[str, float]]:
        """candidates are (key, text). Returns [(key, score)] best first, above threshold."""
        if self.embedder is None:
            scored = [(key, self.fallback.similarity(query, text)) for key, text in candidates]
        else:
            vectors = self._embed([query, *[t for _, t in candidates]])
            scored = [(key, cosine(vectors[0], v)) for (key, _), v in zip(candidates, vectors[1:])]
        best: dict[str, float] = {}
        for key, score in scored:
            if score >= threshold and score > best.get(key, -1):
                best[key] = score
        return sorted(best.items(), key=lambda kv: -kv[1])[:k]

    def _embed(self, texts: list[str]) -> list[list[float]]:
        missing = [t for t in texts if t not in self._cache]
        if missing:
            for t, v in zip(missing, self.embedder.embed(missing)):
                self._cache[t] = v
            if self.cache_path is not None:
                try:
                    self.cache_path.parent.mkdir(parents=True, exist_ok=True)
                    self.cache_path.write_text(json.dumps(self._cache), encoding="utf-8")
                except OSError:
                    pass
        return [self._cache[t] for t in texts]
