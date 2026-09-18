"""pron's own knowledge base derived from the repo (command and module docs, spec chapters,
implements edges), its README composed from the explanations, and the lints over it. The
tests follow each other in this file: the first one synchronizes the docs."""

from __future__ import annotations

from pathlib import Path

import cli.own_world as own_world
from pron.docs import synchronize_docs
from pron.lints import run_lints
from pron.session import Session
from pron.world.doc_id import DocId
from pron.world.world import World

NOW = "2026-09-09"
PRON_REPO = own_world.PRON_REPO
own = own_world.own  # tests/golden/test_16_golden_cli.py reuses both from this module


def test_own_knowledge_base_is_derived_from_the_repo(own: World):
    changed = synchronize_docs(own)
    assert any(c == "SpecDoc spec-02" for c in changed)
    assert any(c.endswith("cmd-pron-say") for c in changed) and any(
        "surface-pron-session" in c for c in changed
    )
    assert any(
        c.startswith(
            "RelationDoc implements--SurfaceDoc:surface-pron-sexpr-resolving-resolve--SpecDoc:spec-02"
        )
        for c in changed
    )
    assert synchronize_docs(own, check=True) == []
    # the spec chapter is tracked where it lives and its sections are addressable
    doc = own.store.doc(DocId.of("SpecDoc", "spec-02"))
    assert doc is not None and doc.path.endswith("source/spec/02-sustantivos.md")
    assert (
        own.store.doc(DocId.of("CliCommandDoc", "cmd-pron-say"))
        .payload["synopsis"]
        .startswith("Say one sentence")
    )
    assert run_lints(own) == [], run_lints(own)


def _surface_of_a_gone_module(own: World, gone: str) -> Path:
    path = own.root / "knowledge" / "surfaces" / f"{gone}.md"
    payload = dict(
        own.store.payload(DocId.of("SurfaceDoc", "surface-pron-session")), id=gone
    )
    own.store.create(DocId.of("SurfaceDoc", gone), dict(payload, surface="gone"), path)
    return path


def test_the_surface_of_a_module_that_no_longer_exists_is_pruned(own: World):
    """A SurfaceDoc left by a moved or deleted module is drift: `--check` reports it and
    writes nothing; `pron docs` untracks it and deletes the file it generated."""
    assert synchronize_docs(own, check=True) == []
    gone = "surface-pron-gone"
    path = _surface_of_a_gone_module(own, gone)
    assert synchronize_docs(own, check=True) == [f"SurfaceDoc {gone} (stale)"]
    assert path.exists() and own.store.doc(DocId.of("SurfaceDoc", gone)) is not None
    assert f"SurfaceDoc {gone} (stale)" in synchronize_docs(own)
    assert not path.exists() and own.store.doc(DocId.of("SurfaceDoc", gone)) is None
    assert synchronize_docs(own, check=True) == []


def _is_composed(text: str) -> None:
    assert text.startswith("# pron\n\n## ¿Qué es pron?\n\n")
    assert (
        "- knowledge/explanations/" not in text
    )  # the paths are the declaration, not the README


def _edit_an_explanation(own: World) -> None:
    """The drift: edit one explanation where it lives."""
    path = own.root / "knowledge" / "explanations" / "what-is-pron.md"
    original = path.read_text(encoding="utf-8")
    path.write_text(
        original.replace(
            "el cordel anudado con que se llevaba el registro",
            "el cordel anudado del registro",
        ),
        encoding="utf-8",
    )


def test_the_readme_is_composed_from_the_explanations(own: World):
    """README.md is generated from the ReadmeDoc's parts: an edited explanation is drift,
    and `pron docs` regenerates the README with the new text."""
    assert synchronize_docs(own, check=True) == []
    readme = own.root / "README.md"
    _is_composed(readme.read_text(encoding="utf-8"))
    _edit_an_explanation(own)
    assert "README.md out of date" in synchronize_docs(own, check=True)
    assert "el cordel anudado del registro" not in readme.read_text(encoding="utf-8")

    assert synchronize_docs(own)  # re-tracks the explanation and regenerates the README
    assert "el cordel anudado del registro" in readme.read_text(encoding="utf-8")
    assert synchronize_docs(own, check=True) == []


def _anchor(own: World, symbol: str, forms: list[str], ref: str, motive: str) -> None:
    own.store.create(
        DocId.of("AnchorDoc", f"anchor-{symbol}"),
        {"symbol": symbol, "forms": forms, "ref": ref, "steps": [], "motive": motive},
        own.root / "knowledge" / "anchors" / f"{symbol}.md",
    )


def test_a_question_over_the_own_knowledge_base(own: World):
    _anchor(
        own, "module", ["module", "modules"], "model:SurfaceDoc", "a module of pron"
    )
    _anchor(
        own,
        "chapter",
        ["chapter", "chapters"],
        "model:SpecDoc",
        "a chapter of the spec",
    )
    _anchor(
        own,
        "implements",
        ["implements", "implement", "implemented by"],
        "relation:implements",
        "which chapter a module carries out",
    )
    own.refresh()
    s = Session(own, now=NOW)
    r = s.turn("what does the module resolve implement?")
    assert r.outcome == "unico", r.text + " / " + " | ".join(r.trace)
    assert "Sustantivos" in r.text
