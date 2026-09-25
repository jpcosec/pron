"""Methods of the server's World or Graph, by name, over the socket (spec 11 §8, 12 §5, §7):
one call becomes one request, keyword arguments only, and the result is whatever the server
answered."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pron.remote.client import request, tcp_address


class _Remote:
    """Methods of the server's World or Graph, by name, over the socket (spec 12 §5, §7)."""

    op = ""

    def __init__(self, path: str | Path, base: dict[str, Any] | None = None):
        self.path = path if tcp_address(path) else Path(path)
        self.base = dict(base or {})

    def call(self, method: str, **args: Any) -> Any:
        return request(
            self.path, {"op": self.op, **self.base, "method": method, "args": args}
        )["result"]

    def __getattr__(self, method: str) -> Any:
        if method.startswith("_"):
            raise AttributeError(method)
        return lambda **args: self.call(method, **args)
