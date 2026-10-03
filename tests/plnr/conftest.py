"""The restaurant world plus the rules that world declares, and the session that holds it.

The rules are documents (TheoremDoc), read from the world at the moment a goal is searched,
so this file only writes them where the world keeps them: it is a declaration, not code.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from pron.session import Session
from pron.world.doc_id import DocId
from pron.world.world import World
from worlds.build import DATA
from worlds.restaurant import build_restaurant

RULES = DATA / "goal_theorems.yaml"


def _declare(world: World, root: Path) -> None:
    """The world's rules, tracked under knowledge/theorems/ like any other declaration."""
    for rule in yaml.safe_load(RULES.read_text(encoding="utf-8")):
        name = f"theorem-{rule['name']}"
        world.store.create(
            DocId.of("TheoremDoc", name),
            {**rule, "description": rule["motive"]},
            root / "knowledge" / "theorems" / f"{rule['name']}.md",
        )


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    base = tmp_path_factory.mktemp("plnr")
    world = build_restaurant(base)
    _declare(world, base / "world")
    world.refresh()
    return world


@pytest.fixture(scope="module")
def session(world: World) -> Session:
    return Session(world, projection="all", speaker="jp", now="2026-09-09")
