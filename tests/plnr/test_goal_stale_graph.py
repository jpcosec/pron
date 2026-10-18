"""Con el grafo viejo (spec 03): la meta nota que el mundo se movió y la respuesta sale igual.

Un mundo real escribe fuera de pron a cada rato. Desde acd3d2b las aristas se leen por una
sola puerta, el índice de aristas de sldb (que ya incluye los RelationDoc autorados); no hay
otra puerta para cuando el índice queda atrás: eso se arregla con un rebuild, no leyendo de
otro lado. Lo que se prueba es que pron nota el grafo viejo, que la meta sigue contestando y
que la traza dice qué puerta contestó.
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
    # Algo escribe fuera de pron sin mantener las aristas al día. Toda escritura por el store de
    # sldb sincroniza su shard de aristas, así que un create solo ya no deja el grafo viejo: lo
    # que lo deja así es una herramienta que escribe el documento y no su shard. Eso es lo que
    # sldb llama stale (un documento trackeado sin shard al día), y es lo que se simula acá.
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
    shard = Path(world.root) / ".sldb" / "runtime" / "edges" / "TheoremDoc" / "theorem-touched.yaml"
    shard.unlink()
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
    queries = r.record["queries"]
    assert any(q.startswith("sldb edges_to(Table:table-3, assigned_to)") for q in queries), queries
