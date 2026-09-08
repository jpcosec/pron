"""Serve a world: one process keeps the world, its caches and its sessions open behind a
Unix socket, and every local caller (the CLI, the REPL, kinesis) says its sentences
through it instead of opening the world again (spec 11 §8).

One request per connection, one JSON object per line. Requests are handled one at a
time: a world has one writer, and a turn is short. The server speaks as whoever the
client says it is; identity is the application's (spec 11 §6). The socket lives at
<world>/.pron/serve.sock; a client that finds no listener there opens the world itself.
The client side is pron.client, stdlib only.
"""

from __future__ import annotations

import json
import os
import socketserver
import threading
from pathlib import Path
from typing import Any

from pron.client import RemoteSession, alive, request, socket_path  # noqa: F401 - re-exported for callers of pron.serve
from pron.session import Session
from pron.world import World


class Server:
    def __init__(self, root: str | Path, pythonpath: str | None = None, sock: str | Path | None = None):
        self.world = World(root, pythonpath)
        self.path = Path(sock) if sock else socket_path(root)
        self.sessions: dict[tuple[str, str, bool], Session] = {}
        self.lock = threading.Lock()
        self._srv: socketserver.UnixStreamServer | None = None

    def handle(self, req: dict[str, Any]) -> dict[str, Any]:
        op = req.get("op", "say")
        with self.lock:
            try:
                return self._dispatch(op, req)
            except Exception as e:  # noqa: BLE001 - the answer says what the world refused; the server stays up
                return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    def _dispatch(self, op: str, req: dict[str, Any]) -> dict[str, Any]:
        if op == "ping":
            return {"ok": True, "world": str(self.world.root), "hash": self.world.hash_mundo(), "sessions": len(self.sessions), "pid": os.getpid()}
        if op == "say":
            r = self._session(req).turn(req["sentence"])
            return {"ok": True, "text": r.text, "outcome": r.outcome, "move": r.move_id, "trace": r.trace, "record": r.record}
        if op == "payload":
            return {"ok": True, "payload": self.world.store.payload(req["model"], req["doc"])}
        if op == "lexicon":
            return {"ok": True, "rows": self._session(req).lex.table(req.get("model"))}
        if op == "state":
            d = self._session(req).dialogue
            return {"ok": True, "state": d.state, "singular": d.singular, "set": d.last_set, "pending": d.pending.kind if d.pending else None}
        if op == "refresh":
            return {"ok": True, "report": self.world.refresh()}
        if op == "stop":
            threading.Thread(target=self.stop, daemon=True).start()
            return {"ok": True, "stopping": True}
        return {"ok": False, "error": f"unknown op {op!r}"}

    def _session(self, req: dict[str, Any]) -> Session:
        key = (req.get("projection", "all"), req.get("speaker", ""), bool(req.get("read_only", False)))
        if key not in self.sessions:
            self.sessions[key] = Session(self.world, projection=key[0], speaker=key[1], speaker_address=req.get("speaker_address"), now=req.get("now"), read_only=key[2])
        return self.sessions[key]

    def serve_forever(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
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
                self.wfile.write(json.dumps(resp, default=str, ensure_ascii=False).encode("utf-8") + b"\n")

        self._srv = socketserver.UnixStreamServer(str(self.path), Handler)
        try:
            self._srv.serve_forever()
        finally:
            self._srv.server_close()
            if self.path.exists():
                self.path.unlink()

    def stop(self) -> None:
        if self._srv is not None:
            self._srv.shutdown()
