"""The client of a running `pron serve` (spec 11 §8): stdlib only, so `pron say` through a
server costs a process start and a socket round trip, not sldb's imports. A request is one
connection, one JSON object per line."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any

from pron.response import Response

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


class RemoteSession:
    """The Session surface a caller uses, answered by a running server: turn(sentence) ->
    Response, plus the lexicon, the dialogue state and documents by address."""

    def __init__(
        self,
        path: str | Path,
        projection: str = "all",
        speaker: str = "",
        speaker_address: str | None = None,
        now: str | None = None,
        read_only: bool = False,
        world: str | Path | None = None,
        home: str | Path | None = None,
    ):
        """world: which of the server's worlds to speak to (name or root; the server's default
        when None). home: the caller's own world; when it differs from `world`, only that
        world's exposed projections open (spec 12 §6)."""
        self.path = Path(path)
        self.base = {
            "projection": projection,
            "speaker": speaker,
            "speaker_address": speaker_address,
            "now": now,
            "read_only": read_only,
            "world": str(world) if world is not None else None,
            "home": str(home) if home is not None else None,
        }

    def _ask(self, op: str, **fields: Any) -> dict[str, Any]:
        return request(self.path, {"op": op, **self.base, **fields})

    def turn(self, sentence: str) -> Response:
        r = self._ask("say", sentence=sentence)
        return Response(
            r["text"],
            r["outcome"],
            list(r.get("trace", [])),
            r.get("move", ""),
            r.get("record", {}),
        )

    def eval(self, forms: str) -> Response:
        """One move written as forms (spec 13): same checks, writes, MoveDoc and undo as a sentence."""
        r = self._ask("eval", forms=forms)
        return Response(
            r["text"],
            r["outcome"],
            list(r.get("trace", [])),
            r.get("move", ""),
            r.get("record", {}),
        )

    def lexicon(self, model: str | None = None) -> list[dict[str, str]]:
        return list(self._ask("lexicon", model=model)["rows"])

    def state(self) -> dict[str, Any]:
        return self._ask("state")

    def payload(self, model: str, doc: str) -> dict[str, Any]:
        """A document by address, refused when its model is outside this session's projection."""
        return dict(self._ask("payload", model=model, doc=doc)["payload"])

    def close(self) -> bool:
        """Drop this dialogue in the server; the next turn starts a fresh one."""
        return bool(self._ask("close")["closed"])

    @property
    def graph(self) -> "RemoteGraph":
        return RemoteGraph(self.path, self.base)

    @property
    def world(self) -> "RemoteWorld":
        return RemoteWorld(self.path, self.base)


class _Remote:
    """Methods of the server's World or Graph, by name, over the socket (spec 12 §5, §7)."""

    op = ""

    def __init__(self, path: str | Path, base: dict[str, Any] | None = None):
        self.path = Path(path)
        self.base = dict(base or {})

    def call(self, method: str, **args: Any) -> Any:
        return request(
            self.path, {"op": self.op, **self.base, "method": method, "args": args}
        )["result"]

    def __getattr__(self, method: str) -> Any:
        if method.startswith("_"):
            raise AttributeError(method)
        return lambda **args: self.call(method, **args)


class RemoteGraph(_Remote):
    """The Graph methods of spec 12 §5 (`edges_from(node_id=...)`, `targets(node_id=..., relation=...)`, ...), keyword arguments only."""

    op = "graph"


class RemoteWorld(_Remote):
    """`model_names()`, `family_of(name=...)`, `relation_types()`, `projection(name=...)`, `hash_mundo()`, `model_hashes()`, `graph_is_fresh()`."""

    op = "world"
