"""Transitive verbs (spec 03): read edges from kgdb with a fallback to the RelationDocs
in sldb; verify a verb against its RelationTypeDoc in sldb; evaluate conditions with
sldb over the subject; assert by creating a RelationDoc; transitions as guarded field
changes. pron never assembles edges.

`Verbs` is what the kernel, the display and the phases of a move hold; each concern is its
own class — `EdgeReader`, `RelationChecks`, `ConditionCheck`, `EdgeAssertion`, `StateMachine`.
"""

from __future__ import annotations

from typing import Any

from pron.sexpr.resolving.condition_check import ConditionCheck, Overlay
from pron.sexpr.resolving.edge_assertion import EdgeAssertion
from pron.sexpr.resolving.edge_read import EdgeRead
from pron.sexpr.resolving.edge_reader import EdgeReader
from pron.sexpr.resolving.relation_checks import RelationChecks
from pron.sexpr.resolving.state_machine import StateMachine
from pron.world.lexicon import Lexicon


class Verbs:
    def __init__(self, lex: Lexicon, write_store: str | None = None):
        self.lex = lex
        self.world = lex.world
        self.store = lex.world.store
        self.stores = list(lex.stores)  # where edges are looked for
        self.write_store = (
            write_store
            if write_store is not None
            else (None if lex.stores[0] == "local" else lex.stores[0])
        )  # where a new RelationDoc goes
        self.reader = EdgeReader(lex, self.stores)
        self.checks = RelationChecks(lex, self.reader)
        self.conditions = ConditionCheck(self.store, self.reader)
        self.assertion = EdgeAssertion(
            self.reader, self.checks, self.conditions, self.write_store
        )
        self.states = StateMachine(self.reader, self.conditions, self.stores)

    # -- reading ------------------------------------------------------------------------

    def edges_from(self, export_id: str, relation: str | None = None) -> EdgeRead:
        return self.reader.edges_from(export_id, relation)

    def edges_to(self, export_id: str, relation: str | None = None) -> EdgeRead:
        return self.reader.edges_to(export_id, relation)

    def _edges_sldb(self, side: str, export_id: str, relation: str | None) -> EdgeRead:
        return self.reader.sldb(side, export_id, relation)

    def targets_of(self, export_id: str, relation: str) -> list[str]:
        return [e["target"] for e in self.edges_from(export_id, relation).edges]

    # -- verifying ---------------------------------------------------------------------

    def relation_type(self, name: str) -> dict[str, Any]:
        return self.checks.relation_type(name)

    def applies(
        self, name: str, source_model: str, target_model: str
    ) -> tuple[bool, str]:
        return self.checks.applies(name, source_model, target_model)

    def cardinality_ok(self, name: str, source: str, target: str) -> tuple[bool, str]:
        return self.checks.cardinality_ok(name, source, target)

    def condition_holds(
        self,
        condition: str,
        subject: str,
        over: str | None = None,
        overlay: Overlay | None = None,
    ) -> tuple[bool, str]:
        return self.conditions.holds(condition, subject, over, overlay)

    # -- asserting -------------------------------------------------------------------

    def assert_edge(
        self, name: str, source: str, target: str, naming: str | None = None
    ) -> tuple[str, str]:
        return self.assertion.assert_edge(name, source, target, naming)

    def negate_edge(
        self, name: str, source: str, target: str
    ) -> tuple[str | None, str]:
        return self.assertion.negate_edge(name, source, target)

    # -- transitions ------------------------------------------------------------------------

    def machine(self, model: str, fld: str) -> dict[str, str]:
        return self.states.machine(model, fld)

    def transition(
        self,
        model: str,
        fld: str,
        subject: str,
        current: Any,
        new: Any,
        overlay: Overlay | None = None,
    ) -> tuple[bool, str, list[str]]:
        return self.states.transition(model, fld, subject, current, new, overlay)

    # -- re-evaluation after a write ----------------------------------------------------

    def broken_conditions(self, export_id: str) -> list[str]:
        return self.conditions.broken(export_id)
