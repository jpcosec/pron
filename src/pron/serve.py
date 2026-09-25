"""Serve worlds: one process keeps one store open, the daemon's, with the nodes' stores
linked into it; each world is a projection over its own store, and every local caller
(the CLI, the REPL, an agent runtime) says its sentences through the socket instead of
opening a store again (spec 01 §Un mundo en varios stores, 11 §8, 12 §7).

One request per connection, one JSON object per line. Requests are handled one at a
time: a store has one writer, and a turn is short. Each request names the world it
speaks to (a linked store, or the daemon's own) and the caller's own world, `home`; a
caller whose home is another world may open only the projections that world exposes,
its interface lexicon, and nothing else (spec 12 §6): talking to another world is
semantic, never access to its store. The server speaks as whoever the client says it is;
identity is the application's (11 §6). Every mounted world gets `<root>/.pron/serve.sock`
pointing at the daemon's socket, so a client that only knows its world finds the daemon.
The client side is pron.remote.

The pieces live in pron.serving: the names the daemon answers to (`WorldNames`), its open
sessions (`SessionPool`), what each op does (`RequestDispatcher`) and the socket
(`SocketServing`, `RequestHandler`).
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Any, Callable

from pron.remote import RemoteSession, alive, request, socket_path  # noqa: F401 - re-exported for callers of pron.serve
from pron.serving.request_dispatcher import RequestDispatcher
from pron.serving.session_pool import SessionPool
from pron.serving.socket_serving import SocketServing
from pron.serving.world_names import WorldNames
from pron.session import Session
from pron.world.world import World

WorldEntry = tuple[str, "str | Path", "str | None"]


class Server:
    def __init__(
        self,
        root: str | Path | None = None,
        pythonpath: str | None = None,
        sock: str | Path | None = None,
        worlds: list[tuple[str, str | Path, str | None]] | None = None,
        listen: str | None = None,
    ):
        """The daemon's store is `root` (or the first of `worlds`); every other world is
        linked into it under its name, so one store serves them all."""
        entries = self._entries(root, pythonpath, worlds)
        name0, root0, py0 = entries[0]
        self.world = World(root0, py0)
        self.names = WorldNames(name0, self.world)
        self.pool = SessionPool(self.world)
        self.lock = threading.Lock()
        self.socket = SocketServing(
            Path(sock) if sock else socket_path(self.world.root), listen
        )
        self.dispatch = RequestDispatcher(self)
        for name, r, _ in entries[1:]:
            self.mount(name, r)

    @staticmethod
    def _entries(
        root: str | Path | None, pythonpath: str | None, worlds: list[WorldEntry] | None
    ) -> list[WorldEntry]:
        entries = list(worlds or [])
        if root is not None:
            entries.insert(0, (Path(root).resolve().name, root, pythonpath))
        if not entries:
            raise ValueError("a server needs at least one world")
        return entries

    @property
    def path(self) -> Path:
        return self.socket.path

    @property
    def sessions(self) -> dict[tuple, Session]:
        return self.pool.sessions

    # -- worlds -----------------------------------------------------------------------------

    def worlds(self) -> dict[str, str]:
        """name -> root of every world this daemon serves: its own store and the linked ones."""
        return self.names.worlds()

    def mount(self, name: str, root: str | Path, pythonpath: str | None = None) -> str:
        """Link a world's store into the daemon's under `name`; its root is an alias too."""
        resolved = str(Path(root).resolve())
        if resolved in self.names.names:
            return self.names.names[resolved]
        self.world.store.link(name, resolved)
        self.names.add(name, resolved)
        if self.socket.is_serving:
            self.socket.link(Path(resolved))
        return name

    # -- requests ---------------------------------------------------------------------------

    def handle(
        self,
        req: dict[str, Any],
        respond: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        """One request under the server's lock. With `respond`, the answer is written and
        flushed inside the lock: the client's bytes leave before the deferred graph refresh
        settles, and the settle runs right after them, still under this lock — the next
        request waits on the lock and always reads a fresh graph (spec 11 §8)."""
        op = req.get("op", "say")
        with self.lock:
            try:
                resp = self.dispatch(op, req)
            except Exception as e:  # noqa: BLE001 - the answer says what the world refused; the server stays up
                resp = {"ok": False, "error": f"{type(e).__name__}: {e}"}
            if respond is not None:
                respond(resp)
            self._settle()
            return resp

    def _settle(self) -> None:
        """Run the pending refresh of the one world every session shares — the mounted
        stores ride in the same World (World.defer_refresh accumulates their union). A
        settle that raises keeps its pending state (World.settle) and is only logged: the
        next request retries it, synchronously, through world.graph."""
        try:
            self.world.settle()
        except Exception as e:  # noqa: BLE001 - the refresh is retried on the next request; the server stays up
            print(
                f"pron serve: the deferred graph refresh failed, "
                f"it will run again before the next answer: {type(e).__name__}: {e}",
                file=sys.stderr,
            )

    # -- the socket -------------------------------------------------------------------------

    def serve_forever(self) -> None:
        self.socket.serve(self, self._roots)

    def _roots(self) -> list[Path]:
        """The daemon's own root and every linked store's: each gets a link to the socket."""
        return [
            self.world.root,
            *(sp.parent for sp in self.world.store.linked().values()),
        ]

    def stop(self) -> None:
        self.socket.stop()
