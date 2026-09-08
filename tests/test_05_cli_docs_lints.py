"""Steps 8–9 and the lints: the REPL over a session, `pron say`, pron's own knowledge base derived
from the repo (command and module docs, spec chapters, implements edges), the lints."""

from __future__ import annotations

import io
import shutil
from pathlib import Path

import pytest

from pron.cli.main import main as pron_main
from pron.cli.repl import run as repl
from pron.docs import synchronize_docs
from pron.lints import run_lints
from pron.session import Session
from pron.world import World, init_world
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"
PRON_REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


def test_repl_keeps_the_dialogue_between_lines(world: World):
    out = io.StringIO()
    lines = "create a client named Ana Rojas, phone 9 5555 1234\nwhat reservations does Ana have?\n1\n:state\n:quit\n"
    from pron.session import Session
    repl(Session(world, projection="all", speaker="jp", now=NOW), world.root.name, "all", stdin=io.StringIO(lines), stdout=out)
    text = out.getvalue()
    assert "Created client Ana Rojas" in text
    assert "Which one?" in text
    assert "state: libre" in text


def test_say_prints_answer_and_trace(world: World, capsys):
    assert pron_main(["say", "the large tables", "--world", str(world.root), "--pythonpath", world.store.pythonpath, "--trace", "--now", NOW]) == 0
    out = capsys.readouterr().out
    assert "table 12" in out and "find 'st.{Table+}'" in out


def test_lexicon_command_lists_words(world: World, capsys):
    assert pron_main(["lexicon", "Reservation", "--world", str(world.root), "--pythonpath", world.store.pythonpath]) == 0
    out = capsys.readouterr().out
    assert "booked_by" in out and "party size" in out


def test_lints_pass_on_a_declared_world(world: World):
    assert run_lints(world) == []


@pytest.fixture(scope="module")
def own(tmp_path_factory) -> World:
    """A copy of pron's own knowledge base: the spec chapters, built from scratch."""
    root = tmp_path_factory.mktemp("pron-own") / "world"
    shutil.copytree(PRON_REPO / "source", root / "source")
    from sldb.cli import main as sldb_main
    assert sldb_main(["stores", "init", "--path", str(root)]) == 0
    init_world(root, str(PRON_REPO), with_knowledge=True)
    return World(root, str(PRON_REPO))


def test_own_knowledge_base_is_derived_from_the_repo(own: World):
    changed = synchronize_docs(own)
    assert any(c == "SpecDoc spec-02" for c in changed)
    assert any(c.endswith("cmd-pron-say") for c in changed) and any("surface-pron-session" in c for c in changed)
    assert any(c.startswith("RelationDoc implements--SurfaceDoc:surface-pron-resolve--SpecDoc:spec-02") for c in changed)
    assert synchronize_docs(own, check=True) == []
    # the spec chapter is tracked where it lives and its sections are addressable
    doc = own.store.doc("SpecDoc", "spec-02")
    assert doc is not None and doc.path.endswith("source/spec/02-sustantivos.md")
    assert own.store.doc("CliCommandDoc", "cmd-pron-say").payload["synopsis"].startswith("Say one sentence")
    assert run_lints(own) == [], run_lints(own)


def test_a_question_over_the_own_knowledge_base(own: World):
    own.store.create("AnchorDoc", "anchor-module", {"symbol": "module", "forms": ["module", "modules"], "ref": "model:SurfaceDoc", "steps": [], "motive": "a module of pron"},
                     own.root / "knowledge" / "anchors" / "module.md")
    own.store.create("AnchorDoc", "anchor-chapter", {"symbol": "chapter", "forms": ["chapter", "chapters"], "ref": "model:SpecDoc", "steps": [], "motive": "a chapter of the spec"},
                     own.root / "knowledge" / "anchors" / "chapter.md")
    own.store.create("AnchorDoc", "anchor-implements", {"symbol": "implements", "forms": ["implements", "implement", "implemented by"], "ref": "relation:implements", "steps": [], "motive": "which chapter a module carries out"},
                     own.root / "knowledge" / "anchors" / "implements.md")
    own.refresh()
    s = Session(own, now=NOW)
    r = s.turn("what does the module resolve implement?")
    assert r.outcome == "unico", r.text + " / " + " | ".join(r.trace)
    assert "Sustantivos" in r.text
