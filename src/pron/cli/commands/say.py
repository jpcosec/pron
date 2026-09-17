"""`pron say`: one sentence to a world, one answer (spec 08 step 8, spec 06, spec 11 §8)."""

from __future__ import annotations

import click

from pron.cli.options import remote_options, talk_options, world_options
from pron.cli.session import session_for


@click.command("say", short_help="Say one sentence")
@world_options
@click.argument("sentence")
@talk_options
@click.option("--trace", is_flag=True)
@remote_options
def command(sentence: str, trace: bool, **opened) -> int:
    """Say one sentence to a world and print the answer, with the trace on request.

    Opens a session with the projection and speaker given, runs one turn, prints the
    answer in natural language; --trace adds the addresses, edges and writes. When a
    `pron serve` listens at the world's socket the sentence goes there and nothing is
    opened here; --local forces opening the world in this process.

    Usage:
      pron say "what tables are on the terrace?" --world . [--projection all] [--speaker me] [--trace] [--local]
    """
    response = session_for(**opened).turn(sentence)
    print(response.text)
    if trace:
        print("\n".join(f"  · {line}" for line in response.trace))
    return 0
