"""The read plane of the MCP surface as a library (spec 14 §2, §3): every `kb://` address and
every read tool, over the mounted worlds, bounded by their projection. Reads go by address
(spec 12 §4, §5): no form, no MoveDoc.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pron.mcp.doc_entries import DocEntries
from pron.mcp.finder import Finder
from pron.mcp.kb_uri import KbUri
from pron.mcp.literal_reads import LiteralReads
from pron.mcp.mount import Mount
from pron.mcp.neighbors import Neighbors
from pron.mcp.page import SEARCH_LIMIT, Page
from pron.mcp.ranked_search import RankedSearch
from pron.mcp.semantic_reads import SemanticReads
from pron.mcp.world_mounts import WorldMounts
from pron.mcp.world_state import WorldState
from pron.world.doc_id import DocId

Plane = Callable[[Mount], Callable[[list[str]], dict[str, Any]]]
PLANES: dict[str, Plane] = {
    "literal": LiteralReads,
    "semantic": SemanticReads,
    "state": WorldState,
}


class ReadPlane:
    """Reads over a server's worlds, each answer a JSON-safe dict."""

    def __init__(self, mounts: WorldMounts) -> None:
        self.mounts = mounts
        self._search: dict[str, RankedSearch] = {}

    def worlds_list(self) -> dict[str, Any]:
        return {"worlds": [self.mounts[n].summary() for n in self.mounts.names()]}

    def get(
        self, uri: str, limit: int | None = None, offset: int = 0
    ) -> dict[str, Any]:
        """Any address of spec 14 §2, the same read as the resource of that URI; a set comes
        paged (the ten best of a search, fifty of any other set)."""
        address, page = KbUri.parse(uri), Page(limit, offset)
        mount = self.mounts[address.world]
        mount.world.store.begin_operation()
        if address.plane == "search":
            answer = self.search(address.world, address.path[1:], page)
        elif not address.segments:
            answer = {"world": mount.summary()}
        else:
            answer = page.cut(PLANES[address.plane](mount)(address.segments))
        return {"uri": uri, "world": address.world, **answer}

    def search(
        self, world: str, text: str, page: Page, among: list[str] | None = None
    ) -> dict[str, Any]:
        """Ranked search (spec 14 §3.3), the ten best unless the page says otherwise."""
        if world not in self._search:
            self._search[world] = RankedSearch(self.mounts[world])
        return page.cut(self._search[world](text, among), SEARCH_LIMIT)

    def find(
        self,
        world: str,
        model: str,
        where: list[str] | None = None,
        text: str | None = None,
        page: Page = Page(),
    ) -> dict[str, Any]:
        """Documents of a model (and its family) by sldb predicates, intersected (spec 02);
        with `text`, ranked (spec 14 §3.3)."""
        ids = Finder(self.mounts[world])(model, where or [])
        if text:
            return {"world": world, **self.search(world, text, page, ids)}
        entries = DocEntries(self.mounts[world])
        rows = [entries.entry(DocId.parse(i)) for i in ids]
        return {"world": world, "model": model, **page.cut({"documents": rows})}

    def read(self, world: str, id: str) -> dict[str, Any]:
        """The whole document by id (`Modelo:doc`)."""
        mount = self.mounts[world]
        mount.world.store.begin_operation()
        doc_id = mount.require(DocId.parse(id))
        return {"world": world, **LiteralReads(mount).document(doc_id)}

    def neighbors(
        self,
        world: str,
        id: str,
        relation: str | None = None,
        direction: str = "both",
    ) -> dict[str, Any]:
        mount = self.mounts[world]
        return {"world": world, **Neighbors(mount)(id, relation, direction)}
