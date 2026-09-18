"""spec 14 §4, nivel 3: kb_model_create and kb_model_extend — a preview that writes nothing
without confirm; with it, the model generated under the pythonpath, registered, named by
_schema and writable by the forms; and a registered model changed through its draft."""

from __future__ import annotations

from pathlib import Path

from mcp_wiring.wired import DISH, restaurant, wire

NOTES = {"name": "notes", "type": "str", "description": "Notes.", "required": False}


def create(app, w, **kw):
    return app.tools.call("kb_model_create", world=w, name="Dish", fields=DISH, **kw)


def schema(app, w) -> dict:
    models = app.tools.call("kb_get", uri=f"kb://{w}/_schema")["models"]
    return {m["name"]: [f["name"] for f in m["fields"]] for m in models}


def test_without_confirm_nothing_is_written(tmp_path):
    world = restaurant(tmp_path)
    app, w = wire(world, "models")
    preview = create(app, w)
    assert preview["outcome"] == "preview" and not preview["written"]
    assert preview["model_ref"] == f"pron_generated.{w}.dish:Dish"
    assert "class Dish(StructuredNLDoc):" in preview["module"]
    assert not Path(preview["path"]).exists() and "Dish" not in schema(app, w)


def test_with_confirm_the_model_is_registered_and_writable(tmp_path):
    app, w = wire(restaurant(tmp_path), "models")
    done = create(app, w, confirm=True)
    assert done["outcome"] == "unico" and Path(done["path"]).is_file()
    assert Path(done["path"]).is_relative_to(tmp_path)
    assert schema(app, w)["Dish"] == ["title", "price", "course", "tags"]
    fields = {"title": "Flan", "price": 3, "course": "dessert"}
    made = app.tools.call(
        "kb_doc_create", world=w, model="Dish", fields=fields, name="dish-flan"
    )
    assert made["outcome"] == "unico", made["text"]
    assert (
        app.tools.call("kb_read", world=w, id="Dish:dish-flan")["payload"]["price"] == 3
    )
    assert create(app, w, confirm=True)["outcome"] == "error"


def test_a_model_on_a_base_carries_its_fields(tmp_path):
    world = restaurant(tmp_path)
    app, w = wire(world, "models")
    fields = [{"name": "since", "type": "str", "description": "Member since."}]
    args = dict(world=w, name="Member", fields=fields, base="Client", confirm=True)
    done = app.tools.call("kb_model_create", **args)
    assert done["outcome"] == "unico", done
    assert "class Member(Client):" in done["module"]
    assert schema(app, w)["Member"] == ["name", "phone", "notes", "since"]
    unknown = app.tools.call(
        "kb_model_create", **{**args, "name": "Other", "base": "Nope"}
    )
    assert unknown["outcome"] == "error" and "base" in unknown["text"]


def test_extend_previews_the_draft_and_leaves_none(tmp_path):
    world = restaurant(tmp_path)
    app, w = wire(world, "models")
    answer = app.tools.call(
        "kb_model_extend", world=w, name="Table", add_fields=[NOTES]
    )
    assert answer["outcome"] == "preview" and "notes: str" in answer["draft"]
    assert answer["validation"]["draft"] is True
    assert not Path(answer["validation"]["path"]).exists()
    assert "notes" not in schema(app, w)["Table"]


def test_extend_with_confirm_promotes(tmp_path):
    world = restaurant(tmp_path)
    app, w = wire(world, "models")
    call = lambda **kw: app.tools.call("kb_model_extend", world=w, name="Table", **kw)  # noqa: E731
    done = call(add_fields=[NOTES], confirm=True)
    assert done["outcome"] == "unico" and done["promoted"]["version"] == 2
    assert schema(app, w)["Table"][-1] == "notes"
    assert call()["outcome"] == "error"
    required = {**NOTES, "name": "chef", "required": True}
    refused = call(add_fields=[required], confirm=True)
    assert refused["outcome"] == "error" and "chef" not in schema(app, w)["Table"]
