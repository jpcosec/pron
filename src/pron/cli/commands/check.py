"""`pron check`: pron's lints over a world (spec 08, Lints)."""

from __future__ import annotations

import click

from pron.cli.options import world_options


@click.command("check", short_help="Run pron's lints")
@world_options
def command(world: str, pythonpath: str | None) -> int:
    """Run pron's lints over a world and fail on any violation.

    Usage:
      pron check --world .
    """
    from pron.lints import run_lints
    from pron.world.world import World

    problems = run_lints(World(world, pythonpath))
    for p in problems:
        print(f"FAIL {p}")
    print("ok" if not problems else f"{len(problems)} problem(s)")
    return 0 if not problems else 1
