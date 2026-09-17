"""Planning one part of a move (spec 06, 13): every noun resolved before anything runs.

Nothing is written until every part of the move has been planned, so a move that cannot
be carried out whole is never carried out half. A part with no nouns — `(undo)`,
`(refresh)`, `(why)` — plans to nothing; a composition plans its steps; anything else
resolves the phrase in each role it has, against the class that role needs. A create's
subject is the exception: it does not exist yet, so there is nothing to resolve, only its
required fields to check.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.part import Part
from pron.kernel.response import Response
from pron.sexpr.asker import Asker
from pron.sexpr.collaborator import Collaborator
from pron.sexpr.compose_planner import ComposePlanner
from pron.sexpr.phrase_planner import PhrasePlanner
from pron.sexpr.resolution import Resolution


class Planner(Collaborator):
    """A part's plan: what each of its roles resolved to, or the answer that stops it."""

    def __call__(
        self,
        part: Part,
        trace: list[str],
        record: dict[str, Any],
        pending: dict[str, str] | None = None,
    ) -> dict[str, Any] | Response:
        if part.kind in ("undo", "refresh", "why"):
            return {}
        if part.kind == "compose":
            return ComposePlanner(self.s)(part, trace, record, pending)
        plan = self._roles(part, trace, record, pending)
        if isinstance(plan, Response):
            return plan
        asked = self._create_data(part, record)
        return asked if asked is not None else plan

    def _roles(
        self,
        part: Part,
        trace: list[str],
        record: dict[str, Any],
        pending: dict[str, str] | None,
    ) -> dict[str, Any] | Response:
        """Subject first, then object: the first that cannot be resolved stops the part."""
        plan: dict[str, Any] = {}
        for role in ("subject", "object"):
            res = self._role(part, role, trace, record, pending)
            if isinstance(res, Response):
                return res
            if res is not None:
                plan[role] = res
        return plan

    def _role(
        self,
        part: Part,
        role: str,
        trace: list[str],
        record: dict[str, Any],
        pending: dict[str, str] | None,
    ) -> Resolution | Response | None:
        np = getattr(part, role)
        if np is None or _is_new_subject(part, role):
            return None  # a create's subject does not exist yet: nothing to resolve
        need_model = self.needed_model(part, role)
        res = PhrasePlanner(self.s)(np, need_model, trace, record, pending)
        if res.outcome == "ambiguo":
            return Asker(self.s).choice(part, role, res, record)
        if res.outcome == "missing":
            return Asker(self.s).missing(res, record)
        return res

    def _create_data(self, part: Part, record: dict[str, Any]) -> Response | None:
        """A create the sentence left incomplete asks for the first field it still needs."""
        if not _is_new_subject(part, "subject"):
            return None
        assert part.subject is not None and part.subject.model is not None
        missing = self.s.kernel.required_missing(
            part.subject.model, part.payload["fields"]
        )
        return Asker(self.s).data(part, missing[0], record) if missing else None

    # -- the class a role needs (spec 02, 05) --------------------------------------------

    def needed_model(self, part: Part, role: str) -> str | None:
        """What class this role has to be: a relation says it, an action's model says it."""
        if part.kind in ("read", "assert") and part.verb is not None and part.verb.relation:
            return self._relation_model(part.verb.relation, role)
        if part.kind == "action":
            return part.payload.get("model") or (part.verb.model if part.verb else None)
        return None

    def _relation_model(self, relation: str, role: str) -> str | None:
        rt = self.s.lex.relation_types.get(relation, {})
        types = rt.get("source_types" if role == "subject" else "target_types") or []
        return types[0] if types else None


def _is_new_subject(part: Part, role: str) -> bool:
    """The subject of a create: the document it names is the one it is about to make."""
    return (
        role == "subject"
        and part.kind == "action"
        and part.payload.get("verb") == "create"
    )
