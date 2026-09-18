"""spec 14 §4, §5 over the real transport: `pron mcp` as a subprocess on stdio, driven by the
SDK's client over a copy of the restaurant — content, rules and models written by tools, and
the ladder refusing a tool above the projection's level. The pythonpath is the copy's own
temporary one, so the generated model never lands in the repository."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import anyio
import pytest

import pron
from mcp_wiring.wired import DISH, LUIS, restaurant

stdio = pytest.importorskip("mcp.client.stdio")
from mcp import ClientSession  # noqa: E402

EVA = "Client:client-eva-rojas"
RES = "Reservation:reservation-2026-09-12-eva-rojas"
EVA_FIELDS = {"name": "Eva Rojas", "phone": "9 3333 0000", "notes": ""}
RES_FIELDS = {
    "date": "2026-09-12",
    "time": "21:00",
    "party_size": 2,
    "status": "pending",
}
TOUGHER = {"condition": "capacity >= 100"}


def server(world, projection: str) -> stdio.StdioServerParameters:
    args = ["-m", "pron.cli.main", "mcp", "--world", f"rest={world.root}"]
    args += ["--pythonpath", world.store.pythonpath, "--projection", projection]
    env = {**os.environ, "PYTHONPATH": str(Path(pron.__file__).parents[1])}
    return stdio.StdioServerParameters(command=sys.executable, args=args, env=env)


async def session_of(world, projection, script):
    async with stdio.stdio_client(server(world, projection)) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            async def call(tool: str, **args) -> dict:
                """The tool's JSON answer; `world` is rest unless None drops it."""
                sent = {
                    k: v for k, v in {"world": "rest", **args}.items() if v is not None
                }
                result = await session.call_tool(tool, sent)
                return json.loads(result.content[0].text)

            return await script(call)


async def content(call) -> dict:
    out = {
        "eva": await call(
            "kb_doc_create", model="Client", fields=EVA_FIELDS, name="client-eva-rojas"
        )
    }
    await call(
        "kb_doc_create",
        model="Reservation",
        fields={**RES_FIELDS, "notes": ""},
        name=RES.split(":")[1],
    )
    edge = dict(source=RES, relation="booked_by", target=EVA)
    out["assert"] = await call("kb_edge_assert", **edge)
    out["expire"] = await call("kb_edge_expire", **edge)
    out["expired"] = await call("kb_neighbors", id=RES, relation="booked_by")
    out["undo"] = await call("kb_undo")
    out["back"] = await call("kb_neighbors", id=RES, relation="booked_by")
    out["held"] = await call("kb_rule_edit", name="assigned_to", changes=TOUGHER)
    out["forced"] = await call(
        "kb_rule_edit", name="assigned_to", changes=TOUGHER, confirm=True
    )
    return out


async def models(call) -> dict:
    out = {"preview": await call("kb_model_create", name="Dish", fields=DISH)}
    out["created"] = await call(
        "kb_model_create", name="Dish", fields=DISH, confirm=True
    )
    out["schema"] = await call("kb_get", uri="kb://rest/_schema", world=None)
    fields = {"title": "Flan", "price": 3, "course": "dessert"}
    out["flan"] = await call(
        "kb_doc_create", model="Dish", fields=fields, name="dish-flan"
    )
    return out


async def level_1(call) -> dict:
    return await call("kb_rule_edit", name="assigned_to", changes=TOUGHER)


def test_writes_over_stdio(tmp_path):
    world = restaurant(tmp_path)
    out = anyio.run(session_of, world, "models", content)
    assert out["eva"]["outcome"] == "unico" and out["eva"]["move_id"]
    assert out["assert"]["outcome"] == "unico", out["assert"]["text"]
    assert out["expire"]["outcome"] == "unico" and out["expired"]["edges"] == []
    assert out["undo"]["outcome"] == "unico"
    assert [e["target"] for e in out["back"]["edges"]] == [f"sldb://document/{EVA}"]
    assert out["held"]["outcome"] == "error" and out["held"]["writes"] == []
    assert [b["source"] for b in out["held"]["broken"]] == [LUIS]
    assert out["forced"]["outcome"] == "unico" and len(out["forced"]["broken"]) == 1


def test_models_and_the_ladder_over_stdio(tmp_path):
    world = restaurant(tmp_path)
    out = anyio.run(session_of, world, "models", models)
    assert out["preview"]["outcome"] == "preview" and not out["preview"]["written"]
    assert out["created"]["outcome"] == "unico"
    assert Path(out["created"]["path"]).is_relative_to(tmp_path)
    assert "Dish" in [m["name"] for m in out["schema"]["models"]]
    assert out["flan"]["outcome"] == "unico", out["flan"]["text"]
    refused = anyio.run(session_of, world, "all", level_1)
    assert refused["outcome"] == "error" and refused["level"] == {
        "needed": 2,
        "session": 1,
    }
