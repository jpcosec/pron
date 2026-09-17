"""Why a document is the way it is (spec 07): the ledger, and the edges that ground it.

The ledger knows the last move that wrote this document: who said what, when, and which
fields it moved; the checks that move's trace kept — a transition, a condition — are worth
repeating, because they are the reason the write was allowed. The graph knows the edges on
the WHY and PROVENANCE axes, which are the reason someone gave. Without a document named,
the question is about whatever was last written or last talked about.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.ids import address_of
from pron.kernel.parts.part import Part
from pron.sexpr.turn.collaborator import Collaborator
from pron.sexpr.resolving.resolution import address_to_export_id


class WhyExecutor(Collaborator):
    """What the ledger and the graph say about one document."""

    def __call__(self, part: Part, trace: list[str], record: dict[str, Any]) -> str:
        target = self.target(part)
        if not target:
            return "Why what? Say something first."
        bits = self._from_ledger(target, trace)
        bits += self._from_edges(target, record)
        return (" · ".join(bits) or f"No record explains {target}.") + "."

    def target(self, part: Part) -> str | None:
        """The document named, or the last one written, or the last one talked about."""
        if "target" in part.payload:
            return part.payload["target"]
        return self.s.dialogue.last_written or (
            self.s.dialogue.last_singular
            and address_to_export_id(self.s.dialogue.last_singular)
        )

    def _from_ledger(self, target: str, trace: list[str]) -> list[str]:
        moves = self.s.ledger.about(target)
        if not moves:
            return []
        m = moves[-1]
        trace.append(f"ledger: {m['id']}")
        return [_because(m, target), *_checks(m)]

    def _from_edges(self, target: str, record: dict[str, Any]) -> list[str]:
        why_edges = self._why_edges(target)
        record["edges"].extend(why_edges)
        if not why_edges:
            return []
        grounds = ", ".join(
            self.s.display.name(address_of(e["target"])) for e in why_edges
        )
        return ["grounded by " + grounds]

    def _why_edges(self, target: str) -> list[dict[str, Any]]:
        """The edges leaving the document on the WHY and PROVENANCE axes."""
        return [
            e
            for e in self.s.verbs.edges_from(target).edges
            if e["metadata"].get("axis") in ("WHY", "PROVENANCE")
        ]


def _because(m: dict[str, Any], target: str) -> str:
    w = [x for x in m["record"].get("writes", []) if x.get("address") == target]
    what = ", ".join(
        f"{x.get('field') or x['verb']}: {x.get('before')!r} → {x.get('after')!r}"
        for x in w
    )
    return (
        f'Because of "{m["sentence"]}" ({m["speaker"] or "someone"}, {m["at"]}): {what}'
    )


def _checks(m: dict[str, Any]) -> list[str]:
    """The lines of that move's trace that say why the write was allowed."""
    return [
        line
        for line in m["record"].get("trace", [])
        if "transition" in line or "condition" in line or "legal" in line
    ]
