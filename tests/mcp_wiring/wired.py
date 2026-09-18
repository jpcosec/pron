"""Helpers of the wiring tests (spec 14 §4, §5): the restaurant with projections at each
level of the ladder, and an app over it with one of them. Each world gets its own name, so
the models a test generates never meet another test's in `sys.modules`."""

from __future__ import annotations

from itertools import count
from pathlib import Path

from pron.mcp.app import McpApp
from pron.world.doc_id import DocId
from pron.world.world import World
from worlds.build import load_data
from worlds.restaurant import build_restaurant

NAMES = count()
LUIS = "Reservation:reservation-2026-09-11-luis-soto"
DISH = [
    {"name": "title", "type": "str", "description": "The dish as the menu names it."},
    {"name": "price", "type": "int", "description": "Price in pesos."},
    {"name": "course", "type": "Literal['main', 'dessert']", "description": "Course."},
    {"name": "tags", "type": "list[str]", "description": "Tags.", "required": False},
]


def add_projection(world: World, name: str, **fields) -> None:
    payload = dict(load_data("restaurant.yaml")["projection"], name=name, **fields)
    path = world.root / "knowledge" / "projections" / f"{name}.md"
    world.store.create(DocId.of("ProjectionDoc", f"projection-{name}"), payload, path)
    world.refresh()


def restaurant(tmp: Path) -> World:
    """The restaurant with `reader` (0), `all` (1), `rules` (2) and `models` (3, every model)."""
    world = build_restaurant(tmp)
    add_projection(world, "reader", mutability=0)
    add_projection(world, "rules", mutability=2)
    add_projection(world, "models", mutability=3, models=[])
    return world


def wire(world: World, projection: str = "all", **kw) -> tuple[McpApp, str]:
    """An app over the world under a fresh name, and that name."""
    name = f"w{next(NAMES)}"
    app = McpApp.open(
        [f"{name}={world.root}"], world.store.pythonpath, projection, **kw
    )
    return app, name
