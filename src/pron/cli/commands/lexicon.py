"""`pron lexicon`: what a projection can say (spec 08 step 9, spec 05)."""

from __future__ import annotations

import json as jsonlib

import click

from pron.cli.options import world_options


@click.command("lexicon", short_help="List what this projection can say")
@world_options
@click.argument("model", required=False, default=None)
@click.option("--projection", default="all")
@click.option("--json", "json", is_flag=True)
def command(
    world: str, pythonpath: str | None, model: str | None, projection: str, json: bool
) -> int:
    """List what this projection can say.

    Every word with its kind, what it names and its motive; with a model, the verbs that
    class takes and its fields. Answers "what can I say?".

    Usage:
      pron lexicon --world . [--projection all] [MODEL] [--json]
    """
    from pron.world.lexicon import Lexicon
    from pron.world.world import World

    opened = World(world, pythonpath)
    rows = Lexicon(opened, opened.projection(projection)).table(model)
    if json:
        print(jsonlib.dumps(rows, indent=2, ensure_ascii=False))
        return 0
    width = max((len(r["form"]) for r in rows), default=10)
    for r in rows:
        print(f"{r['form']:<{width}}  {r['kind']:<16} {r['ref']:<48} {r['motive']}")
    return 0
