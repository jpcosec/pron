"""`pron eval`: one move written as forms (spec 13), answered like a sentence (spec 11 §8)."""

from __future__ import annotations

import click

from pron.cli.options import remote_options, talk_options, world_options
from pron.cli.session import session_for


@click.command("eval", short_help="Evaluate one move written as forms")
@world_options
@click.argument("forms")
@talk_options
@click.option("--trace", is_flag=True)
@remote_options
def command(forms: str, trace: bool, **opened) -> int:
    """Evaluate one move written as forms (spec 13) and print the answer, with the trace on request.

    The same move a sentence resolves to, without the natural language surface: nouns by
    address (doc "Model:name") or by predicate (find Model (where "...")), and the kernel's
    verbs, relations and aliases by name. Goes through the running `pron serve` when one listens.

    Usage:
      pron eval '(say confirm (doc "Reservation:reservation-x"))' --world . [--projection all] [--speaker me] [--trace] [--local]
    """
    response = session_for(**opened).eval(forms)
    print(response.text)
    if trace:
        print("\n".join(f"  · {line}" for line in response.trace))
    return 0
