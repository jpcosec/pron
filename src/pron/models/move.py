"""One move of the ledger: a whole turn, recorded as a document of the world (spec 07)."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from sldb import StructuredNLDoc


class MoveDoc(StructuredNLDoc):
    """A turn: who said what, how it was interpreted, what was asked of the world,
    what was written, what came out, and the world's fingerprint before and after.
    Tagged type.pron.move so kgdb's ingest leaves it out of the graph.
    """

    __family__ = "ledger"
    __semantics__ = {
        "type": ["pron", "move"],
        "workspace": ["knowledge", "ledger"],
    }
    __template__ = """---
id: ⸢rev•id⸥
at: ⸢rev•at⸥
speaker: ⸢rev•speaker⸥
outcome: ⸢rev•outcome⸥
state_before: ⸢rev•state_before⸥
state_after: ⸢rev•state_after⸥
hash_before: ⸢rev•hash_before⸥
hash_after: ⸢rev•hash_after⸥
refers_to: ⸢rev•refers_to⸥
---

# ⸢render•id⸥

## Sentence

⸢rev•sentence⸥

## Record

```yaml
⸢rev,dict•record⸥
```
""".strip()

    id: str = Field(
        description="Move id, move-<timestamp>-<n>; also the document name."
    )
    at: str = Field(description="When the move happened, ISO 8601 with timezone.")
    speaker: str = Field(
        default="",
        description="Who spoke: an opaque id and, when the speaker is an object of the world, its address.",
    )
    outcome: str = Field(
        description="unico | ambiguo | missing | externo | undo | error."
    )
    state_before: str = Field(
        description="Dialogue state before the move: libre or pendiente."
    )
    state_after: str = Field(description="Dialogue state after the move.")
    hash_before: str = Field(default="", description="hash_mundo before executing.")
    hash_after: str = Field(
        default="",
        description="hash_mundo after executing; equal to hash_before when nothing was written.",
    )
    refers_to: str = Field(
        default="",
        description="Id of the move this one answers, corrects or undoes; empty otherwise.",
    )
    sentence: str = Field(description="The sentence exactly as it came in.")
    record: dict[str, Any] = Field(
        default_factory=dict,
        description="The full record: interpretation, queries with their results, writes with previous and new values and whether done, edges read, candidates or neighbors, notes.",
    )
