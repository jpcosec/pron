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
The client side is pron.client.
"""

from __future__ import annotations

import json
import os
import socketserver
import threading
from pathlib import Path
from typing import Any

from pron.client import RemoteSession, alive, request, socket_path  # noqa: F401 - re-exported for callers of pron.serve
from pron.ids import LOCAL, is_local
from pron.session import Session
from pron.world import World

GRAPH_METHODS = (
    "has_node",
    "node",
    "node_type",
    "edges_from",
    "edges_to",
    "exists",
    "nodes_of_type",
    "targets",
    "sources",
    "roots",
    "children",
    "parent",
    "descendants",
    "neighbors_via",
    "built_from",
    "available",
)
WORLD_METHODS = (
    "model_names",
    "family_of",
    "relation_types",
    "projection",
    "hash_mundo",
    "model_hashes",
    "graph_is_fresh",
)
FOREIGN_OPS = (
    "say",
    "lexicon",
    "state",
    "close",
    "ping",
    "worlds",
)  # what a caller from another world may ask


def _key(world: str, req: dict[str, Any]) -> tuple:
    return (
        world,
        req.get("projection", "all"),
        req.get("speaker", ""),
        bool(req.get("read_only", False)),
        req.get("speaker_address"),
        req.get("now"),
    )


def _call(target: Any, allowed: tuple[str, ...], req: dict[str, Any]) -> Any:
    """One method of the world or the graph, by name, from the allowed list, with json args."""
    method = req.get("method", "")
    if method not in allowed:
        raise ValueError(f"unknown method {method!r}; one of {', '.join(allowed)}")
    args = req.get("args") or {}
    if "exclude_prefixes" in args:
        args["exclude_prefixes"] = tuple(args["exclude_prefixes"])
    return getattr(target, method)(**args)


class Server:
    def __init__(
        self,
        root: str | Path | None = None,
        pythonpath: str | None = None,
        sock: str | Path | None = None,
        worlds: list[tuple[str, str | Path, str | None]] | None = None,
    ):
        """The daemon's store is `root` (or the first of `worlds`); every other world is
        linked into it under its name, so one store serves them all."""
        entries = list(worlds or [])
        if root is not None:
            entries.insert(0, (Path(root).resolve().name, root, pythonpath))
        if not entries:
            raise ValueError("a server needs at least one world")
        name0, root0, py0 = entries[0]
        self.world = World(root0, py0)
        self.names: dict[str, str] = {
            name0: LOCAL,
            str(self.world.root): LOCAL,
            LOCAL: LOCAL,
        }
        self.sessions: dict[tuple, Session] = {}
        self.lock = threading.Lock()
        self.links: list[Path] = []
        self._srv: socketserver.UnixStreamServer | None = None
        for name, r, _ in entries[1:]:
            self.mount(name, r)
        self.path = Path(sock) if sock else socket_path(self.world.root)

    # -- worlds -----------------------------------------------------------------------------

    def worlds(self) -> dict[str, str]:
        """name -> root of every world this daemon serves: its own store and the linked ones."""
        out = {self._own_name(): str(self.world.root)}
        for name, sp in self.world.store.linked().items():
            out[name] = str(sp.parent)
        return out

    def _own_name(self) -> str:
        return next(
            n
            for n, v in self.names.items()
            if v == LOCAL and n != LOCAL and not n.startswith("/")
        )

    def mount(self, name: str, root: str | Path, pythonpath: str | None = None) -> str:
        """Link a world's store into the daemon's under `name`; its root is an alias too."""
        resolved = str(Path(root).resolve())
        if resolved in self.names:
            return self.names[resolved]
        self.world.store.link(name, resolved)
        self.names[name] = name
        self.names[resolved] = name
        if self._srv is not None:
            self._link(Path(resolved))
        return name

    def _world_name(self, ref: str | None) -> str:
        if ref is None:
            return LOCAL
        key = self.names.get(ref) or self.names.get(str(Path(ref).resolve()))
        if key is None:
            raise KeyError(
                f"no world {ref!r} in this daemon; mounted: {', '.join(sorted(self.worlds()))}"
            )
        return key

    def _link(self, root: Path) -> None:
        """<root>/.pron/serve.sock -> the daemon's socket, so `pron say --world <root>` finds it."""
        link = socket_path(root)
        if link == self.path or link.parent != root / ".pron":
            return
        link.parent.mkdir(parents=True, exist_ok=True)
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(self.path)
        self.links.append(link)

    # -- requests ---------------------------------------------------------------------------

    def handle(self, req: dict[str, Any]) -> dict[str, Any]:
        op = req.get("op", "say")
        with self.lock:
            try:
                return self._dispatch(op, req)
            except Exception as e:  # noqa: BLE001 - the answer says what the world refused; the server stays up
                return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    def _dispatch(self, op: str, req: dict[str, Any]) -> dict[str, Any]:
        if op == "worlds":
            return {"ok": True, "worlds": self.worlds(), "default": self._own_name()}
        if op == "mount":
            return {
                "ok": True,
                "world": self.mount(req["name"], req["root"], req.get("pythonpath")),
            }
        if op == "stop":
            threading.Thread(target=self.stop, daemon=True).start()
            return {"ok": True, "stopping": True}
        name = self._world_name(req.get("world"))
        foreign = self._foreign(name, req)
        if foreign and op not in FOREIGN_OPS:
            raise PermissionError(
                f"a caller from another world may only speak to {name!r}: {', '.join(FOREIGN_OPS)}"
            )
        world = self.world
        if op == "ping":
            return {
                "ok": True,
                "world": str(world.root),
                "name": name if not is_local(name) else self._own_name(),
                "hash": world.hash_mundo(),
                "sessions": len(self.sessions),
                "pid": os.getpid(),
            }
        if op in ("say", "eval"):
            sess = self._session(name, req, foreign)
            r = sess.turn(req["sentence"]) if op == "say" else sess.eval(req["forms"])
            return {
                "ok": True,
                "text": r.text,
                "outcome": r.outcome,
                "move": r.move_id,
                "trace": r.trace,
                "record": r.record,
            }
        if op == "payload":
            self._in_projection(name, req, req["model"])
            return {
                "ok": True,
                "payload": world.store.payload(req["model"], req["doc"], name),
            }
        if op == "graph":
            return {"ok": True, "result": _call(world.graph, GRAPH_METHODS, req)}
        if op == "world":
            return {"ok": True, "result": _call(world, WORLD_METHODS, req)}
        if op == "lexicon":
            return {
                "ok": True,
                "rows": self._session(name, req, foreign).lex.table(req.get("model")),
            }
        if op == "state":
            d = self._session(name, req, foreign).dialogue
            return {
                "ok": True,
                "state": d.state,
                "singular": d.singular,
                "set": d.last_set,
                "pending": d.pending.kind if d.pending else None,
            }
        if op == "close":
            return {
                "ok": True,
                "closed": self.sessions.pop(_key(name, req), None) is not None,
            }
        if op == "refresh":
            return {"ok": True, "report": world.refresh()}
        return {"ok": False, "error": f"unknown op {op!r}"}

    def _foreign(self, name: str, req: dict[str, Any]) -> bool:
        home = req.get("home")
        return home is not None and self._world_name(home) != name

    def _session(self, name: str, req: dict[str, Any], foreign: bool) -> Session:
        """One session per (world, projection, speaker, read_only, speaker_address, now). A
        caller from another world opens only an exposed projection: the interface (spec 12 §6)."""
        key = _key(name, req)
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
            )
        return self.sessions[key]

    def _in_projection(self, name: str, req: dict[str, Any], model: str) -> None:
        """A payload read names a projection or none; with one, the model must be in it (01)."""
        pname = req.get("projection")
        if not pname:
            return
        from pron.lexicon import projection_models

        if model not in projection_models(
            self.world, self.world.projection(pname, None if is_local(name) else name)
        ):
            raise PermissionError(f"{model} is not in projection {pname!r}")

    # -- the socket -------------------------------------------------------------------------

    def serve_forever(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() or self.path.is_symlink():
            if alive(self.path):
                raise RuntimeError(f"a server already listens at {self.path}")
            self.path.unlink()
        app = self

        class Handler(socketserver.StreamRequestHandler):
            def handle(self) -> None:
                line = self.rfile.readline()
                if not line:
                    return
                try:
                    req = json.loads(line)
                except ValueError as e:
                    resp = {"ok": False, "error": f"bad request: {e}"}
                else:
                    resp = app.handle(req)
                self.wfile.write(
                    json.dumps(resp, default=str, ensure_ascii=False).encode("utf-8")
                    + b"\n"
                )

        self._srv = socketserver.UnixStreamServer(str(self.path), Handler)
        self._link(self.world.root)
        for sp in self.world.store.linked().values():
            self._link(sp.parent)
        try:
            self._srv.serve_forever()
        finally:
            self._srv.server_close()
            for link in self.links:
                if link.is_symlink():
                    link.unlink()
            if self.path.exists():
                self.path.unlink()

    def stop(self) -> None:
        if self._srv is not None:
            self._srv.shutdown()
