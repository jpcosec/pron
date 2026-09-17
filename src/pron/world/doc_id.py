"""The id of one document, with the store it belongs to (spec 02, 12 §5).

An export id is `Model:doc` for a document of the local store and `store:Model:doc` for
one of a store linked into it; an address is `st.{Model}.doc` or `store:st.{Model}.doc`
(sldb's own prefix form). `None` and "local" both mean the local store. A `DocId` holds
the three parts apart, so nothing downstream splits a string to learn them — and a
RelationDoc, whose name embeds the ids of its two ends (colons), reads back whole.

This module imports nothing of pron: `pron.kernel.ids` is written over it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

LOCAL = "local"
RELATION_MODEL = "RelationDoc"
_RELATION_ID = re.compile(rf"(?:([^:]+):)?{RELATION_MODEL}:(.+)")


def is_local(store: str | None) -> bool:
    return store is None or store == LOCAL


@dataclass(frozen=True)
class DocId:
    """`store:Model:name`, its parts apart; `store` is None for the local store."""

    store: str | None
    model: str
    name: str

    def __post_init__(self) -> None:
        if self.store == LOCAL:
            object.__setattr__(self, "store", None)

    @staticmethod
    def of(model: str, name: str, store: str | None = None) -> "DocId":
        """From the `(model, name, store)` every store method used to take."""
        return DocId(store, model, name)

    @staticmethod
    def parse(export_id: str) -> "DocId":
        """'A:Model:doc' or 'Model:doc'; a RelationDoc's id keeps the colons of its name."""
        relation = DocId.parse_relation(export_id)
        return relation if relation is not None else DocId.parse_plain(export_id)

    @staticmethod
    def parse_plain(export_id: str) -> "DocId":
        """The split at the first two colons, blind to the model: right for every id whose
        name carries no colon, which is every id but a RelationDoc's."""
        parts = export_id.split(":", 2)
        if len(parts) == 3:
            return DocId(parts[0], parts[1], parts[2])
        if len(parts) == 2:
            return DocId(None, parts[0], parts[1])
        raise ValueError(f"not an export id: {export_id!r}")

    @staticmethod
    def parse_relation(export_id: str) -> "DocId | None":
        """The id of a RelationDoc ('RelationDoc:{name}', 'A:RelationDoc:{name}'), or None
        when it is not one. The store prefix carries no colon, so the match is unambiguous."""
        m = _RELATION_ID.fullmatch(export_id)
        return None if m is None else DocId(m.group(1), RELATION_MODEL, m.group(2))

    @staticmethod
    def from_address(address: str) -> "DocId":
        """st.{Model}.doc, A:st.{Model+}.doc, or an export id passing through."""
        if address.startswith("st.{"):
            model, name = address[4:].split("}.", 1)
            return DocId(None, model.rstrip("+"), name)
        if ":st.{" in address:
            store, rest = address.split(":", 1)
            return DocId.from_address(rest).in_store(store)
        return DocId.parse(address)

    def __str__(self) -> str:
        local = f"{self.model}:{self.name}"
        return local if self.store is None else f"{self.store}:{local}"

    @property
    def is_local(self) -> bool:
        return self.store is None

    @property
    def address(self) -> str:
        a = f"st.{{{self.model}}}.{self.name}"
        return a if self.store is None else f"{self.store}:{a}"

    def in_store(self, store: str | None) -> "DocId":
        return DocId(store, self.model, self.name)

    def relativize(self, store: str | None) -> "DocId":
        """The id as the documents of `store` write it: a document of that same store carries
        no prefix, so the store reads its own documents the same alone and through a daemon."""
        same = self.store is not None and self.store == store
        return self.in_store(None) if same else self

    def qualify(self, store: str | None) -> "DocId":
        """The id as a session that links `store` names it: an unprefixed id read from a
        document of that store belongs to that store."""
        return self.in_store(store) if self.store is None else self
