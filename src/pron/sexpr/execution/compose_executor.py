"""Doing a composition (spec 05, 11 §7): several writes said as one word.

The steps run in the order the alias declares them and each may name what an earlier one
made, as `$created`; naming it before anything created it is a malformed declaration and
stops the composition before it asks the store for anything. The create runs first in
practice, and it is told what it is about to be related to, because the naming template of
the new document may name it (spec 04). The answer is composed at the end, once every
relation exists: "Created reservation for Ana, on the terrace, for Friday."
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.ids import address_of, model_of
from pron.kernel.parts.part import Part
from pron.kernel.actions.write import Write
from pron.world.doc_id import DocId
from pron.world.store_error import StoreError

if TYPE_CHECKING:
    from pron.kernel.display import Display
    from pron.kernel.kernel import Kernel
    from pron.sexpr.dialogue.dialogue import Dialogue
    from pron.sexpr.execution.relation_write import EdgeWriter
    from pron.sexpr.turn.move_context import MoveContext
    from pron.world.world import World

BEFORE_CREATE = "composition references $created before create"


class ComposeExecutor:
    """A composition's steps, written in order, and the one sentence they add up to."""

    def __init__(
        self,
        kernel: Kernel,
        world: World,
        display: Display,
        dialogue: Dialogue,
        edges: EdgeWriter,
    ):
        self.kernel, self.world, self.edges = kernel, world, edges
        self.display, self.dialogue = display, dialogue

    def __call__(self, part: Part, plan: dict[str, Any], ctx: MoveContext) -> str:
        assert part.verb is not None
        self.part, self.plan, self.ctx = part, plan, ctx
        self.steps = part.verb.payload.get("steps", [])
        self.literals = {k: v for k, v in part.payload.items() if not k.startswith("_")}
        self.created: str | None = None
        self.texts: list[str] = []
        for step, resolved in zip(self.steps, plan["steps"]):
            self._step(step, resolved)
        return self._answer()

    def _step(self, step: dict[str, Any], resolved: dict[str, Any]) -> None:
        fn = getattr(self, "_do_" + str(step.get("do")), None)
        if fn is not None:
            fn(step, resolved)

    def _side(
        self, step: dict[str, Any], resolved: dict[str, Any], key: str
    ) -> str | None:
        """`$created` is what this composition made, if it has made it yet."""
        if step.get(key) == "$created":
            return self.created
        return resolved[key].export_ids()[0]

    # -- create ---------------------------------------------------------------------------

    def _do_create(self, step: dict[str, Any], resolved: dict[str, Any]) -> None:
        model = step["model"]
        fields, related = self._fields(model), self._related()
        self._require(model, fields)
        name = self.part.payload.get("_name")
        w = self.kernel.create(model, fields, related, name=name)
        self._note_created(model, w)

    def _fields(self, model: str) -> dict[str, Any]:
        names = {f["name"] for f in self.kernel.schema(model)}
        return {k: v for k, v in self.literals.items() if k in names}

    def _related(self) -> dict[str, Any]:
        """What the new document will be related to, for its naming template (spec 04)."""
        related: dict[str, Any] = {}
        for later, later_res in zip(self.steps, self.plan["steps"]):
            if _asserts_from_created(later, later_res):
                tid = DocId.parse_plain(later_res["target"].export_ids()[0])
                related[later["relation"]] = self.world.store.payload(tid)
        return related

    def _require(self, model: str, fields: dict[str, Any]) -> None:
        missing = self.kernel.required_missing(model, fields)
        if missing:
            raise StoreError(f"{model} needs {', '.join(missing)}")

    def _note_created(self, model: str, w: Write) -> None:
        self.created = w.address
        self.ctx.trace.append(f"docs create --model {model} {self.created} {w.after}")
        self.ctx.record["writes"].append(w.record())
        self.texts.append(model.lower())  # named at the end, once its relations exist

    # -- assert and change -----------------------------------------------------------------

    def _do_assert(self, step: dict[str, Any], resolved: dict[str, Any]) -> None:
        src = self._side(step, resolved, "source")
        tgt = self._side(step, resolved, "target")
        if src is None or tgt is None:
            raise StoreError(BEFORE_CREATE)
        rel = step["relation"]
        self.edges(rel, src, tgt, self.ctx)
        self.texts.append(f"{rel.replace('_', ' ')} {self.display.name(tgt)}")

    def _do_change(self, step: dict[str, Any], resolved: dict[str, Any]) -> None:
        tgt = self._side(step, resolved, "target")
        if tgt is None:
            raise StoreError(BEFORE_CREATE)
        w = self.kernel.change(tgt, step["field"], step["value"])
        self.ctx.record["writes"].append(w.record())

    # -- what it all said --------------------------------------------------------------------

    def _answer(self) -> str:
        if not self.created:
            return "Done: " + "; ".join(self.texts) + "."
        model, addr = model_of(self.created), address_of(self.created)
        self.texts[0] = f"{model.lower()} {self.display.name(addr)}"
        self.dialogue.remember([addr], model)
        self.dialogue.last_written = self.created
        return f"Created {self.texts[0]}{self._rest()}." + self._also()

    def _rest(self) -> str:
        return ", " + ", ".join(self.texts[1:]) if len(self.texts) > 1 else ""

    def _also(self) -> str:
        """A slot that took any one of several documents says which other would have done."""
        alt = [
            r
            for r in self.plan["steps"]
            for k, r in r.items()
            if k == "target" and r.candidates and r.note.startswith("any")
        ]
        if not alt:
            return ""
        name = self.display.names(alt[0].candidates)[0]
        return f" {name.capitalize()} would also work."


def _asserts_from_created(step: dict[str, Any], resolved: dict[str, Any]) -> bool:
    return (
        step.get("do") == "assert"
        and step.get("source") == "$created"
        and "target" in resolved
    )
