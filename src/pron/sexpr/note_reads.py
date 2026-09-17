"""Spec 07: every document a turn resolved, with the hash_c it had when it was read.

A move records what it wrote; it also records what it read, so the ledger can say what the
answer was based on and whether that has moved since. Both the phrase planner (nouns) and
the relation read (edges) note their reads here, once per document.
"""

from __future__ import annotations

from typing import Any

from pron.sexpr.resolution import address_to_export_id
from pron.world.store_error import StoreError


def note_reads(world, addresses: list[str], record: dict[str, Any]) -> None:
    """Add each address to the move's reads, with the hash_c sldb has for it right now."""
    reads = record.setdefault("reads", [])
    seen = {r["address"] for r in reads}
    for a in addresses:
        eid = address_to_export_id(a)
        if eid in seen or ":" not in eid:
            continue
        try:
            reads.append({"address": eid, "hash_c": world.store.hash_of(eid)})
        except StoreError:
            continue
