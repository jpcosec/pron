"""`pron repl`: a session kept open, one sentence per line (spec 08 step 8, spec 11 §8)."""

from __future__ import annotations

from pathlib import Path

import click

from pron.cli.options import remote_options, talk_options, world_options
from pron.cli.session import session_for


@click.command("repl", short_help="Talk to a world")
@world_options
@talk_options
@remote_options
def command(**opened) -> int:
    """Talk to a world, one sentence per line.

    The same session as `say`, kept open: pending questions and referents survive between
    lines. `:trace` toggles the trace, `:lexicon [MODEL]` lists words, `:quit` leaves.
    Through the running server when one listens; --local opens the world here.

    Usage:
      pron repl --world . [--projection all] [--speaker me] [--local]
    """
    from pron.cli.repl import run

    world_name = Path(opened["world"]).resolve().name
    return run(session_for(**opened), world_name, opened["projection"])
