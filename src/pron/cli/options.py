"""The options several pron commands share, declared once (spec 08 step 9): where the world
is, how a session speaks, and whether it goes through a running server (spec 11 §8)."""

from __future__ import annotations

from collections.abc import Callable

import click


def stacked(*decorators: Callable) -> Callable:
    """Apply decorators so the parameters list in the order they are written."""

    def apply(fn: Callable) -> Callable:
        for decorator in reversed(decorators):
            fn = decorator(fn)
        return fn

    return apply


world_options = stacked(
    click.option("--world", default=".", help="World root (contains .sldb)"),
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
