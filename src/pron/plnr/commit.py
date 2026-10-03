"""Turning a plan that holds into the writes of the kernel (spec 04, 11 §7).

The plan comes back from the search over an overlay; nothing has been written. What the plan
promised is a list of pending forms — `(create MODEL doc)`, `(change doc field value)`,
`(assert REL src tgt)` — and each one is carried out by the same kernel verb a sentence
would use, with the same permissions, the same coercion and the same roundtrip. A plan is not
a second way to write; it is the same way, decided before the first write instead of during
it.

A create keeps the fields the plan sets on it in the same payload, because that is how sldb
wants a new document. Anything the kernel refuses raises StoreError, and whoever called this
decides what to say about the writes already done — pron does not undo by itself (spec 11 §7).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plnr import Plan

from pron.kernel.actions.write import Write
from pron.kernel.ids import join_id
from pron.sexpr.forms.syntax import unvalue
from pron.world.store_error import StoreError

if TYPE_CHECKING:
    from pron.kernel.kernel import Kernel
    from pron.plnr.pron_world import PronWorld


class Commit:
    """The writes of one plan, replayed in order."""

    def __init__(self, kernel: Kernel, world: PronWorld):
        self.kernel, self.world = kernel, world
        self.plan: Plan | None = None

    def __call__(self, plan: Plan) -> list[Write]:
        self.plan = plan
        return [self._one(form) for form in plan.writes]

    def _one(self, form: list[Any]) -> Write:
        head = str(form[0])
        if head == "create":
            return self._create(form)
        if head == "change":
            return self._change(form)
        if head == "assert":
            return self._assert(form)
        raise StoreError(f"a plan cannot write ({head} …)")

    def _create(self, form: list[Any]) -> Write:
        _, model, doc = (str(x) for x in form[:3])
        self._allows("create")
        payload = self._fields_of(doc)
        return self.kernel.create(model, payload, name=_name(doc))

    def _change(self, form: list[Any]) -> Write:
        _, doc, field, value = form[0], str(form[1]), str(form[2]), unvalue(form[3])
        self._allows("change")
        if _name(doc) in self._created:
            return _folded(
                self._id(doc), field, value
            )  # already in the create's payload
        self.kernel.expect(self._id(doc))
        return self.kernel.change(self._id(doc), field, value)

    def _assert(self, form: list[Any]) -> Write:
        relation, source, target = (str(x) for x in form[1:4])
        if "assert" not in self.world.lex.relation_types.get(relation, {}).get(
            "mode", "read"
        ):
            raise StoreError(f"in this session I can read {relation}, not assert it")
        _, export_id = self.world.verbs.assertion.assert_edge(
            relation, self._id(source), self._id(target)
        )
        return Write("assert", export_id, "relation_type", None, relation, True)

    def _allows(self, verb: str) -> None:
        if not self.kernel.allowed(verb):
            raise StoreError(f"in this session I cannot {verb}")

    # -- the fields a plan sets on a document it is creating --------------------------

    @property
    def _created(self) -> dict[str, str]:
        """The documents this plan creates, by name, with the model each one gets."""
        return {
            _name(str(f[2])): str(f[1]) for f in self._writes() if str(f[0]) == "create"
        }

    def _fields_of(self, doc: str) -> dict[str, Any]:
        return {
            str(f[2]): unvalue(f[3])
            for f in self._writes()
            if str(f[0]) == "change" and str(f[1]) == doc
        }

    def _writes(self) -> list[list[Any]]:
        assert self.plan is not None
        return list(self.plan.writes)

    def _id(self, doc: str) -> str:
        """The export id of a document: what the plan wrote, or the name of a document this
        same plan creates turned into an id — the model is the one its create declared."""
        if ":" in doc:
            return doc
        model = self._created.get(doc)
        if model is None:
            raise StoreError(f"the plan names {doc}, which it does not create")
        return join_id(self.kernel.write_store, model, doc)


def _name(doc: str) -> str:
    """The document's name inside its store: an export id minus its store and model, or the
    bare name a plan wrote when it does not care which model the document is."""
    return doc.split(":", 1)[1] if ":" in doc else doc


def _folded(doc: str, field: str, value: Any) -> Write:
    """A field the create already wrote: no second write, but the record says it happened."""
    return Write("change", doc, field, None, value, True, "in the create's payload")
