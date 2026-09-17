"""The restaurant world of source/spec/09a, built from scratch in a directory.

Nothing here is pron: it is what a world's owner declares. pron has to work on it
before its own knowledge base matters. The declaration is data/restaurant.yaml and
data/restaurant_models.py.txt; this module only builds it, in the order it always did.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pron.world.world import World
from worlds.build import (
    Doc,
    anchor_docs,
    create_docs,
    declared_docs,
    load_data,
    projection_doc,
    relation_doc,
    relation_type_docs,
    start_world,
)

MODELS = ["Client", "Table", "Reservation", "State"]


def _state_docs(data: dict[str, Any]) -> list[Doc]:
    return [
        (
            "State",
            f"state-reservation-{n}",
            {
                "machine": "Reservation.status",
                "name": n,
                "description": f"The reservation is {n}.",
            },
            Path("states") / f"{n}.md",
        )
        for n in data["states"]
    ]


def _table_docs(data: dict[str, Any]) -> list[Doc]:
    return [
        ("Table", f"table-{t['number']}", t, Path("tables") / f"{t['number']}.md")
        for t in data["tables"]
    ]


def _relation_docs(data: dict[str, Any]) -> list[Doc]:
    state = "State:state-reservation-{}".format
    transitions = [
        relation_doc(
            "transitions_to",
            state(src),
            state(tgt),
            f"{src} transitions_to {tgt}",
            cond,
        )
        for src, tgt, cond in data["transitions"]
    ]
    edges = [
        relation_doc(rel, src, tgt, f"{rel}--{src}--{tgt}")
        for rel, src, tgt in data["relations"]
    ]
    return transitions + edges


def _documents(data: dict[str, Any]) -> list[Doc]:
    return [
        *_state_docs(data),
        *_table_docs(data),
        *declared_docs(data),
        *relation_type_docs(data),
        *_relation_docs(data),
        projection_doc(data),
        *anchor_docs(data),
    ]


def build_restaurant(base: Path, refresh: bool = True) -> World:
    """Build the whole world under base/ and return it opened."""
    root = base / "world"
    world = start_world(base, root, "restaurant", "restaurant_models.py.txt", MODELS)
    create_docs(world, root, _documents(load_data("restaurant.yaml")))
    if refresh:
        world.refresh()
    return world
