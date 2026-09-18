"""A projection: the part of a world one session can name (spec 01, 05)."""

from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator

from sldb import StructuredNLDoc

ACTIONS = ("create", "change", "add", "clean", "remove", "forget", "refresh", "undo")


class ProjectionDoc(StructuredNLDoc):
    """What a session can name and do: which stores, models, relation types (with
    read or read-and-assert mode), action verbs and aliases enter; how new documents
    are named, how objects are displayed, which field identifies them, how
    strict the approximate matching is, and how far its sessions may change the
    world (its level of mutability).
    """

    __family__ = "knowledge"
    __semantics__ = {
        "type": ["knowledge", "projection"],
        "workspace": ["knowledge", "projections"],
    }
    __template__ = """---
name: ⸢rev•name⸥
stores: ⸢rev•stores⸥
models: ⸢rev•models⸥
relations: ⸢rev•relations⸥
actions: ⸢rev•actions⸥
aliases: ⸢rev•aliases⸥
naming: ⸢rev•naming⸥
display: ⸢rev•display⸥
key: ⸢rev•key⸥
matching: ⸢rev•matching⸥
exposed: ⸢optrev•exposed⸥
mutability: ⸢optrev•mutability⸥
---

# ⸢render•name⸥

⸢rev•description⸥
""".strip()

    name: str = Field(
        description="Projection name; the document is named projection-<name>."
    )
    stores: list[str] = Field(
        default_factory=lambda: ["local"],
        description="Stores that enter: 'local' and names of linked stores.",
    )
    models: list[str] = Field(
        default_factory=list,
        description="Models that can be named; {Model+} families included. Empty means every model of the store.",
    )
    relations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Relation types that enter, each {name, mode} with mode 'read' or 'read and assert'. Empty means every type, read and assert.",
    )
    actions: list[str] = Field(
        default_factory=list,
        description="Kernel verbs allowed: create, change, add, clean, remove, forget, refresh, undo. Empty means none.",
    )
    aliases: list[str] = Field(
        default_factory=lambda: ["all"],
        description="Alias documents that enter, by symbol; 'all' means every AnchorDoc.",
    )
    naming: dict[str, str] = Field(
        default_factory=dict,
        description="Per model, how a new document is named, e.g. 'client-{name}'; without a rule pron asks.",
    )
    display: dict[str, str] = Field(
        default_factory=dict,
        description="Per model, how an object is shown, e.g. 'table {number}'; {rel.field} follows an edge.",
    )
    key: dict[str, str] = Field(
        default_factory=dict,
        description="Per model, the field that identifies an object by value, so 'table 12' is number = 12.",
    )
    matching: dict[str, Any] = Field(
        default_factory=lambda: {"neighbors": 3, "threshold": 0.55},
        description="Approximate matching: how many neighbors to offer and the minimum similarity.",
    )
    exposed: bool = Field(
        default=False,
        description="Whether sessions from other worlds may open this projection: the world's interface lexicon (spec 01, 12). Off, only the world's own clients can.",
    )
    mutability: int = Field(
        default=1,
        ge=0,
        le=3,
        description="How far a session of this projection may change its world (spec 14 §5): 0 reads, 1 documents and edges, 2 also relation types, 3 also models.",
    )
    description: str = Field(
        default="", description="Who this projection is for and what it leaves out."
    )

    @field_validator("exposed", mode="before")
    @classmethod
    def _absent_is_off(cls, v: Any) -> Any:
        """A projection written before the field existed has no `exposed` line: off."""
        return False if v is None or v == "" else v

    @field_validator("mutability", mode="before")
    @classmethod
    def _absent_is_content(cls, v: Any) -> Any:
        """A projection written before the field existed has no `mutability` line: level 1."""
        return 1 if v is None or v == "" else v
