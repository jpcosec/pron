"""Con el grafo viejo (spec 03): las aristas autoradas se leen de los RelationDoc en sldb.

Un mundo real escribe fuera de pron a cada rato. La meta no puede depender de que el grafo
esté fresco: lee las aristas de los documentos, la respuesta sale igual y la traza dice qué
puerta contestó.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pron.session import Session
from pron.world.doc_id import DocId
from pron.world.world import World
from worlds.restaurant import build_restaurant


@pytest.fixture(scope="module")
def stale(tmp_path_factory) -> World:
    world = build_restaurant(tmp_path_factory.mktemp("stale"))
    # algo escribe fuera de pron, sin refresh: el grafo deja de cubrir el mundo
    world.store.create(
        DocId.of("TheoremDoc", "theorem-touched"),
        {
            "name": "touched",
            "kind": "consequent",
            "pattern": "(same ?x ?x)",
            "body": "",
            "motive": "una regla que ensucia el hash del mundo",
            "description": "una regla que ensucia el hash del mundo",
        },
        Path(world.root) / "knowledge" / "theorems" / "touched.md",
    )
    return world


def test_a_move_starts_by_noticing_the_world_moved(stale: World):
    assert stale.graph_is_fresh() is False


def test_the_edges_are_still_read_and_the_answer_comes_out(stale: World):
    session = Session(stale, projection="all", speaker="jp", now="2026-09-09")
    r = session.eval(
        "(goal (find all ?r (goal (edge assigned_to ?r Table:table-3))))"
    )
    assert r.outcome == "unico", r.text
    assert r.text == "?r = (Reservation:reservation-2026-09-11-luis-soto)", r.text


def test_the_trace_says_sldb_answered(stale: World):
    session = Session(stale, projection="all", speaker="jp", now="2026-09-09")
    r = session.eval("(goal (edge assigned_to ?r Table:table-3))")
    assert any("not fresh" in q for q in r.record["queries"]), r.record["queries"]
