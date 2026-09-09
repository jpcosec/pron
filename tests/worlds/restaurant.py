"""The restaurant world of source/spec/09a, built from scratch in a directory.

Nothing here is pron: it is what a world's owner declares. pron has to work on it
before its own knowledge base matters.
"""

from __future__ import annotations

import sys
from pathlib import Path

from sldb.cli import main as sldb_main

from pron.world import World, init_world

MODELS = '''from typing import Literal
from pydantic import Field
from sldb import StructuredNLDoc


class Client(StructuredNLDoc):
    """A person who books. Identified by name; the phone number is mandatory."""
    __family__ = "restaurant"
    __semantics__ = {"type": ["restaurant", "client"]}
    __template__ = """---
name: ⸢rev•name⸥
phone: ⸢rev•phone⸥
---

# ⸢render•name⸥

## Notes

⸢rev•notes⸥
""".strip()

    name: str = Field(description="Full name as the client gives it.")
    phone: str = Field(description="Contact phone number, in whatever format the client uses.")
    notes: str = Field(default="", description="Free-form remarks about the client: allergies, preferences, incidents.")


class Table(StructuredNLDoc):
    """A physical table in the venue. Capacity is fixed; the zone is one of two."""
    __family__ = "restaurant"
    __semantics__ = {"type": ["restaurant", "table"]}
    __template__ = """---
number: ⸢rev•number⸥
capacity: ⸢rev•capacity⸥
zone: ⸢rev•zone⸥
---

# Table ⸢render•number⸥
""".strip()

    number: int = Field(description="Table number as marked on the floor.")
    capacity: int = Field(description="Maximum number of people seated comfortably.")
    zone: Literal["terrace", "indoor"] = Field(description="Where the table is: the open-air terrace or the indoor room.")


class Reservation(StructuredNLDoc):
    """A booking for a date and time. Who it is for and which table it gets are relations, not fields."""
    __family__ = "restaurant"
    __semantics__ = {"type": ["restaurant", "reservation"]}
    __template__ = """---
date: ⸢rev•date⸥
time: ⸢rev•time⸥
party_size: ⸢rev•party_size⸥
status: ⸢rev•status⸥
---

# Reservation ⸢render•date⸥ ⸢render•time⸥

## Notes

⸢rev•notes⸥
""".strip()

    date: str = Field(description="Reservation date in ISO form, YYYY-MM-DD.")
    time: str = Field(description="Arrival time, HH:MM in 24-hour form.")
    party_size: int = Field(description="Number of people coming.")
    status: Literal["pending", "confirmed", "seated", "cancelled"] = Field(
        default="pending",
        description="Where the reservation stands. Changes only through the transitions declared between states.",
    )
    notes: str = Field(default="", description="Free-form remarks: occasion, special requests.")


class State(StructuredNLDoc):
    """One possible state of a status field. Exists as a document so that transitions are edges between states."""
    __family__ = "restaurant"
    __semantics__ = {"type": ["restaurant", "state"]}
    __template__ = """---
machine: ⸢rev•machine⸥
name: ⸢rev•name⸥
---

# ⸢render•machine⸥ · ⸢render•name⸥

⸢rev•description⸥
""".strip()

    machine: str = Field(description="Which field of which model this machine governs, as Model.field; for example Reservation.status.")
    name: str = Field(description="The field value this document stands for.")
    description: str = Field(description="What being in this state means.")
'''

TABLES = [
    (3, 4, "indoor"),
    (5, 4, "indoor"),
    (12, 6, "terrace"),
    (14, 8, "terrace"),
    (20, 2, "terrace"),
]
STATES = ["pending", "confirmed", "seated", "cancelled"]
TRANSITIONS = [
    ("pending", "confirmed", "party_size <= 8"),
    ("pending", "cancelled", ""),
    ("confirmed", "seated", ""),
    ("confirmed", "cancelled", ""),
]

RELATION_TYPES = [
    {
        "name": "booked_by",
        "cardinality": "many_to_one",
        "axis": "WHAT",
        "source_types": ["Reservation"],
        "target_types": ["Client"],
        "condition": "",
        "description": "Who a reservation belongs to. Every reservation is booked by exactly one client.",
    },
    {
        "name": "assigned_to",
        "cardinality": "many_to_one",
        "axis": "WHERE",
        "source_types": ["Reservation"],
        "target_types": ["Table"],
        "condition": "capacity >= {party_size}",
        "description": "Which table a reservation gets. The table must seat everyone.",
    },
    {
        "name": "transitions_to",
        "cardinality": "many_to_many",
        "axis": "WHEN",
        "source_types": ["State"],
        "target_types": ["State"],
        "condition": "",
        "description": "An allowed move between two states of a status field.",
    },
]

PROJECTION = {
    "name": "all",
    "stores": ["local"],
    "models": ["Client", "Table", "Reservation", "State"],
    "relations": [
        {"name": "booked_by", "mode": "read and assert"},
        {"name": "assigned_to", "mode": "read and assert"},
        {"name": "transitions_to", "mode": "read"},
    ],
    "actions": [
        "create",
        "change",
        "add",
        "clean",
        "remove",
        "forget",
        "refresh",
        "undo",
    ],
    "aliases": ["all"],
    "naming": {
        "Client": "client-{name}",
        "Reservation": "reservation-{date}-{booked_by.name}",
        "RelationDoc": "{relation_type}--{source_id}--{target_id}",
    },
    "display": {
        "Client": "{name}",
        "Table": "table {number}",
        "Reservation": "{date} {time}, {party_size} people, table {assigned_to.number}, {status}",
    },
    "key": {"Table": "number"},
    "matching": {"neighbors": 3, "threshold": 0.55},
    "description": "Everything, read and assert, for the tests.",
}

ALIASES = [
    ("client", ["client", "clients"], "model:Client", "a person who books", []),
    ("table", ["table", "tables"], "model:Table", "a table in the venue", []),
    (
        "reservation",
        ["reservation", "reservations", "booking", "bookings"],
        "model:Reservation",
        "a booking for a date and time",
        [],
    ),
    (
        "named",
        ["named", "called", "whose name is"],
        "field:Client.name",
        "the client's name",
        [],
    ),
    (
        "phone",
        ["phone", "phone number"],
        "field:Client.phone",
        "the contact phone number",
        [],
    ),
    (
        "for N people",
        ["for N people", "for N", "party of N", "N people"],
        "field:Reservation.party_size",
        "how many people",
        [],
    ),
    (
        "seats N",
        ["for N people", "for N", "seats N", "that seats N"],
        "predicate:Table:capacity >= N",
        "a table with room for N people",
        [],
    ),
    (
        "on the Z",
        ["on the Z", "in the Z"],
        "predicate:Table:zone = Z",
        "where the table is",
        [],
    ),
    (
        "on DAY",
        ["on DAY", "this DAY", "next DAY"],
        "field:Reservation.date",
        "when, as a date",
        [],
    ),
    ("at TIME", ["at TIME"], "field:Reservation.time", "when, as a time", []),
    (
        "book",
        ["book her", "book him", "book them", "make a reservation for"],
        "compose",
        "create a reservation for someone and put it at a table",
        [
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
        ],
    ),
    (
        "assign",
        ["assign", "put it at table", "seat at"],
        "relation:assigned_to",
        "put a reservation at a table",
        [],
    ),
    ("has", ["has", "have", "of"], "relation:booked_by", "someone's reservations", []),
    (
        "confirm",
        ["confirm", "confirm it"],
        "action:change Reservation.status=confirmed",
        "move the reservation to confirmed",
        [],
    ),
    (
        "cancel",
        ["cancel", "cancel it"],
        "action:change Reservation.status=cancelled",
        "cancel the reservation",
        [],
    ),
    (
        "seat",
        ["seat", "seat them", "they arrived"],
        "action:change Reservation.status=seated",
        "mark that they arrived",
        [],
    ),
    (
        "fits",
        ["fits", "fit", "fits at"],
        "predicate:Table:capacity >= {party_size}",
        "whether the table has room for the reservation",
        [],
    ),
    (
        "large",
        ["large", "big"],
        "predicate:Table:capacity >= 6",
        "tables for six or more",
        [],
    ),
    (
        "note",
        ["note", "a note", "add a note", "note saying"],
        "field:Reservation.notes",
        "remarks on the reservation",
        [],
    ),
]


def _run(argv: list[str]) -> None:
    assert sldb_main(argv) == 0, argv


def build_restaurant(base: Path, refresh: bool = True) -> World:
    """Build the whole world under base/ and return it opened."""
    sys.modules.pop("restaurant", None)
    sys.modules.pop("restaurant.models", None)
    pkg = base / "restaurant"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "models.py").write_text(MODELS, encoding="utf-8")
    root = base / "world"
    root.mkdir(exist_ok=True)
    _run(["stores", "init", "--path", str(root)])
    common = ["--store", str(root / ".sldb"), "--pythonpath", str(base)]
    for m in ("Client", "Table", "Reservation", "State"):
        _run(["models", "add", f"restaurant.models:{m}", *common])
    init_world(root, str(base))
    world = World(root, str(base))
    s = world.store
    for n in STATES:
        s.create(
            "State",
            f"state-reservation-{n}",
            {
                "machine": "Reservation.status",
                "name": n,
                "description": f"The reservation is {n}.",
            },
            root / "states" / f"{n}.md",
        )
    for number, cap, zone in TABLES:
        s.create(
            "Table",
            f"table-{number}",
            {"number": number, "capacity": cap, "zone": zone},
            root / "tables" / f"{number}.md",
        )
    s.create(
        "Client",
        "client-ana-perez",
        {"name": "Ana Pérez", "phone": "9 1111 0000", "notes": ""},
        root / "clients" / "ana-perez.md",
    )
    s.create(
        "Client",
        "client-luis-soto",
        {"name": "Luis Soto", "phone": "9 2222 0000", "notes": ""},
        root / "clients" / "luis-soto.md",
    )
    s.create(
        "Reservation",
        "reservation-2026-09-11-luis-soto",
        {
            "date": "2026-09-11",
            "time": "20:00",
            "party_size": 4,
            "status": "pending",
            "notes": "",
        },
        root / "reservations" / "2026-09-11-luis-soto.md",
    )
    for rt in RELATION_TYPES:
        s.create(
            "RelationTypeDoc",
            f"rt-{rt['name']}",
            {"title": rt["name"], "direction": "directed", **rt},
            root / "relations" / "types" / f"{rt['name']}.md",
        )
    for src, tgt, cond in TRANSITIONS:
        name = f"transitions_to--State:state-reservation-{src}--State:state-reservation-{tgt}"
        s.create(
            "RelationDoc",
            name,
            {
                "title": f"{src} transitions_to {tgt}",
                "source_id": f"State:state-reservation-{src}",
                "target_id": f"State:state-reservation-{tgt}",
                "relation_type": "transitions_to",
                "condition": cond,
                "notes": "",
            },
            root / "relations" / f"{name}.md",
        )
    for rel, src, tgt in (
        (
            "booked_by",
            "Reservation:reservation-2026-09-11-luis-soto",
            "Client:client-luis-soto",
        ),
        (
            "assigned_to",
            "Reservation:reservation-2026-09-11-luis-soto",
            "Table:table-3",
        ),
    ):
        name = f"{rel}--{src}--{tgt}"
        s.create(
            "RelationDoc",
            name,
            {
                "title": name,
                "source_id": src,
                "target_id": tgt,
                "relation_type": rel,
                "condition": "",
                "notes": "",
            },
            root / "relations" / f"{name}.md",
        )
    s.create(
        "ProjectionDoc",
        "projection-all",
        PROJECTION,
        root / "knowledge" / "projections" / "all.md",
    )
    for symbol, forms, ref, motive, steps in ALIASES:
        slug = symbol.replace(" ", "-").lower()
        s.create(
            "AnchorDoc",
            f"anchor-{slug}",
            {
                "symbol": symbol,
                "forms": forms,
                "ref": ref,
                "steps": steps,
                "motive": motive,
            },
            root / "knowledge" / "anchors" / f"{slug}.md",
        )
    if refresh:
        world.refresh()
    return world
