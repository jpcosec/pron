"""Steps 8–9 and the lints on a declared world: the REPL over a session, `pron say`,
`pron lexicon`, the lints."""

from __future__ import annotations

import io

import pytest

from pron.cli.main import main as pron_main
from pron.cli.repl import run as repl
from pron.lints import run_lints
from pron.world.world import World
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


def test_repl_keeps_the_dialogue_between_lines(world: World):
    out = io.StringIO()
    lines = "create a client named Ana Rojas, phone 9 5555 1234\nwhat reservations does Ana have?\n1\n:state\n:quit\n"
    from pron.session import Session

    repl(
        Session(world, projection="all", speaker="jp", now=NOW),
        world.root.name,
        "all",
        stdin=io.StringIO(lines),
        stdout=out,
    )
    text = out.getvalue()
    assert "Created client Ana Rojas" in text
    assert "Which one?" in text
    assert "state: libre" in text


def test_say_prints_answer_and_trace(world: World, capsys):
    assert (
        pron_main(
            [
                "say",
                "the large tables",
                "--world",
                str(world.root),
                "--pythonpath",
                world.store.pythonpath,
                "--trace",
                "--now",
                NOW,
            ]
        )
        == 0
    )
    out = capsys.readouterr().out
    assert "table 12" in out and "find 'st.{Table+}'" in out


def test_lexicon_command_lists_words(world: World, capsys):
    assert (
        pron_main(
            [
                "lexicon",
                "Reservation",
                "--world",
                str(world.root),
                "--pythonpath",
                world.store.pythonpath,
            ]
        )
        == 0
    )
    out = capsys.readouterr().out
    assert "booked_by" in out and "party size" in out


def test_lints_pass_on_a_declared_world(world: World):
    assert run_lints(world) == []
