"""Model editing (spec 12 §4, spec 10 §3): the class editor's door into pron.

A draft lives in a `.py.temp` sibling of the compiled model module until `model_promote`
installs it, reindexes, and bumps the version. Promotion mutates the model for the rest
of the process, so unlike most of this suite it needs a fresh world per test.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pron.world.store import Store
from pron.world.store_error import StoreError
from pron.world.world import World
from worlds.restaurant import build_restaurant


@pytest.fixture()
def world(tmp_path: Path) -> World:
    return build_restaurant(tmp_path)


def _model_path(store: Store, name: str) -> str:
    return next(m["path"] for m in store.model_catalog() if m["name"] == name)


def test_model_catalog_lists_registered_models_with_version(world: World):
    catalog = {m["name"]: m for m in world.store.model_catalog()}
    assert catalog["Table"]["version"] == 1
    assert catalog["Table"]["family"] == "restaurant"
    assert catalog["Table"]["documents"] == 5


def test_model_detail_matches_show(world: World):
    detail = world.store.model_detail("Table")
    field_names = {f["name"] for f in detail["model"]["fields"]}
    assert {"number", "capacity", "zone"} <= field_names
    assert detail["model"]["version"] == 1


def test_model_fields_add_writes_draft_sibling_without_mutating_active_source(
    world: World,
):
    active = Path(_model_path(world.store, "Table"))
    active_before = active.read_text(encoding="utf-8")
    draft = world.store.model_fields_add(
        "Table", "priority", field_type="int", description="Prioridad", default="5"
    )
    assert draft == active.with_name(active.name + ".temp")
    assert draft.exists()
    assert "priority" in draft.read_text(encoding="utf-8")
    assert active.read_text(encoding="utf-8") == active_before


def test_model_fields_remove_updates_draft(world: World):
    world.store.model_fields_add("Table", "priority", field_type="int", description="x")
    draft = world.store.model_fields_remove("Table", "priority")
    assert "priority" not in draft.read_text(encoding="utf-8")


def test_model_template_edit_writes_draft(world: World):
    draft = world.store.model_template_edit(
        "Table", "number: ⸢rev•number⸥\n---\n\n# Mesa ⸢render•number⸥"
    )
    assert draft.exists()
    assert "Mesa" in draft.read_text(encoding="utf-8")


def test_model_validate_draft_reports_draft_true_and_valid_true(world: World):
    world.store.model_fields_add(
        "Table", "priority", field_type="int", description="x", default="5"
    )
    result = world.store.model_validate_draft("Table")
    assert result["valid"] is True
    assert result["draft"] is True
    assert result["promoted"] is False
    assert all(d["valid"] for d in result["documents"])


def test_model_promote_without_draft_raises_store_error(world: World):
    with pytest.raises(StoreError, match="draft"):
        world.store.model_promote("Table")


def test_model_promote_installs_draft_bumps_version_and_is_visible_immediately(
    world: World,
):
    active = Path(_model_path(world.store, "Table"))
    world.store.model_fields_add(
        "Table", "priority", field_type="int", description="x", default="5"
    )
    world.store.model_validate_draft("Table")
    result = world.store.model_promote("Table")

    assert result["promoted"] is True
    assert result["version"] == 2
    assert not active.with_name(active.name + ".temp").exists()

    # Visible in the same process without restarting: model_promote must invalidate
    # sldb's `sys.modules` cache of the model's module, or this next read would still
    # see the pre-promote class.
    assert "priority" in {f["name"] for f in world.store.schema("Table")}


def test_replace_rewrites_whole_payload(world: World):
    before = world.store.payload("Table", "table-3")
    new_zone = "terrace" if before["zone"] != "terrace" else "indoor"
    world.store.replace("Table", "table-3", {**before, "zone": new_zone})
    assert world.store.payload("Table", "table-3")["zone"] == new_zone


def test_replace_of_matches_replace(world: World):
    before = world.store.payload("Table", "table-5")
    new_zone = "terrace" if before["zone"] != "terrace" else "indoor"
    world.store.replace_of("Table:table-5", {**before, "zone": new_zone})
    assert world.store.payload_of("Table:table-5")["zone"] == new_zone
