"""spec 14 §1: several worlds, each mounted as it is — nothing linked, nothing written — and
one session per (world, speaker); `import pron` does not load the MCP SDK."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

import pron
from mcp_surface.mounted import mount
from pron.mcp.world_mounts import WorldMounts, parse_world
from worlds.restaurant import build_restaurant


CACHE = (".sldb/runtime/", ".pron/")  # derived caches, rewritten by any read


def files(root: Path, content_only: bool = False) -> dict[str, bytes]:
    out = {
        str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()
    }
    return {k: v for k, v in out.items() if not (content_only and k.startswith(CACHE))}


def test_mounting_writes_nothing_in_the_world(tmp_path):
    world = build_restaurant(tmp_path)
    index = world.root / ".sldb" / "core" / "store_index.yaml"
    before, index_bytes = files(world.root), index.read_bytes()
    mount(world)
    assert index.read_bytes() == index_bytes
    assert files(world.root) == before
    assert not world.store.linked()


def test_reading_writes_nothing_but_derived_caches(tmp_path):
    world = build_restaurant(tmp_path)
    before = files(world.root, content_only=True)
    app = mount(world)
    app.tools.call("worlds_list")
    for uri in ("kb://rest/Table/table-3", "kb://rest/@terrace", "kb://rest/?terrace"):
        app.tools.call("kb_get", uri=uri)
    assert files(world.root, content_only=True) == before


def test_a_world_is_named_or_takes_its_directory_name(tmp_path):
    assert parse_world(f"a={tmp_path}") == ("a", tmp_path.resolve())
    assert parse_world(str(tmp_path)) == (tmp_path.name, tmp_path.resolve())


def test_two_worlds_with_one_name_are_refused(world):
    with pytest.raises(ValueError, match="two worlds"):
        WorldMounts([f"x={world.root}", f"x={world.root}"], world.store.pythonpath)


def test_an_unknown_world_says_which_are_mounted(app):
    with pytest.raises(LookupError, match="mounted: rest"):
        app.tools.call("kb_read", world="nope", id="Table:table-3")


def test_sessions_are_one_per_world_and_speaker(app):
    mounts = app.mounts
    assert mounts.session("rest") is mounts.session("rest", "mcp")
    assert mounts.session("rest", "agent-7") is not mounts.session("rest")
    assert mounts.session("rest", "agent-7").dialogue.speaker == "agent-7"


def test_worlds_list_names_roots_and_models(app, world):
    [only] = app.tools.call("worlds_list")["worlds"]
    assert only["name"] == "rest" and only["root"] == str(world.root)
    assert only["models"] == ["Client", "Table", "Reservation", "State"]


def test_importing_pron_and_its_read_plane_does_not_load_the_sdk():
    code = "import sys, pron, pron.cli.main, pron.mcp.app; print('mcp' in sys.modules)"
    env = {**os.environ, "PYTHONPATH": str(Path(pron.__file__).parents[1])}
    out = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    assert out.stdout.split() == ["False"]
