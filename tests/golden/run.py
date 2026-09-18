"""Drivers of the characterization scripts: play a list of steps on a session and capture,
per step, everything a turn observably produces."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from pron.kernel.parts.response import Response
from pron.session import Session
from pron.world.doc_id import DocId
from pron.world.world import World
from golden.normalize import Normalizer
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"
LUIS = "Reservation:reservation-2026-09-11-luis-soto"
MODELS = ["Client", "Table", "Reservation", "State"]

Step = str | tuple[str, Any]


def restaurant(base: Path, projection: str = "all", **kw) -> tuple[World, Session]:
    """The spec 09a world with the extra projections and words the scripts use."""
    world = build_restaurant(base)
    add_projection(world, "keeper", models=[*MODELS, "AnchorDoc"])
    read = [
        {"name": r["name"], "mode": "read"}
        for r in world.projection("all")["relations"]
    ]
    add_projection(world, "creator", actions=["create"], relations=read)
    world.store.create(
        DocId.of("AnchorDoc", "anchor-prebook"),
        {
            "symbol": "prebook",
            "forms": ["prebook her", "prebook him"],
            "ref": '(move (assert booked_by (created) (it "it" Client)) (create Reservation))',
            "steps": [],
            "motive": "a compose alias that refers to what it has not created yet",
        },
        world.root / "knowledge" / "anchors" / "prebook.md",
    )
    return world, Session(world, projection=projection, speaker="jp", now=NOW, **kw)


def add_projection(world: World, name: str, **overrides: Any) -> None:
    proj = dict(world.projection("all"), name=name, **overrides)
    path = world.root / "knowledge" / "projections" / f"{name}.md"
    world.store.create(DocId.of("ProjectionDoc", f"projection-{name}"), proj, path)


def play(session: Session, steps: list[Step], base: Path) -> list[dict[str, Any]]:
    """Each step is a sentence, ("eval", forms), or ("outside", fn(world)) for a change made
    to the world by someone other than this session; all run before anything is compared."""
    norm = Normalizer(base, base.resolve())
    return [norm(_step(session, step)) for step in steps]


def _step(session: Session, step: Step) -> dict[str, Any]:
    kind, arg = ("turn", step) if isinstance(step, str) else step
    if kind == "outside":
        return {"outside": arg(session.world)}
    said: Callable[[str], Response] = session.eval if kind == "eval" else session.turn
    return {kind: arg, **capture(session, said(arg))}


def capture(session: Session, r: Response) -> dict[str, Any]:
    move = (
        session.world.store.doc(DocId.of("MoveDoc", r.move_id)) if r.move_id else None
    )
    ledger = dict(move.payload) if move else None
    ledger_record = ledger.pop("record", None) if ledger else None
    return {
        "text": r.text,
        "outcome": r.outcome,
        "trace": r.trace,
        "record": r.record,
        "move_id": r.move_id,
        "ledger": ledger,
        "ledger_record_is_response_record": ledger_record == r.record,
        "written": _written(session.world, r.record.get("writes") or []),
    }


def _written(world: World, writes: list[dict[str, Any]]) -> dict[str, Any]:
    """The payload each written address now reads from the store; None when it is gone.
    Addresses here are local `Model:name`, and a RelationDoc's name has colons of its own."""
    out: dict[str, Any] = {}
    for w in writes:
        model, _, name = (w.get("address") or "").partition(":")
        doc = world.store.doc(DocId.of(model, name)) if name else None
        out[w.get("address") or "?"] = doc.payload if doc else None
    return out
