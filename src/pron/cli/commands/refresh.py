"""`pron refresh`: rebuild a world's indexes and typed edge index (spec 08 step 9, spec 03)."""

from __future__ import annotations

import click

from pron.cli.options import world_options


@click.command("refresh", short_help="Rebuild indexes and the typed graph")
@world_options
def command(world: str, pythonpath: str | None) -> int:
    """Rebuild the world's indexes and its typed edge index.

    sldb stores update, then sldb.api.rebuild_edges brings the edge index current, in-process.

    Usage:
      pron refresh --world .
    """
    from pron.world.world import World

    report = World(world, pythonpath).refresh()
    print(
        f"edges: {report['docs_written']} written, {report['docs_reused']} reused, "
        f"{report['models_walked']} models walked"
    )
    return 0
