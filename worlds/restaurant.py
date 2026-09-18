"""The world the tests search over: documents, edges and the theorems that go with them.

Kept as data in one place so a test says what it is about and nothing else. The names here
(Table, Reservation, status, assigned_to) are this world's; the engine never mentions one.
"""

from __future__ import annotations

from pathlib import Path

from plnr import MemoryWorld, Theorems

THEOREMS = Path(__file__).with_suffix(".theorems")


def documents() -> dict[str, tuple[str, dict[str, object]]]:
    return {
        "t10": ("Table", {"capacity": 2, "zone": "hall", "number": 10}),
        "t12": ("Table", {"capacity": 6, "zone": "terrace", "number": 12}),
        "t14": ("Table", {"capacity": 8, "zone": "terrace", "number": 14}),
        "ana": ("Client", {"name": "Ana Rojas", "phone": "9 5555 1234"}),
        "luis": ("Client", {"name": "Luis Soto"}),
        "r-1": ("Reservation", {"party_size": 4, "status": "pending"}),
        "s-pending": ("State", {"machine": "status", "name": "pending"}),
        "s-confirmed": ("State", {"machine": "status", "name": "confirmed"}),
        "s-seated": ("State", {"machine": "status", "name": "seated"}),
        "g-1": (
            "Guard",
            {"from": "s-confirmed", "to": "s-seated", "predicate": "party_size <= 6"},
        ),
    }


def edges() -> list[tuple[str, str, str]]:
    return [
        ("transitions_to", "s-pending", "s-confirmed"),
        ("transitions_to", "s-confirmed", "s-seated"),
        ("booked_by", "r-1", "ana"),
        ("assigned_to", "r-1", "t10"),
    ]


def world() -> MemoryWorld:
    return MemoryWorld(documents(), edges())


def theorems() -> Theorems:
    return Theorems().load(THEOREMS.read_text(encoding="utf-8"), source=str(THEOREMS))
