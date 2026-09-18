"""Conditions evaluated with sldb (spec 03, 11 §7): a predicate whose `{field}` takes the
subject's values, run over the subject or over another document; over a payload a move has
not written yet when there is one; and, after a write, the conditions of a document's edges
that no longer hold.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from pron.kernel.ids import scope as _scope, split_id
from pron.sexpr.resolving.pending_match import pending_matches
from pron.world.doc_id import DocId

if TYPE_CHECKING:
    from pron.sexpr.resolving.edge_reader import EdgeReader

BRACE_RE = re.compile(r"\{([A-Za-z_][\w]*)\}")
Overlay = dict[str, dict[str, Any]]


class ConditionCheck:
    """Whether a condition holds, and which ones a write broke."""

    def __init__(self, store: Any, reader: EdgeReader):
        self.store, self.reader = store, reader

    def holds(
        self,
        condition: str,
        subject: str,
        over: str | None = None,
        overlay: Overlay | None = None,
    ) -> tuple[bool, str]:
        """Evaluate an sldb predicate. `{field}` takes the subject's values; the predicate runs over
        `over` (an export id) when given, else over the subject itself. `overlay` maps export ids
        to payloads a move has not written yet: those are read instead of the store, and the
        predicate over one of them goes through sldb's evaluator on that payload (spec 11 §7)."""
        if not condition.strip():
            return True, ""
        overlay = overlay or {}
        s_payload = overlay.get(subject) or self.store.payload(
            DocId.parse_plain(subject)
        )
        where = BRACE_RE.sub(lambda m: str(s_payload.get(m.group(1), "")), condition)
        target = over or subject
        if target in overlay:
            return self._pending(target, where, overlay[target])
        return self._stored(target, where)

    def _stored(self, target: str, where: str) -> tuple[bool, str]:
        t_store, t_model, t_doc = split_id(target)
        sc = _scope(t_store, t_model)
        found = self.store.find(sc, where)
        ok = any(a.endswith("}." + t_doc) for a in found)
        return ok, f"find '{sc}' --where '{where}'"

    def _pending(
        self, target: str, where: str, payload: dict[str, Any]
    ) -> tuple[bool, str]:
        t_store, t_model, t_doc = split_id(target)
        ok = (
            self.store.matches(DocId.parse_plain(target), where, payload)
            if t_doc != "$created"
            else pending_matches(self.store, t_model, where, payload, t_store)
        )
        return ok, f"where '{where}' over the pending payload of {target} (dry run)"

    def broken(self, export_id: str) -> list[str]:
        """Conditions of edges from and to a document that no longer hold."""
        edges = (
            self.reader.sldb("source_id", export_id, None).edges
            + self.reader.sldb("target_id", export_id, None).edges
        )
        return [
            f"{e['relation']} → {e['target']} requires {cond}, which no longer holds"
            for e in edges
            if (cond := e["metadata"].get("condition", ""))
            and not self.holds(cond, e["source"], over=e["target"])[0]
        ]
