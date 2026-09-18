"""The worlds of one MCP server (spec 14 §1): one independent `World` per `--world`, opened
without linking any store into another and without writing anything, and the sessions,
one per `(world, speaker)`, that the write tools evaluate their forms in.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pron.mcp.mount import Mount
from pron.world.world import World

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.session import Session


def parse_world(spec: str) -> tuple[str, Path]:
    """`NAME=PATH`, or a `PATH` named after its directory (spec 14 §1)."""
    if "=" in spec and not Path(spec).exists():
        name, _, path = spec.partition("=")
    else:
        name, path = "", spec
    root = Path(path).resolve()
    return name or root.name, root


class WorldMounts:
    """name -> Mount, and the sessions of each world by speaker."""

    def __init__(
        self,
        specs: list[str],
        pythonpath: str | None = None,
        projection: str = "all",
        speaker: str = "mcp",
    ) -> None:
        self.projection, self.speaker = projection, speaker
        self.mounts: dict[str, Mount] = {}
        for name, root in map(parse_world, specs):
            if name in self.mounts:
                raise ValueError(f"two worlds named {name!r}")
            self.mounts[name] = Mount(name, World(root, pythonpath), projection)
        self._sessions: dict[tuple[str, str], Session] = {}

    def names(self) -> list[str]:
        return list(self.mounts)

    def __getitem__(self, name: str) -> Mount:
        try:
            return self.mounts[name]
        except KeyError:
            known = ", ".join(self.mounts) or "none"
            raise LookupError(f"no world named {name!r} (mounted: {known})") from None

    def session(self, world: str, speaker: str | None = None) -> "Session":
        """The session of `(world, speaker)`, opened on first use and kept (spec 14 §1): a
        pending question of a form stays in it for the next form of the same speaker."""
        from pron.session import Session

        who = speaker or self.speaker
        key = (world, who)
        if key not in self._sessions:
            mount = self[world]
            self._sessions[key] = Session(mount.world, self.projection, speaker=who)
        return self._sessions[key]

    def forget_sessions(self, world: str) -> None:
        """Drop the world's sessions (its models changed): the next call opens a new one."""
        for key in [k for k in self._sessions if k[0] == world]:
            del self._sessions[key]
