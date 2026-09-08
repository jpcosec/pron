"""The ledger: one MoveDoc per turn, a document of the world (spec 07)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pron.world import LEDGER_DIR, World


class Ledger:
    def __init__(self, world: World):
        self.world = world
        self._prefix = ""
        self._n = 0

    def new_id(self, at: datetime) -> str:
        """move-<second>-<n>: n counts within the second and skips ids already in the store,
        so two sessions in the same second, or a restarted one, never collide."""
        prefix = f"move-{at.strftime('%Y%m%dT%H%M%S')}"
        if prefix != self._prefix:
            self._prefix, self._n = prefix, 0
        taken = {d.name for d in self.world.store.docs_of("MoveDoc") if d.name.startswith(prefix)} if "MoveDoc" in self.world.model_names() else set()
        self._n += 1
        while f"{prefix}-{self._n:03d}" in taken:
            self._n += 1
        return f"{prefix}-{self._n:03d}"

    def write(self, *, move_id: str, at: datetime, speaker: str, sentence: str, outcome: str, state_before: str, state_after: str,
              hash_before: str, hash_after: str, refers_to: str = "", record: dict[str, Any] | None = None) -> str:
        payload = {
            "id": move_id, "at": at.isoformat(), "speaker": speaker, "outcome": outcome,
            "state_before": state_before, "state_after": state_after, "hash_before": hash_before, "hash_after": hash_after,
            "refers_to": refers_to, "sentence": sentence, "record": json.loads(json.dumps(record or {}, default=str)),
        }
        path = self.world.root / LEDGER_DIR / f"{move_id}.md"
        return self.world.store.create("MoveDoc", move_id, payload, path)

    def last_with_write(self, speaker: str | None = None) -> dict[str, Any] | None:
        moves = [d for d in self.world.store.docs_of("MoveDoc") if d.payload.get("record", {}).get("writes")]
        if speaker:
            moves = [d for d in moves if d.payload.get("speaker") == speaker]
        moves.sort(key=lambda d: d.payload.get("at", ""))
        return dict(moves[-1].payload) if moves else None

    def about(self, address: str) -> list[dict[str, Any]]:
        """Moves that wrote on an address, oldest first."""
        out = []
        for d in self.world.store.docs_of("MoveDoc"):
            if any(w.get("address") == address for w in d.payload.get("record", {}).get("writes", [])):
                out.append(dict(d.payload))
        return sorted(out, key=lambda p: p.get("at", ""))

    def get(self, move_id: str) -> dict[str, Any] | None:
        d = self.world.store.doc("MoveDoc", move_id)
        return dict(d.payload) if d else None


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)
