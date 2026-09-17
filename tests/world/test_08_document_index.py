"""The document index: what a runtime ranks a world's documents with, embedding only what
changed (spec 05, 10, 11 §2)."""

from __future__ import annotations

import json
import math
from pathlib import Path

from pron.world.matching.document_index import DocumentIndex
from pron.world.matching.matcher import Matcher


class CharBag:
    """A deterministic fake Embedder: normalized letter counts."""

    calls: list[list[str]] = []

    def id(self) -> str:
        return "charbag"

    def embed(self, texts):
        CharBag.calls.append(list(texts))
        out = []
        for t in texts:
            v = [0.0] * 26
            for c in t.lower():
                if "a" <= c <= "z":
                    v[ord(c) - 97] += 1
            n = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / n for x in v])
        return out


THREE = [
    ("a", "h1", "terrace table"),
    ("b", "h2", "indoor room"),
    ("c", "h3", "phone number"),
]


def _reads_back_without_embedding(path: Path) -> None:
    """A new instance reads the file back and needs no embedding."""
    again = DocumentIndex(Matcher(CharBag()), path)
    assert again.keys() == ["a", "b"]
    assert again.index([("a", "h1", "terrace table"), ("b", "h2-changed", "x")]) == {
        "embedded": 0,
        "reused": 2,
        "dropped": 0,
    }


def test_index_embeds_only_what_changed_and_persists(tmp_path: Path):
    CharBag.calls = []
    idx = DocumentIndex(Matcher(CharBag()), tmp_path / "docs.json")
    assert idx.index(THREE) == {"embedded": 3, "reused": 0, "dropped": 0}
    assert idx.index(THREE) == {"embedded": 0, "reused": 3, "dropped": 0}
    stats = idx.index(
        [("a", "h1", "terrace table"), ("b", "h2-changed", "indoor room, renovated")]
    )
    assert stats == {"embedded": 1, "reused": 1, "dropped": 1}
    assert CharBag.calls[-1] == ["indoor room, renovated"]
    saved = json.loads((tmp_path / "docs.json").read_text())
    assert saved["embedder"] == "charbag" and set(saved["entries"]) == {"a", "b"}
    _reads_back_without_embedding(tmp_path / "docs.json")


def test_rank_orders_by_similarity_and_respects_k_and_threshold(tmp_path: Path):
    idx = DocumentIndex(Matcher(CharBag()), tmp_path / "docs.json")
    idx.index(
        [
            ("terrace", "1", "terrace table"),
            ("indoor", "2", "indoor room"),
            ("phone", "3", "phone number"),
        ]
    )
    ranked = idx.rank("terrace tables")
    assert [k for k, _ in ranked][0] == "terrace"
    assert all(ranked[i][1] >= ranked[i + 1][1] for i in range(len(ranked) - 1))
    assert len(idx.rank("terrace tables", k=1)) == 1
    top = ranked[0][1]
    assert idx.rank("terrace tables", threshold=top) == [("terrace", top)]


def test_a_cache_from_another_embedder_is_ignored(tmp_path: Path):
    path = tmp_path / "docs.json"
    DocumentIndex(Matcher(CharBag()), path).index([("a", "1", "x")])
    other = DocumentIndex(Matcher(), path)  # difflib
    assert other.keys() == []


def test_without_embedder_the_index_ranks_with_difflib(tmp_path: Path):
    idx = DocumentIndex(Matcher(), tmp_path / "docs.json")
    stats = idx.index(
        [("terrace", "1", "terrace table"), ("phone", "2", "phone number")]
    )
    assert stats["embedded"] == 2
    saved = json.loads((tmp_path / "docs.json").read_text())
    assert (
        saved["embedder"] == "difflib"
        and "vector" not in saved["entries"]["terrace"]
        and saved["entries"]["terrace"]["text"] == "terrace table"
    )
    assert idx.rank("terrace")[0][0] == "terrace"


def test_document_index_exposes_its_vectors(tmp_path):
    from pron.world.matching.document_index import DocumentIndex
    from pron.world.matching.matcher import Matcher

    idx = DocumentIndex(Matcher(CharBag()), tmp_path / "docs.json")
    idx.index([("a", "h1", "alpha"), ("b", "h2", "beta")])
    vectors = idx.vectors()
    assert set(vectors) == {"a", "b"}
    assert all(isinstance(v, list) and v for v in vectors.values())
    bare = DocumentIndex(Matcher(None), tmp_path / "difflib.json")
    bare.index([("a", "h1", "alpha")])
    assert bare.vectors() == {}
