"""The ladder of mutability declared per projection (spec 14 §5): `mutability` on the
ProjectionDoc, 1 when absent, 0 for a read-only session."""

from __future__ import annotations

import pytest
from conftest import add_projection, session
from pydantic import ValidationError

from pron.models.projection import ProjectionDoc
from pron.world.mutability import form_models, level_of
from pron.world.world import World


def test_the_field_defaults_to_content():
    assert ProjectionDoc(name="p").mutability == 1
    assert ProjectionDoc(name="p", mutability="").mutability == 1
    assert ProjectionDoc(name="p", mutability=3).mutability == 3
    with pytest.raises(ValidationError):
        ProjectionDoc(name="p", mutability=4)


def test_the_level_of_a_projection():
    assert level_of({}) == 1 and level_of({"mutability": 0}) == 0
    assert form_models(1) == frozenset()
    assert form_models(2) == {"RelationTypeDoc"}


def test_sessions_read_their_level(world: World):
    add_projection(world, "reader", mutability=0)
    assert level_of(session(world).projection) == 1
    assert level_of(session(world, "rules").projection) == 2
    assert level_of(session(world, "reader").projection) == 0
    assert level_of(session(world, "rules", read_only=True).projection) == 0
