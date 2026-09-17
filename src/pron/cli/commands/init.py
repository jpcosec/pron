"""`pron init`: make a store a pron world (spec 08 step 9, spec 01)."""

from __future__ import annotations

import json

import click

from pron.cli.options import world_options


@click.command("init", short_help="Make a store a pron world")
@world_options
@click.option(
    "--knowledge",
    is_flag=True,
    help="Also what pron's own knowledge base needs",
)
@click.option(
    "--template",
    default=None,
    help="World template directory: anchors/, projections/, relations/types/, relations/",
)
def command(
    world: str, pythonpath: str | None, knowledge: bool, template: str | None
) -> int:
    """Make a store a pron world.

    Runs kgdb init (typed relations) and registers pron's models: AnchorDoc, ProjectionDoc,
    MoveDoc; with --knowledge also SpecDoc, the command and module docs, and the relation
    type implements, for pron's own knowledge base. Idempotent.

    With --template DIR, the world is born with the words, projections and relation
    types the template holds (anchors/, projections/, relations/types/, relations/).

    Usage:
      pron init --world . [--pythonpath .] [--knowledge] [--template DIR]
    """
    from pron.world.world import init_world

    report = init_world(world, pythonpath, with_knowledge=knowledge, template=template)
    print(json.dumps(report, indent=2))
    return 0
