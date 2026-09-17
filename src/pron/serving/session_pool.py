"""The sessions a daemon keeps open (spec 11 §8, 12 §6): one per (world, projection, speaker,
read_only, speaker_address, now). A caller from another world opens only an exposed
projection — the interface — and every session answers before its graph refresh settles.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.ids import is_local
from pron.session import Session
from pron.world.world import World


class SessionPool:
    """Open sessions over one daemon world, by request key."""

    def __init__(self, world: World) -> None:
        self.world = world
        self.sessions: dict[tuple, Session] = {}

    @staticmethod
    def key(world: str, req: dict[str, Any]) -> tuple:
        return (
            world,
            req.get("projection", "all"),
            req.get("speaker", ""),
            bool(req.get("read_only", False)),
            req.get("speaker_address"),
            req.get("now"),
        )

    def session(self, name: str, req: dict[str, Any], foreign: bool) -> Session:
        """One session per (world, projection, speaker, read_only, speaker_address, now). A
        caller from another world opens only an exposed projection: the interface (spec 12 §6)."""
        key = self.key(name, req)
        if key not in self.sessions:
            home = None if is_local(name) else name
            if foreign and not self.world.projection(key[1], home).get("exposed"):
                raise PermissionError(
                    f"projection {key[1]!r} of {name!r} is not exposed to other worlds"
                )
            self.sessions[key] = Session(
                self.world,
                projection=key[1],
                speaker=key[2],
                speaker_address=key[4],
                now=key[5],
                read_only=key[3],
                home=home,
                defer_refresh=True,  # the answer leaves before the graph refresh; handle settles it (11 §8)
            )
        return self.sessions[key]

    def close(self, name: str, req: dict[str, Any]) -> bool:
        """Whether a session was open under the request's key (it is not anymore)."""
        return self.sessions.pop(self.key(name, req), None) is not None
