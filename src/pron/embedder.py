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
from typing import Iterable, Protocol, Sequence


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


class DocumentIndex:
    """Documents of a world ranked by similarity to a query (spec 05 §Calce aproximado, 11 §2):
    the vectors live in one derived file outside git, keyed by the document's content hash,
    so a re-index embeds only what changed. With a Matcher that has no Embedder there are no
    vectors: the texts are kept and ranked with difflib, and the file says which it is.
    pron never decides what to do with a rank; it offers it."""

    def __init__(self, matcher: Matcher, cache_path: Path):
        self.matcher = matcher
        self.cache_path = Path(cache_path)
        self._entries: dict[str, dict] = {}
        self._load()

    @property
    def embedder_id(self) -> str:
        return self.matcher.id()

    def _load(self) -> None:
        self._entries = {}
        if not self.cache_path.exists():
            return
        try:
            data = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if data.get("embedder") == self.embedder_id:
            self._entries = data.get("entries", {}) or {}

    def _save(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps({"embedder": self.embedder_id, "entries": self._entries}), encoding="utf-8")

    def index(self, items: Iterable[tuple[str, str, str]]) -> dict[str, int]:
        """items are (key, content_hash, text). Embeds the keys whose hash is new or changed,
        keeps the rest, drops the keys that did not come. Returns {embedded, reused, dropped}."""
        items = list(items)
        keep: dict[str, dict] = {}
        todo: list[tuple[str, str, str]] = []
        reused = 0
        for key, h, text in items:
            prev = self._entries.get(key)
            if prev is not None and prev.get("hash") == h:
                keep[key] = prev
                reused += 1
            else:
                todo.append((key, h, text))
        if self.matcher.embedder is None:
            for key, h, text in todo:
                keep[key] = {"hash": h, "text": text}
        elif todo:
            vectors = self.matcher.embedder.embed([t for _, _, t in todo])
            for (key, h, _), v in zip(todo, vectors):
                keep[key] = {"hash": h, "vector": [float(x) for x in v]}
        dropped = len(set(self._entries) - set(keep))
        self._entries = keep
        self._save()
        return {"embedded": len(todo), "reused": reused, "dropped": dropped}

    def keys(self) -> list[str]:
        return sorted(self._entries)

    def vectors(self) -> dict[str, list[float]]:
        """key -> vector for every indexed document that has one (none without an Embedder).
        For consumers that project or compare the vectors themselves, e.g. a 2D map of a world."""
        return {k: list(e["vector"]) for k, e in self._entries.items() if "vector" in e}

    def rank(self, query: str, k: int | None = None, threshold: float = 0.0) -> list[tuple[str, float]]:
        """[(key, score)] best first, above threshold; cosine over the vectors, or difflib
        over the kept texts when there is no Embedder."""
        if not self._entries:
            return []
        if self.matcher.embedder is None:
            scored = [(key, self.matcher.fallback.similarity(query, e.get("text", ""))) for key, e in self._entries.items()]
        else:
            q = self.matcher.embedder.embed([query])[0]
            scored = [(key, cosine(q, e["vector"])) for key, e in self._entries.items() if "vector" in e]
        out = sorted(((key, s) for key, s in scored if s >= threshold), key=lambda kv: (-kv[1], kv[0]))
        return out[:k] if k is not None else out
