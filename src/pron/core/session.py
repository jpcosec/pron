"""Clarification session. Implements atom-session-expires-by-ttl-and-store-hash.

One pending expression at a time, persisted in .knowledge/session.json under
the cwd, discarded after 15 minutes or when the store's hash_a changes.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

TTL_SECONDS = 15 * 60
SESSION_RELPATH = ".knowledge/session.json"


class Session:
    """Persisted pending-clarification state."""

    def __init__(self, root: Path, store_hash: str) -> None:
        self.path = Path(root) / SESSION_RELPATH
        self.store_hash = store_hash

    def load(self) -> dict | None:
        """The pending state, or None if absent/expired/invalidated."""
        if not self.path.exists():
            return None
        data = json.loads(self.path.read_text())
        expired = time.time() - data.get("created_at", 0) > TTL_SECONDS
        invalidated = data.get("store_hash") != self.store_hash
        if expired or invalidated:
            self.clear()
            return None
        return data

    def save(self, pending_sexpr: str, candidates: list[str]) -> None:
        """Persist one pending expression (replaces any previous one)."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {
                    "pending_sexpr": pending_sexpr,
                    "candidates": candidates,
                    "created_at": time.time(),
                    "store_hash": self.store_hash,
                },
                indent=1,
            )
        )

    def clear(self) -> None:
        """Drop the pending state."""
        self.path.unlink(missing_ok=True)
