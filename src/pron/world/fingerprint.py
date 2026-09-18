"""hash_mundo (spec 11 §5): the fingerprint of what the lexicon and the graph depend on —
every model but the ledger (name, version, hash_b, schema), the predicates, and the
linked stores — memoized by the store's own Merkle roots.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pron.world.doc_kind import ledger_model
from pron.world.store import Store


class WorldFingerprint:
    """hash_mundo of one store and the stores it links, recomputed only when they moved."""

    def __init__(self, store: Store) -> None:
        self.store = store
        self._cache: tuple[Any, str] | None = None

    def __call__(self) -> str:
        """Memoized by (local hash_a, every linked store's own hash_a): hash_a is already the
        store's Merkle root over every model's hash_b, so it alone says whether anything in
        `idx.models` could have moved since the last call — a turn that reads this several
        times (spec 11 §5, §_move, §_refresh) recomputes the expensive part (per-model
        schema) once, not once per read (PLAN 15 M4)."""
        idx = self.store.store_index()
        key = (
            idx.hash_a,
            tuple(sorted((s.name, self._linked_hash_a(s.name)) for s in idx.stores)),
        )
        cached = self._cache
        if cached is not None and cached[0] == key:
            return cached[1]
        value = self._uncached(idx)
        self._cache = (key, value)
        return value

    def _linked_hash_a(self, name: str) -> str | None:
        try:
            return self.store.store_index(name).hash_a
        except Exception:  # noqa: BLE001 - a missing linked store counts as absent
            return None

    def _uncached(self, idx: Any) -> str:
        parts: list[Any] = self._model_parts(idx)
        parts.append(sorted((p.name, p.axis) for p in idx.predicates))
        parts.append(sorted((s.name, s.path) for s in idx.stores))
        parts += [self._linked_part(s.name) for s in idx.stores]
        return hashlib.sha256(
            json.dumps(parts, sort_keys=True, default=str).encode()
        ).hexdigest()

    def _model_parts(self, idx: Any) -> list[Any]:
        parts: list[Any] = []
        ledger = ledger_model()
        for m in sorted(idx.models, key=lambda m: m.name):
            if m.name == ledger:
                continue
            mi = self.store.models_index(m.name)
            try:
                schema = self.store.schema(m.name)
            except Exception:  # noqa: BLE001 - an unresolvable model still counts by its hash
                schema = []
            parts.append([m.name, mi.version, mi.hash_b, schema])
        return parts

    def _linked_part(self, name: str) -> list[Any]:
        """A linked store's models move the lexicon of a projection over it."""
        try:
            return [
                name,
                sorted(
                    (m.name, self.store.models_index(m.name, name).hash_b)
                    for m in self.store.store_index(name).models
                ),
            ]
        except Exception:  # noqa: BLE001 - a missing linked store counts as absent
            return [name, None]
