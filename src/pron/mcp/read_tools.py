"""The read tools, level 0 (spec 14 §3): thin over the read plane, one method per tool. Their
signatures are the tools' input schemas and their docstrings what an agent reads of them.
"""

from __future__ import annotations

from typing import Any

from pron.mcp.read_plane import ReadPlane
from pron.mcp.tool_table import ToolTable

NAMES = ("worlds_list", "kb_get", "kb_find", "kb_read", "kb_neighbors")


class ReadTools:
    """worlds_list, kb_get, kb_find, kb_read, kb_neighbors."""

    def __init__(self, plane: ReadPlane) -> None:
        self.plane = plane

    def register(self, table: ToolTable) -> None:
        for name in NAMES:
            table.add(name, getattr(self, name), level=0)

    def worlds_list(self) -> dict[str, Any]:
        """The worlds of this server: name, root, projection and the models it names."""
        return self.plane.worlds_list()

    def kb_get(self, uri: str) -> dict[str, Any]:
        """Resolve any kb:// address: kb://{world}/{Model}[/{doc}[/{field}[/{i}]]] (literal),
        kb://{world}/[{Model}/]@{value} (a tag or enumerated value), @family/{family},
        @{Model:doc}/{relation}/~{relation}… (walks), selectors joined by & (intersection),
        kb://{world}/?{text} (ranked search), and _schema, _ledger/recent, _store/integrity,
        _transitions/{Model}/{state}. Every document comes with its literal address."""
        return self.plane.get(uri)

    def kb_find(
        self,
        world: str,
        model: str,
        where: list[str] | None = None,
        text: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Documents of a model (and its family) matching every sldb --where predicate in
        `where` (e.g. "capacity >= 6"); with `text`, ranked by similarity to it."""
        return self.plane.find(world, model, where, text, limit)

    def kb_read(self, world: str, id: str) -> dict[str, Any]:
        """One whole document by id, Model:doc (or store:Model:doc for a linked store)."""
        return self.plane.read(world, id)

    def kb_neighbors(
        self,
        world: str,
        id: str,
        relation: str | None = None,
        direction: str = "both",
    ) -> dict[str, Any]:
        """The edges of a document (direction out, in or both; optionally one relation), each
        with its origin, its condition and the other end's address."""
        return self.plane.neighbors(world, id, relation, direction)
