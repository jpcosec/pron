"""Where predicates across the sldb door (spec 02): a predicate that does not parse is
an error response naming the predicate, never an empty result; and "" is a literal, so
`field = ""` finds a document whose field is present and empty."""

from __future__ import annotations

import pytest

from pron.session import Session
from pron.world import World
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("where"))


@pytest.fixture
def session(world: World) -> Session:
    return Session(world, projection="all", speaker="runtime", now=NOW)


def test_an_unparseable_predicate_is_an_error_not_an_empty_result(session: Session):
    r = session.eval('(show (all Reservation (where "bogus predicate")))')
    assert r.outcome == "error", r.text
    assert "bogus predicate" in r.text
    assert "no evaluator understands" in r.text


def test_an_empty_literal_finds_a_document_with_an_empty_field(session: Session):
    r = session.eval('(show (all Reservation (where "notes = \\"\\"")))')
    assert r.outcome == "unico", r.text
    assert r.text == session.eval("(show (all Reservation))").text
    assert r.text != "None."
