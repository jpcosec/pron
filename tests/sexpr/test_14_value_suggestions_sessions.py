"""PLAN 11 P2: an unknown word alone, said in a session, is ranked against the values that
already exist and offers the sentence that resolves (spec 05 §Calce aproximado)."""

from __future__ import annotations

from pron.session import Session
from worlds.values import build_values

NOW = "2026-09-14"


# -- P2: an unknown word alone, ranked against existing values, offers the resolving sentence


def test_c_a_bare_unknown_word_offers_the_resolving_sentence():
    world = build_values(_module_tmp("c"))
    session = Session(world, projection="all", speaker="probe", now=NOW, read_only=True)
    r = session.turn("evento adverso")
    assert r.outcome == "missing", r.text
    values = r.record["missing"].get("values") or []
    sentences = [v["sentence"] for v in values]
    assert "the fact about evento_adverso" in sentences, (r.text, sentences)
    assert "the fact about evento_adverso" in r.text, r.text


def test_g_an_injected_embedder_finds_what_difflib_cannot():
    world = build_values(_module_tmp("g"))
    session = Session(
        world,
        projection="all",
        speaker="probe",
        now=NOW,
        read_only=True,
        embedder=_FakeEmbedder(),
    )
    r = session.turn("adverse event")
    assert r.outcome == "missing", r.text
    values = r.record["missing"].get("values") or []
    sentences = [v["sentence"] for v in values]
    assert "the fact about evento_adverso" in sentences, (r.text, sentences)
    assert any("fake-v1" in line for line in r.trace), r.trace


class _FakeEmbedder:
    _VECTORS = {
        "adverse": [1.0, 0.0, 0.0, 0.0],
        "evento_adverso": [0.97, 0.2, 0.0, 0.0],
        "medinfo": [0.0, 1.0, 0.0, 0.0],
        "seguimiento": [0.0, 0.0, 1.0, 0.0],
    }

    def id(self) -> str:
        return "fake-v1"

    def embed(self, texts):
        return [self._VECTORS.get(t, [0.0, 0.0, 0.0, 1.0]) for t in texts]


def _module_tmp(tag: str):
    import tempfile
    from pathlib import Path

    return Path(tempfile.mkdtemp(prefix=f"pron-values-{tag}-"))
