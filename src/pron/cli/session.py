"""The session a talking command opens (spec 11 §8): the running server's when one listens at
the world's socket, else one opened in this process."""

from __future__ import annotations

from pathlib import Path


def session_for(
    world: str,
    pythonpath: str | None,
    projection: str,
    speaker: str,
    now: str | None,
    local: bool = False,
    socket: str | None = None,
    home: str | None = None,
):
    """A live session: through the running server when one listens at the world's socket
    (and --local was not asked), else opened here."""
    from pron.remote import RemoteSession, alive, socket_path

    sock = Path(socket) if socket else socket_path(world)
    if not local and alive(sock):
        return RemoteSession(
            sock,
            projection=projection,
            speaker=speaker,
            now=now,
            world=str(Path(world).resolve()),
            home=home,
        )
    from pron.session import Session
    from pron.world.world import World

    return Session(
        World(world, pythonpath), projection=projection, speaker=speaker, now=now
    )
