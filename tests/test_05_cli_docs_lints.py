"""Steps 8–9 and the lints: the REPL over a session, `pron say`, the self-documentation, the lints, the atom migration."""

from __future__ import annotations

import io
import subprocess
from pathlib import Path

import pytest

from pron.cli.main import main as pron_main
from pron.cli.repl import run as repl
from pron.docs import synchronize_docs
from pron.lints import run_lints
from pron.migrate import migrate_atoms
from pron.world import World
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"
PRON_REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


def test_repl_keeps_the_dialogue_between_lines(world: World):
    out = io.StringIO()
    lines = "create a client named Ana Rojas, phone 9 5555 1234\nwhat reservations does Ana have?\n1\n:state\n:quit\n"
    repl(world, projection="all", speaker="jp", now=NOW, stdin=io.StringIO(lines), stdout=out)
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


def test_docs_are_generated_from_code_and_lints_pass(world: World):
    changed = synchronize_docs(world)
    assert any(c.endswith("cmd-pron-say") for c in changed) and any("surface-pron-session" in c for c in changed)
    assert synchronize_docs(world, check=True) == []
    doc = world.store.doc("CliCommandDoc", "cmd-pron-say")
    assert doc.payload["synopsis"].startswith("Say one sentence")
    assert "--trace" in doc.payload["arguments"]
    problems = run_lints(world)
    assert problems == [], problems


def test_v1_atoms_migrate_into_atom(world: World, tmp_path: Path):
    src = tmp_path / "v1atoms"
    src.mkdir()
    names = subprocess.run(["git", "ls-tree", "--name-only", "v1-code-and-kb", "knowledge/atoms/"], cwd=PRON_REPO, capture_output=True, text=True, check=True).stdout.split()
    picked = [n for n in names if n.endswith(".md")][:5]
    for n in picked:
        content = subprocess.run(["git", "show", f"v1-code-and-kb:{n}"], cwd=PRON_REPO, capture_output=True, text=True, check=True).stdout
        (src / Path(n).name).write_text(content, encoding="utf-8")
    report = migrate_atoms(world, src)
    assert report["migrated"] == 5 and report["failed"] == [], report
    atom = world.store.docs_of("Atom")[0]
    assert atom.payload["question"] in ("what", "why", "how", "how_not", "when", "where", "for_whom")
    assert not any(t.startswith("impl:") for t in atom.payload["tags"])
    assert "system:pron" in atom.payload["tags"] or not any(t.startswith("system:") for t in atom.payload["tags"])
