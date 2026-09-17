"""Asserting a relation (spec 03, 11 §7): one RelationDoc per source × target pair.

The projection has to allow asserting this relation and not only reading it — the same
check the pre-validation already made, made again here because this is the last thing
before the write. Each edge is a document created in sldb, recorded in the move so undo
can take it back, and said out loud as the sentence it is.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.part import Part
from pron.world.store_error import StoreError

if TYPE_CHECKING:
    from pron.kernel.display import Display
    from pron.sexpr.dialogue.dialogue import Dialogue
    from pron.sexpr.execution.relation_write import EdgeWriter
    from pron.sexpr.turn.move_context import MoveContext
    from pron.world.lexicon import Lexicon


class AssertExecutor:
    """The edges one assert part writes."""

    def __init__(
        self, lex: Lexicon, display: Display, dialogue: Dialogue, edges: EdgeWriter
    ):
        self.lex, self.display, self.dialogue, self.edges = (
            lex,
            display,
            dialogue,
            edges,
        )

    def __call__(self, part: Part, plan: dict[str, Any], ctx: MoveContext) -> str:
        assert part.verb is not None and part.verb.relation is not None
        rel = part.verb.relation
        self._allowed(rel)
        texts = self._edges(rel, plan, ctx)
        subject = plan["subject"]
        self.dialogue.remember(subject.addresses, subject.phrase.model)
        return "Done: " + "; ".join(texts) + "."

    def _allowed(self, rel: str) -> None:
        mode = self.lex.relation_types.get(rel, {}).get("mode", "read")
        if "assert" not in mode:
            raise StoreError(
                f"in this session I can tell you about {rel}, not assert it"
            )

    def _edges(self, rel: str, plan: dict[str, Any], ctx: MoveContext) -> list[str]:
        return [
            self._edge(rel, s, t, ctx)
            for s in plan["subject"].export_ids()
            for t in plan["object"].export_ids()
        ]

    def _edge(self, rel: str, s: str, t: str, ctx: MoveContext) -> str:
        self.edges(rel, s, t, ctx)
        name = self.display.name
        return f"{name(s)} {rel.replace('_', ' ')} {name(t)}"
