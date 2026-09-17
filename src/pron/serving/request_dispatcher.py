"""What a daemon does with one request (spec 11 §8, 12 §6, §7): the daemon's own ops (worlds,
mount, stop), then, for the world the request names, one of the world ops (`WorldOps`) or
the session ops (`SessionOps`). A caller whose home is another world may ask only for the
foreign ops, never for its store.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any, Callable

from pron.serving.session_ops import SessionOps
from pron.serving.world_ops import WorldOps

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.serve import Server

FOREIGN_OPS = (
    "say",
    "lexicon",
    "state",
    "close",
    "ping",
    "worlds",
)  # what a caller from another world may ask
DAEMON_OPS = ("worlds", "mount", "stop")

Op = Callable[[str, dict[str, Any], bool], dict[str, Any]]


class RequestDispatcher:
    """One server's answer to each op."""

    def __init__(self, server: "Server") -> None:
        self.server = server
        world, sessions = WorldOps(server), SessionOps(server)
        self.ops: dict[str, Op] = {
            "ping": world.ping,
            "say": sessions.say,
            "eval": sessions.eval,
            "payload": world.payload,
            "graph": world.graph,
            "world": world.world,
            "lexicon": sessions.lexicon,
            "state": sessions.state,
            "close": sessions.close,
            "refresh": world.refresh,
        }

    def __call__(self, op: str, req: dict[str, Any]) -> dict[str, Any]:
        if op in DAEMON_OPS:
            return self._daemon(op, req)
        name = self.server.names.resolve(req.get("world"))
        foreign = self._foreign(name, req)
        if foreign and op not in FOREIGN_OPS:
            raise PermissionError(
                f"a caller from another world may only speak to {name!r}: {', '.join(FOREIGN_OPS)}"
            )
        answer = self.ops.get(op)
        if answer is None:
            return {"ok": False, "error": f"unknown op {op!r}"}
        return answer(name, req, foreign)

    def _daemon(self, op: str, req: dict[str, Any]) -> dict[str, Any]:
        server = self.server
        if op == "worlds":
            return {
                "ok": True,
                "worlds": server.worlds(),
                "default": server.names.own(),
            }
        if op == "mount":
            world = server.mount(req["name"], req["root"], req.get("pythonpath"))
            return {"ok": True, "world": world}
        threading.Thread(target=server.stop, daemon=True).start()
        return {"ok": True, "stopping": True}

    def _foreign(self, name: str, req: dict[str, Any]) -> bool:
        home = req.get("home")
        return home is not None and self.server.names.resolve(home) != name
