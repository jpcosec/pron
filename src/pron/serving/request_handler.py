"""One connection to the daemon (spec 11 §8): one JSON request per line, and its answer
written and flushed while the server still holds its lock, so the graph refresh settles
right after the client's bytes leave.
"""

from __future__ import annotations

import json
import socketserver
from typing import Any


class RequestHandler(socketserver.StreamRequestHandler):
    """Reads a request and hands it to `app` (a pron.serve.Server)."""

    app: Any = None

    @classmethod
    def bound_to(cls, app: Any) -> type["RequestHandler"]:
        """A handler class whose requests go to `app`."""
        return type("Handler", (cls,), {"app": app})

    def handle(self) -> None:
        line = self.rfile.readline()
        if not line:
            return
        try:
            req = json.loads(line)
        except ValueError as e:
            self._write({"ok": False, "error": f"bad request: {e}"})
            return
        self.app.handle(req, respond=self._respond)

    def _write(self, r: dict[str, Any]) -> None:
        self.wfile.write(
            json.dumps(r, default=str, ensure_ascii=False).encode("utf-8") + b"\n"
        )

    def _respond(self, r: dict[str, Any]) -> None:
        """The answer leaves while the server still holds its lock; the graph
        refresh settles right after these bytes (spec 11 §8)."""
        self._write(r)
        self.wfile.flush()
