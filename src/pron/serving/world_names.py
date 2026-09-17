"""The names a daemon answers to (spec 01 §Un mundo en varios stores, 12 §7): its own world
by name, by root and as "local", and every world mounted into it by name and by root.
"""

from __future__ import annotations

from pathlib import Path

from pron.kernel.ids import LOCAL
from pron.world.world import World


class WorldNames:
    """name or root -> the store it names in the daemon's world ("local" or a linked store)."""

    def __init__(self, own: str, world: World) -> None:
        self.world = world
        self.names: dict[str, str] = {
            own: LOCAL,
            str(world.root): LOCAL,
            LOCAL: LOCAL,
        }

    def own(self) -> str:
        """The daemon's own world by name."""
        return next(
            n
            for n, v in self.names.items()
            if v == LOCAL and n != LOCAL and not n.startswith("/")
        )

    def worlds(self) -> dict[str, str]:
        """name -> root of every world this daemon serves: its own store and the linked ones."""
        out = {self.own(): str(self.world.root)}
        for name, sp in self.world.store.linked().items():
            out[name] = str(sp.parent)
        return out

    def add(self, name: str, resolved_root: str) -> None:
        self.names[name] = name
        self.names[resolved_root] = name

    def resolve(self, ref: str | None) -> str:
        """The store a request's `world` names; no name is the daemon's own."""
        if ref is None:
            return LOCAL
        key = self.names.get(ref) or self.names.get(str(Path(ref).resolve()))
        if key is None:
            raise KeyError(
                f"no world {ref!r} in this daemon; mounted: {', '.join(sorted(self.worlds()))}"
            )
        return key
