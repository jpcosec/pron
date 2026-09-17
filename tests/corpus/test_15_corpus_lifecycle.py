"""The indexed corpus of a world (spec 12 §5b): the life cycle of a world is pron's business."""

from __future__ import annotations

from pron.world.world import World


# -- the life cycle of a world is pron's business -----------------------------------------


def test_a_built_world_is_ready_and_ensuring_it_again_does_nothing(world):
    assert world.is_ready()
    assert world.ensure_ready() is None


def test_ensure_ready_makes_a_plain_store_a_world(tmp_path):
    from sldb.cli.main import main as sldb_main

    root = tmp_path / "plain"
    root.mkdir()
    assert sldb_main(["stores", "init", "--path", str(root)]) == 0
    plain = World(root)
    assert not plain.is_ready()
    report = plain.ensure_ready()
    assert report is not None
    assert plain.is_ready()
