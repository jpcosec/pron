"""`pron docs`: regenerate pron's own knowledge base from this repo (spec 08 step 9)."""

from __future__ import annotations

import click

from pron.cli.options import world_options


@click.command("docs", short_help="Regenerate pron's command docs")
@world_options
@click.option("--check", is_flag=True)
def command(world: str, pythonpath: str | None, check: bool) -> int:
    """Regenerate pron's own knowledge base from this repo: a CliCommandDoc per command, a
    SurfaceDoc per module, a SpecDoc per chapter of source/spec, and the implements edges
    from each module to the chapters its docstring cites.

    Usage:
      pron docs --world . [--check]
    """
    from pron.docs import synchronize_docs
    from pron.world.world import World

    opened = World(world, pythonpath)
    changed = synchronize_docs(opened, check=check)
    print("\n".join(changed) if changed else "up to date")
    if changed and not check:
        opened.refresh()  # the indexes and the graph follow the documents just written
    return 1 if (check and changed) else 0
