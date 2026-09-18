"""`_transitions/{Modelo}/{estado}` (spec 14 §2.3, spec 10 §2.5): the legal moves out of one
state of a model's status field — the `transitions_to` edges of the State document that
stands for it, each with its destination and its condition.
"""

from __future__ import annotations

from typing import Any

from pron.mcp.doc_entries import DocEntries
from pron.mcp.mount import Mount
from pron.world.doc_id import DocId
from pron.world.graph import bare, doc_id as node_of


class Transitions:
    """The transitions out of a state, read from the edge index."""

    def __init__(self, mount: Mount) -> None:
        self.mount = mount
        self.entries = DocEntries(mount)

    def __call__(self, model: str, state: str) -> dict[str, Any]:
        self.mount.require_model(model)
        out: list[dict[str, Any]] = []
        for doc_id, machine in self.states(model, state):
            for edge in self.mount.world.graph.edges_from(
                node_of(str(doc_id)), "transitions_to"
            ):
                out.append(self._row(machine, edge))
        notes = [] if out else [f"no transition declared out of {model} {state!r}"]
        return {"model": model, "from": state, "transitions": out, "notes": notes}

    def states(self, model: str, state: str) -> list[tuple[DocId, str]]:
        """The State documents whose machine is `{model}.field` and whose name is `state`."""
        found = []
        for record in self.mount.world.store.docs_of("State", "*"):
            machine = str(record.payload.get("machine", ""))
            if machine.startswith(f"{model}.") and record.payload.get("name") == state:
                found.append(
                    (DocId.of("State", record.name, record.store_name), machine)
                )
        return found

    def _row(self, machine: str, edge: dict[str, Any]) -> dict[str, Any]:
        target = DocId.parse(bare(edge["target"]))
        payload = self.mount.world.store.payload(target)
        return {
            "field": machine.split(".", 1)[1],
            "to": payload.get("name"),
            "state": self.entries.entry(target, payload),
            "condition": edge["metadata"].get("condition", ""),
        }
