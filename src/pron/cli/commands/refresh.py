"""`pron refresh`: rebuild a world's indexes and typed graph (spec 08 step 9, spec 03)."""

from __future__ import annotations

import click

from pron.cli.options import world_options


@click.command("refresh", short_help="Rebuild indexes and the typed graph")
@world_options
def command(world: str, pythonpath: str | None) -> int:
    """Rebuild the world's indexes and its typed graph.

    sldb stores update, then kgdb's typed ingest into .pron/graph.nx.json, in-process.

    Usage:
      pron refresh --world .
    """
    from pron.world.world import World

    report = World(world, pythonpath).refresh()
    print(
        f"graph: {report['nodes']} nodes, {report['edges']} edges, {len(report['relation_types'])} relation types"
    )
    return 0
