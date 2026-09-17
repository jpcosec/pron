"""Undoing a recorded move (spec 11 §7): the inverses of its writes, newest first. Before
touching anything, a write whose document changed since the move (a different hash_c from
the one the move left) is skipped and named, and an inverse that would orphan a later
relation rejects the whole undo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.actions.verb_registry import VERBS
from pron.kernel.actions.write import Write
from pron.kernel.ids import split_relation_doc_id
from pron.world.store_error import StoreError

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.kernel.kernel import Kernel


class MoveUndo:
    """One undo of one move, through one kernel."""

    def __init__(self, kernel: "Kernel") -> None:
        self.kernel = kernel

    def __call__(self, move: dict[str, Any]) -> list[Write]:
        writes = [
            w
            for w in reversed(move.get("record", {}).get("writes", []))
            if w.get("done")
        ]
        out, todo = self._checked(writes, self._dropping(writes))
        for w in todo:
            self._invert(w, out)
        return out

    @staticmethod
    def _dropping(writes: list[dict[str, Any]]) -> set[str]:
        """The relation docs this undo untracks (by doc name, as the edge metadata names them):
        endpoints of those edges are not orphans."""
        return {
            rel[1]
            for w in writes
            if w["verb"] == "assert"
            and (rel := split_relation_doc_id(w["address"])) is not None
        }

    def _checked(
        self, writes: list[dict[str, Any]], dropping: set[str]
    ) -> tuple[list[Write], list[dict[str, Any]]]:
        """(the writes skipped because their document moved on, the writes to invert)."""
        out: list[Write] = []
        todo: list[dict[str, Any]] = []
        for w in writes:
            skipped = None if w["verb"] == "forget" else self._changed_since(w)
            if skipped is not None:
                out.append(skipped)
                continue
            if w["verb"] == "create":
                self._refuse_orphans(w["address"], dropping)
            todo.append(w)
        return out, todo

    def _changed_since(self, w: dict[str, Any]) -> Write | None:
        address = w["address"]
        left = w.get("hash_c")
        current = self._current_hash(address)
        if left and current and left != current:
            return Write(
                "undo",
                address,
                w.get("field"),
                None,
                None,
                done=False,
                note=f"{address} changed after that move; not touched",
            )
        return None

    def _current_hash(self, address: str) -> str:
        """The hash_c a document has now; a RelationDoc id carries a name with colons, so
        split_id cannot parse it and hash_c is asked directly (spec 03)."""
        rel = split_relation_doc_id(address)
        if rel is not None:
            return self.kernel.store.hash_c("RelationDoc", rel[1], rel[0])
        return self.kernel.store.hash_of(address)

    def _refuse_orphans(self, address: str, dropping: set[str]) -> None:
        dependents = [
            e
            for e in self.kernel.dependents(address)
            if e["metadata"].get("relation_doc") not in dropping
        ]
        if dependents:
            raise StoreError(
                f"undo would orphan {len(dependents)} relation(s) on {address}: "
                + ", ".join(
                    e["metadata"].get("relation_doc", e["relation"]) for e in dependents
                )
            )

    def _invert(self, w: dict[str, Any], out: list[Write]) -> None:
        verb, address = w["verb"], w["address"]
        self.kernel.expected_hash.pop(address, None)
        out.extend(self._inverse(w))
        if verb != "forget":
            self.kernel.warnings += self.kernel.verbs.broken_conditions(address)

    def _inverse(self, w: dict[str, Any]) -> list[Write]:
        v = VERBS.get(w["verb"])
        if v is not None:
            u = v.undo(self.kernel, w)
            return [] if u is None else [u]
        if w["verb"] in ("create", "assert"):
            return [self._untrack(w)]
        return []

    def _untrack(self, w: dict[str, Any]) -> Write:
        address = w["address"]
        rel = split_relation_doc_id(address)
        if rel is not None:
            self.kernel.store.untrack(rel[1], rel[0])
        else:
            self.kernel.store.untrack_of(address)
        return Write(
            "undo", address, None, w.get("after"), None, done=True, note="untracked"
        )
