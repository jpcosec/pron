"""What the review of 2026-09-08 found missing against the spec, on what a projection allows:
permissions inside a compose alias (05), the projection cutting the lexicon (01), and a model
identifier known split into words."""

from __future__ import annotations


from pron.world.lexicon import Lexicon
from pron.session import Session
from pron.world.world import World

NOW = "2026-09-09"


def test_a_compose_alias_respects_the_relation_permissions(world: World):
    proj = dict(
        world.projection("all"),
        name="creator",
        actions=["create"],
        relations=[
            {"name": "booked_by", "mode": "read"},
            {"name": "assigned_to", "mode": "read"},
            {"name": "transitions_to", "mode": "read"},
        ],
    )
    world.store.create(
        "ProjectionDoc",
        "projection-creator",
        proj,
        world.root / "knowledge" / "projections" / "creator.md",
    )
    s = Session(world, projection="creator", speaker="zoe", now=NOW)
    assert s.turn("the client Luis Soto").outcome == "unico"
    r = s.turn("book him a table on the terrace for 2 people on Saturday at 8pm")
    assert r.outcome == "missing" and "not assert" in r.text, r.text
    assert world.store.doc("Reservation", "reservation-2026-09-12-luis-soto") is None


def test_the_projection_cuts_aliases_whose_target_is_outside_it(world: World):
    proj = dict(
        world.projection("all"),
        name="clients",
        models=["Client"],
        relations=[],
        actions=[],
    )
    world.store.create(
        "ProjectionDoc",
        "projection-clients",
        proj,
        world.root / "knowledge" / "projections" / "clients.md",
    )
    s = Session(world, projection="clients", now=NOW)
    r = s.turn("the tables")
    assert r.outcome == "missing" and "don't have" in r.text, r.text
    assert s.turn("the clients").outcome == "unico"


def test_a_model_identifier_is_also_known_split_into_words(world: World):
    lex = Lexicon(
        world,
        {"models": ["RelationTypeDoc"], "relations": [], "actions": [], "aliases": []},
    )
    assert [w.ref for w in lex.lookup("relation type doc")] == [
        "(model RelationTypeDoc)"
    ]
