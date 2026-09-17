"""Reading a relation (spec 03, 07): the edges of a document, and what they name.

`(targets rel NOUN)` reads the edges leaving the resolved subject and answers with their
targets; `(sources rel NOUN)` reads the edges arriving at the object and answers with their
sources. Neither side given is not a question anybody can answer. Whatever the read found
is narrowed by the predicates the sentence's extra modifiers left, noted as reads of the
move (spec 07), and remembered as the referent the next turn may say "them" about.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.ids import address_of
from pron.kernel.parts.part import Part
from pron.sexpr.resolving.edge_read import EdgeRead
from pron.sexpr.execution.listing import listing
from pron.sexpr.turn.note_reads import note_reads
from pron.sexpr.resolving.leftover_predicates import LeftoverPredicates
from pron.sexpr.resolving.predicate_filter import PredicateFilter

if TYPE_CHECKING:
    from pron.kernel.display import Display
    from pron.sexpr.dialogue.dialogue import Dialogue
    from pron.sexpr.resolving.verbs import Verbs
    from pron.sexpr.turn.move_context import MoveContext
    from pron.world.lexicon import Lexicon
    from pron.world.world import World


class ReadExecutor:
    """One relation read, answered."""

    def __init__(
        self,
        world: World,
        lex: Lexicon,
        verbs: Verbs,
        dialogue: Dialogue,
        display: Display,
    ):
        self.world, self.verbs, self.dialogue, self.display = (
            world,
            verbs,
            dialogue,
            display,
        )
        self.leftovers = LeftoverPredicates(world, lex)
        self.predicates = PredicateFilter(world, lex)

    def __call__(self, part: Part, plan: dict[str, Any], ctx: MoveContext) -> str:
        assert part.verb is not None and part.verb.relation is not None
        found = self._edges(part, plan, ctx)
        if found is None:
            return "I need to know whose."
        asked_np = self._asked_phrase(part)
        found = self._narrow(found, asked_np, part, ctx)
        addresses = [address_of(e) for e in dict.fromkeys(found)]
        note_reads(self.world, addresses, ctx.record)
        self.dialogue.remember(addresses, asked_np.model if asked_np else None)
        return listing(self.display, addresses)

    @staticmethod
    def _asked_phrase(part: Part):
        asked = part.payload.get("asked", "object")
        return part.subject if asked == "subject" else part.object

    # -- the edges themselves ------------------------------------------------------------

    def _edges(
        self, part: Part, plan: dict[str, Any], ctx: MoveContext
    ) -> list[str] | None:
        reads, side = self._reads(part, plan)
        if reads is None:
            return None
        found = [e[side] for r in reads for e in r.edges]
        for r in reads:
            self._note(r, ctx)
        return found

    def _reads(
        self, part: Part, plan: dict[str, Any]
    ) -> tuple[list[EdgeRead] | None, str]:
        """The edges from the subject (answering targets), or to the object (sources)."""
        assert part.verb is not None and part.verb.relation is not None
        rel = part.verb.relation
        if part.payload.get("asked", "object") == "object" and "subject" in plan:
            ids = plan["subject"].export_ids()
            return [self.verbs.edges_from(e, rel) for e in ids], "target"
        if "object" in plan:
            ids = plan["object"].export_ids()
            return [self.verbs.edges_to(e, rel) for e in ids], "source"
        return None, ""

    @staticmethod
    def _note(r: EdgeRead, ctx: MoveContext) -> None:
        ctx.trace.extend(r.queries)
        ctx.record["queries"].extend(r.queries)
        ctx.record["edges"].extend(r.edges)
        if r.source == "sldb":
            ctx.trace.append(
                "edges read from the RelationDocs in sldb: the graph is not fresh"
            )

    # -- the extra modifiers on the asked side -------------------------------------------

    def _narrow(
        self, found: list[str], asked_np, part: Part, ctx: MoveContext
    ) -> list[str]:
        predicates = self._predicates(part, asked_np)
        if asked_np is None or not predicates:
            return found
        return self.predicates(found, asked_np.model, predicates, ctx)

    def _predicates(self, part: Part, asked_np) -> list[str]:
        if "where" in part.payload:
            return part.payload["where"]
        if asked_np is None:
            return []
        return self.leftovers(asked_np, part.leftovers)
