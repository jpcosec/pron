"""pron's own knowledge base as a fixture: a copy of the repo's spec chapters and explanations
made a world. Shared by the docs tests and the golden CLI tests."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from sldb.cli import main as sldb_main

from pron.world.world import World, init_world

PRON_REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def own(tmp_path_factory) -> World:
    """A copy of pron's own knowledge base: the spec chapters and the hand-written
    explanations the README composes, built from scratch."""
    root = tmp_path_factory.mktemp("pron-own") / "world"
    shutil.copytree(PRON_REPO / "source", root / "source")
    shutil.copytree(
        PRON_REPO / "knowledge" / "explanations", root / "knowledge" / "explanations"
    )
    shutil.copy2(
        PRON_REPO / "knowledge" / "readme.md", root / "knowledge" / "readme.md"
    )
    assert sldb_main(["stores", "init", "--path", str(root)]) == 0
    init_world(root, str(PRON_REPO), with_knowledge=True)
    return World(root, str(PRON_REPO))
