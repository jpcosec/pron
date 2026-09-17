"""The Session surface, answered by a running server instead of an open store (spec 11 §8,
12 §6, §7): turn(sentence) -> Response, plus the lexicon, the dialogue state and documents
by address."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pron.kernel.response import Response
from pron.remote.client import request
from pron.remote.remote_graph import RemoteGraph
from pron.remote.remote_world import RemoteWorld


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
