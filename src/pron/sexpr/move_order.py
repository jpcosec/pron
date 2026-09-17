"""The order the parts of one move run in (spec 06 §Coordinación, spec 13 §Sustantivos).

A move may create a document and, in the same breath, say something about it: "create a
client named Ana and book her a table". The creates with an explicit name are known before
anything runs — their export id is the name the form gave them — so a noun that says one of
them resolves without reading the store, and the part that says it is held back until the
create that makes it has run, even if the form said it first.

The order is a generator on purpose: each part is executed by whoever consumes it before
the next one is chosen, so "already done" means already written, not merely already picked.
"""

from __future__ import annotations

from typing import Any, Iterator

from pron.kernel.ids import address_of, join_id
from pron.kernel.part import Part


def pending_creates(parts: list[Part], write_store: str | None) -> dict[str, str]:
    """The creates of this move with an explicit name, by the export id they will have."""
    ids = [
        _create_id(part, write_store) for part in parts if part.payload.get("name")
    ]
    return {eid: address_of(eid) for eid in ids if eid is not None}


def dependency_order(
    parts: list[Part],
    plans: list[dict[str, Any]],
    pending: dict[str, str],
    write_store: str | None,
) -> Iterator[int]:
    """Each part in turn, never before the create of this move that it names."""
    creates = _creates(parts, pending, write_store)
    remaining = list(range(len(parts)))
    done: set[int] = set()
    while remaining:
        j = remaining.pop(_ready(remaining, plans, creates, done))
        yield j
        done.add(j)


def plan_references(plan: dict[str, Any]) -> list[str]:
    """Export ids a planned part names, so execution can hoist the creates of its move."""
    sides = [{"source": plan.get("subject"), "target": plan.get("object")}]
    return [
        eid for step in sides + plan.get("steps", []) for eid in _step_references(step)
    ]


def _step_references(step: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for res in (step.get("source"), step.get("target")):
        if res is not None and hasattr(res, "export_ids"):
            ids += res.export_ids()
    return ids


def _ready(
    remaining: list[int],
    plans: list[dict[str, Any]],
    creates: dict[str, int],
    done: set[int],
) -> int:
    """Where in what is left the first part sits whose creates have all run."""
    return next(
        idx
        for idx, j in enumerate(remaining)
        if all(
            creates.get(e, j) in done or e not in creates
            for e in plan_references(plans[j])
        )
    )


def _creates(
    parts: list[Part], pending: dict[str, str], write_store: str | None
) -> dict[str, int]:
    """Which part of the move creates each of the names it uses."""
    return {
        eid: i
        for eid in pending
        for i, part in enumerate(parts)
        if _create_id(part, write_store) == eid
    }


def _create_id(part: Part, write_store: str | None) -> str | None:
    if part.kind != "action" or part.payload.get("verb") != "create":
        return None
    if part.subject is None or part.subject.model is None:
        return None
    return join_id(write_store, part.subject.model, part.payload.get("name", ""))
