"""A world's words (spec 12 §6, §7): a template gives a new world its words; a turn records
what it read."""

from __future__ import annotations

from pathlib import Path

from sldb.runtime.validation import render_model_markdown

from pron.models.anchor import AnchorDoc
from pron.models.projection import ProjectionDoc
from pron.session import Session
from pron.world.world import World, apply_template
from worlds.bare import init_bare

NOW = "2026-09-09"

MOVE_ALIAS = {
    "symbol": "move",
    "forms": ["move", "moves"],
    "ref": "model:MoveDoc",
    "steps": [],
    "motive": "a recorded turn",
}

INTERFACE = {
    "name": "interface",
    "stores": ["local"],
    "models": ["MoveDoc"],
    "relations": [],
    "actions": [],
    "aliases": ["all"],
    "naming": {},
    "display": {},
    "key": {},
    "matching": {"neighbors": 3, "threshold": 0.55},
    "exposed": True,
    "description": "what other worlds may ask",
}


def _render(path: Path, model, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_model_markdown(model, payload) + "\n", encoding="utf-8")


def _template(tmp_path: Path) -> Path:
    """A world template: one alias and one exposed projection, rendered from their models."""
    t = tmp_path / "template"
    _render(t / "anchors" / "move.md", AnchorDoc, MOVE_ALIAS)
    _render(t / "projections" / "interface.md", ProjectionDoc, INTERFACE)
    return t


def test_a_template_gives_a_new_world_its_words(tmp_path):
    root = tmp_path / "born"
    report = init_bare(root, template=_template(tmp_path))
    assert set(report["template_added"]) == {
        "AnchorDoc:anchor-move",
        "ProjectionDoc:projection-interface",
    }
    world = World(root, str(root))
    assert world.projection("interface")["exposed"] is True
    s = Session(world, projection="interface", now=NOW)
    assert s.turn("the moves").outcome == "unico"
    assert apply_template(root, _template(tmp_path), str(root)) == []  # idempotent


def test_a_turn_records_what_it_read_with_its_hash(restaurant: World):
    s = Session(restaurant, projection="all", speaker="jp", now=NOW)
    r = s.turn("the reservations of Luis Soto")
    reads = {x["address"]: x["hash_c"] for x in r.record["reads"]}
    assert (
        "Client:client-luis-soto" in reads
        and "Reservation:reservation-2026-09-11-luis-soto" in reads
    )
    assert all(len(h) == 64 for h in reads.values())
    assert reads["Client:client-luis-soto"] == restaurant.store.hash_c(
        "Client", "client-luis-soto"
    )
    move = s.ledger.get(r.move_id)
    assert move["record"]["reads"] == r.record["reads"]
