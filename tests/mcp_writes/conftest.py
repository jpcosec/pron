"""The restaurant world for the write tools (spec 14 §4, §5): its own projection `all`
(level 1, no `mutability` line) and a projection `rules` at level 2, the same otherwise."""

from __future__ import annotations

import pytest

from pron.session import Session
from pron.world.doc_id import DocId
from pron.world.world import World
from worlds.build import load_data
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"
LUIS = "Reservation:reservation-2026-09-11-luis-soto"


def add_projection(world: World, name: str, **fields) -> None:
    payload = dict(load_data("restaurant.yaml")["projection"], name=name, **fields)
    path = world.root / "knowledge" / "projections" / f"{name}.md"
    world.store.create(DocId.of("ProjectionDoc", f"projection-{name}"), payload, path)
    world.refresh()


@pytest.fixture
def world(tmp_path) -> World:
    w = build_restaurant(tmp_path)
    add_projection(w, "rules", mutability=2)
    return w


def session(world: World, projection: str = "all", **kw) -> Session:
    return Session(world, projection=projection, speaker="mcp", now=NOW, **kw)
