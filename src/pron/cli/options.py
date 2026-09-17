"""The options several pron commands share, declared once (spec 08 step 9): where the world
is, how a session speaks, and whether it goes through a running server (spec 11 §8)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import click

STORE_INDEX = Path(".sldb") / "core" / "store_index.yaml"


def stacked(*decorators: Callable) -> Callable:
    """Apply decorators so the parameters list in the order they are written."""

    def apply(fn: Callable) -> Callable:
        for decorator in reversed(decorators):
            fn = decorator(fn)
        return fn

    return apply


def existing_world(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """A world is an sldb store (spec 01): without one there is nothing to open."""
    if not (Path(value) / STORE_INDEX).is_file():
        raise click.BadParameter(
            f"no sldb store at {value} (create one there with `sldb stores init`, then `pron init`)"
        )
    return value


world_options = stacked(
    click.option(
        "--world",
        default=".",
        callback=existing_world,
        help="World root (contains .sldb)",
    ),
    click.option(
        "--pythonpath",
        default=None,
        help="Project path where the world's models import from",
    ),
)

talk_options = stacked(
    click.option("--projection", default="all"),
    click.option("--speaker", default=""),
    click.option("--now", default=None),
)

remote_options = stacked(
    click.option(
        "--local",
        is_flag=True,
        help="Open the world here even if a server listens",
    ),
    click.option(
        "--socket",
        default=None,
        help="The daemon's socket, when the world's .pron/serve.sock is not it",
    ),
    click.option(
        "--home",
        default=None,
        help="The caller's own world (name or path); another world opens only its exposed projections",
    ),
)
