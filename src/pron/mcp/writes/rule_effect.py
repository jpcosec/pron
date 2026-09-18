"""The simulated effect of editing a relation type (spec 14 §4, nivel 2): the guard of
`kb_rule_edit`. The type's authored edges are judged under the type as it is and as the
changes would leave it; an edge breaks when the new version finds something wrong with it
that the current one does not. Nothing is written.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.mcp.writes.rule_edges import RuleEdges
from pron.mcp.writes.rule_forms import RuleForms
from pron.mcp.writes.rule_judge import RuleJudge
from pron.world.doc_id import DocId

if TYPE_CHECKING:
    from pron.session import Session


class RuleEffect:
    """The edges a change to a relation type would break."""

    def __init__(self, session: Session):
        self.session = session
        self.edges, self.judge = RuleEdges(session), RuleJudge(session)

    def current(self, name: str) -> dict[str, Any] | None:
        """The RelationTypeDoc `rt-<name>` as it is, None when there is none."""
        doc = self.session.world.store.doc(DocId.parse(RuleForms.rule_id(name)))
        return None if doc is None else dict(doc.payload)

    def __call__(self, name: str, changes: dict[str, Any]) -> list[dict[str, Any]]:
        """`[{relation_doc, source, target, reasons}]`, in the order sldb finds them."""
        rule = self.current(name) or {}
        edges = self.edges(name)
        before = self.judge(rule, edges)
        after = self.judge({**rule, **changes}, edges)
        return [
            {
                "relation_doc": e["doc"],
                "source": e["source"],
                "target": e["target"],
                "reasons": new,
            }
            for e in edges
            if (
                new := [
                    r
                    for r in after.get(e["doc"], [])
                    if r not in before.get(e["doc"], [])
                ]
            )
        ]
