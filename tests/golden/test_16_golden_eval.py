"""Characterization (golden master, spec 13): Session.eval on forms for every write verb, an
assertion, reads, a composed move, undo, and the error paths of forms that cannot be read or
evaluated, recorded whole as they are today."""

from __future__ import annotations

from golden.run import LUIS, play, restaurant

ANCHOR = '(doc "AnchorDoc:anchor-client")'
WALK_IN = '(doc "Reservation:walk-in")'

FORMS = [
    '(create Client (name "Eva Diaz") (phone "9 4444 0000"))',
    f'(change (doc "{LUIS}") party_size 3)',
    f'(add {ANCHOR} forms "patron")',
    f'(remove {ANCHOR} forms "patron")',
    f'(change {ANCHOR} forms (list "client" "client" "" "clients"))',
    f"(clean {ANCHOR} forms)",
    f"(remove {ANCHOR} forms)",
    '(forget (doc "Table:table-5"))',
    '(create Reservation (as "walk-in") (date "2026-09-12") (time "13:00") (party_size 2))',
    f'(assert assigned_to {WALK_IN} (doc "Table:table-20"))',
    '(show (find Table (where "capacity >= 6")))',
    f'(targets assigned_to (doc "{LUIS}"))',
    '(show (the Table (where "zone = \\"terrace\\"")))',
    '(move (create Client (as "x1") (name "Nueva Una") (phone "111"))'
    ' (create Reservation (as "x2") (date "2026-09-10") (time "21:00") (party_size 3))'
    ' (assert booked_by (doc "Reservation:x2") (doc "Client:x1")))',
    "(undo)",
    "(show",
    "(explode)",
    "(all Table)",
]


def test_eval_forms(tmp_path, snapshot):
    _, session = restaurant(tmp_path, projection="keeper")
    steps = [("eval", forms) for forms in FORMS]
    assert play(session, steps, tmp_path) == snapshot
