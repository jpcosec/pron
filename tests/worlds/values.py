"""A minimal world for PLAN 11 (value suggestions and the glossary), built from scratch.

Mirrors legos' clinic world's Fact model (topic/statement) so the same real texts the plan
measured there ("evento adverso", "evento_adversso") exercise the same paths here, plus an
Atom model with a `system` field to exercise PLAN 11 P3 (values already used in `system`/
`tags` enter the lexicon). The declaration is data/values.yaml and
data/values_models.py.txt; this module only builds it.
"""

from __future__ import annotations

from pathlib import Path

from pron.world.world import World
from worlds.build import (
    anchor_docs,
    create_docs,
    declared_docs,
    load_data,
    projection_doc,
    start_world,
)


def build_values(root: Path, refresh: bool = True) -> World:
    """Build the values world directly at root/ and return it opened."""
    pythonpath = root.parent
    models = ["Fact", "Atom"]
    world = start_world(
        pythonpath, root, "values_models", "values_models.py.txt", models
    )
    data = load_data("values.yaml")
    docs = [*declared_docs(data), projection_doc(data), *anchor_docs(data)]
    create_docs(world, root, docs)
    if refresh:
        world.refresh()
    return world
