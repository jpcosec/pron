"""Step 1: an alias a world declares is a form, whichever way it was written."""

from __future__ import annotations

from pron.sexpr.forms.refs import parse
from pron.world.world import World

OLD_BOOK_STEPS = [
    {"do": "create", "model": "Reservation", "fields": "$literals"},
    {
        "do": "assert",
        "relation": "booked_by",
        "source": "$created",
        "target": "$referent:Client",
    },
    {
        "do": "assert",
        "relation": "assigned_to",
        "source": "$created",
        "target": "$object:Table",
    },
]


def test_a_composed_alias_is_a_form_that_round_trips(world: World):
    d = world.store.doc("AnchorDoc", "anchor-book")
    assert d.payload["ref"].startswith("(move (create Reservation)")
    assert parse(d.payload["ref"]).steps[1] == {
        "do": "assert",
        "relation": "booked_by",
        "source": "$created",
        "target": "$referent:Client",
    }
    assert "book her" in d.payload["forms"]


def test_an_alias_written_the_old_way_is_read_as_the_same_form():
    old = parse("compose", OLD_BOOK_STEPS)
    new = parse(
        '(move (create Reservation) (assert booked_by (created) (it "her" Client)) (assert assigned_to (created) (a Table)))'
    )
    assert old.steps == new.steps
    assert (
        parse("action:change Reservation.status=confirmed").text
        == '(change (it "it" Reservation) status "confirmed")'
    )
    assert parse("predicate:Table:capacity >= N").where == "capacity >= N"
