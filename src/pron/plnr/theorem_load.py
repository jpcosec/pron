"""The theorems of a world, read from its TheoremDoc documents (spec 03, 13).

The rules of a world are documents of that world, so they are read here and nowhere else:
no rule of any world lives in the code that runs the search. A store without TheoremDoc —
or with none of them — searches with the primitives alone.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from plnr import Theorem, TheoremError, Theorems, read_all, read_one

from pron.world.doc_id import DocId

if TYPE_CHECKING:
    from pron.world.world import World

MODEL = "TheoremDoc"


class TheoremLoad(ValueError):
    """A TheoremDoc that is not a usable rule."""


def load_theorems(world: World, store: str | None = None) -> Theorems:
    """Every rule of the world, in the order the store hands them back, so applying them is
    deterministic."""
    theorems = Theorems()
    if MODEL not in world.model_names(store):
        return theorems
    for doc in world.store.docs_of(MODEL, store):
        try:
            theorems.add(_theorem(doc.name, doc.payload))
        except TheoremError as e:
            raise TheoremLoad(f"{doc.name}: {e}") from e
    return theorems


def _theorem(name: str, payload: dict) -> Theorem:
    pattern = read_one(str(payload.get("pattern") or ""))
    body = tuple(read_all(str(payload.get("body") or "")))
    return Theorem(
        name=str(payload.get("name") or name.removeprefix("theorem-")),
        kind=str(payload.get("kind") or ""),
        pattern=pattern,
        body=body,
        source=f"{MODEL}:{name}",
    )


def theorem_doc(
    name: str, kind: str, pattern: str, body: str, motive: str = ""
) -> DocId:
    """Where a rule is written, for whoever declares one."""
    return DocId.of(MODEL, f"theorem-{name}")
