"""A long-lived World sees the outside change on the very next request (spec 12 §3).

sldb re-checks the document files once per operation, and an operation now starts at every
pron request (turn, eval, payload), not once when the World was opened. So a markdown
edited by hand (no sldb command), or a document written by another process, is visible to
the next eval of the same Session and to the next payload read of the same World.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from pron.session import Session
from pron.world.world import World
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"


@pytest.fixture()
def world(tmp_path: Path) -> World:
    return build_restaurant(tmp_path)


@pytest.fixture()
def session(world: World) -> Session:
    return Session(world, projection="all", speaker="jp", now=NOW)


def _edit_hand(path: Path, old: str, new: str) -> None:
    """Rewrite one field in the markdown itself: no sldb command anywhere."""
    text = path.read_text(encoding="utf-8")
    assert old in text, old
    path.write_text(text.replace(old, new), encoding="utf-8")


def _sldb_in_another_process(world: World, *args: str) -> None:
    """One sldb command in a separate Python: its own caches, like any other process."""
    import sldb

    src = Path(sldb.__file__).resolve().parents[1]
    base = str(world.store.pythonpath)
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(src), base]))
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "sldb",
            *args,
            "--store",
            str(world.root / ".sldb"),
            "--pythonpath",
            base,
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert run.returncode == 0, run.stdout + run.stderr


def test_a_hand_edit_is_visible_to_the_next_request(world: World, session: Session):
    doc = world.root / "clients" / "ana-perez.md"
    assert world.payload("Client", "client-ana-perez")["name"] == "Ana Pérez"
    r = session.eval('(show (doc "Client:client-ana-perez"))')
    assert r.outcome == "unico", r.text
    assert "Ana Pérez" in r.text

    _edit_hand(doc, "name: Ana Pérez", "name: Ana Editada")

    assert world.payload("Client", "client-ana-perez")["name"] == "Ana Editada"
    r = session.eval('(show (doc "Client:client-ana-perez"))')
    assert r.outcome == "unico", r.text
    assert "Ana Editada" in r.text


def test_a_write_from_another_process_is_visible_to_the_next_request(
    world: World, session: Session
):
    assert world.payload("Table", "table-3")["number"] == 3
    r = session.eval('(show (doc "Table:table-3"))')
    assert r.outcome == "unico", r.text
    assert "table 3" in r.text.lower()

    _sldb_in_another_process(
        world, "fields", "update", "docs/Table/table-3/number", "30"
    )

    assert world.payload("Table", "table-3")["number"] == 30
    r = session.eval('(show (doc "Table:table-3"))')
    assert r.outcome == "unico", r.text
    assert "table 30" in r.text.lower()
