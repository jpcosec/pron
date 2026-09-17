"""A bare world: a new sldb store made a pron world, with nothing declared in it yet."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sldb.cli import main as sldb_main

from pron.world.world import init_world


def init_bare(root: Path, template: Path | None = None) -> dict[str, Any]:
    """Create root, make it a store and a world (with a template's words, if given)."""
    root.mkdir()
    assert sldb_main(["stores", "init", "--path", str(root)]) == 0
    return init_world(root, str(root), template=template)
