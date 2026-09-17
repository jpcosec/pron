"""The client of a running `pron serve` (spec 11 §8): stdlib only, so `pron say` through a
server costs a process start and a socket round trip, not sldb's imports. A request is one
connection, one JSON object per line."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any

SOCKET_RELPATH = Path(".pron") / "serve.sock"
MAX_SOCKET_PATH = 100  # AF_UNIX paths are capped around 108 bytes on Linux


def socket_path(root: str | Path) -> Path:
    """<world>/.pron/serve.sock, or, when that path is too long for a Unix socket, a short
    one in the temp dir named by a hash of the world's root (server and clients agree)."""
    root = Path(root).resolve()
    path = root / SOCKET_RELPATH
    if len(str(path).encode("utf-8")) <= MAX_SOCKET_PATH:
        return path
    import hashlib
    import tempfile

    return (
        Path(tempfile.gettempdir())
        / f"pron-{hashlib.sha1(str(root).encode('utf-8')).hexdigest()[:12]}.sock"
    )


def request(
    path: str | Path, req: dict[str, Any], timeout: float = 600.0
) -> dict[str, Any]:
    """One request to a running server. Raises ConnectionError when nobody listens."""
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect(str(path))
        except OSError as e:
            raise ConnectionError(f"no pron server at {path}: {e}") from e
        s.sendall(json.dumps(req, ensure_ascii=False).encode("utf-8") + b"\n")
        chunks = []
        while True:
            chunk = s.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
            if chunk.endswith(b"\n"):
                break
    resp = json.loads(b"".join(chunks).decode("utf-8"))
    if not resp.get("ok"):
        raise RuntimeError(resp.get("error", "the server refused"))
    return resp


def alive(path: str | Path) -> bool:
    """Whether a server answers at that socket."""
    if not Path(path).exists():
        return False
    try:
        return bool(request(path, {"op": "ping"}, timeout=5.0).get("ok"))
    except (ConnectionError, RuntimeError, OSError, ValueError):
        return False
