"""A `kb://` address (spec 14 §2): the world it names and the path inside it, and which of
the planes reads that path — literal (§2.1), semantic (§2.2), ranked search (§3.3) or the
world's state (§2.3).
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import unquote

from pron.world.doc_id import DocId

SCHEME = "kb://"


def literal_uri(world: str, doc_id: DocId, *rest: str | int) -> str:
    """The literal address of a document, or of a field or item of it (spec 14 §2.1)."""
    model = doc_id.model if doc_id.store is None else f"{doc_id.store}:{doc_id.model}"
    return "/".join([f"{SCHEME}{world}", model, doc_id.name, *map(str, rest)])


@dataclass(frozen=True)
class KbUri:
    """`kb://{world}/{path}`, the path percent-decoded (a resource URI cannot carry a bare
    `?`, so `%3F` stands for it there)."""

    world: str
    path: str

    @staticmethod
    def parse(uri: str) -> "KbUri":
        if not uri.startswith(SCHEME):
            raise ValueError(f"not a kb:// address: {uri!r}")
        world, _, path = uri[len(SCHEME) :].partition("/")
        if not world:
            raise ValueError(f"a kb:// address names its world first: {uri!r}")
        return KbUri(world, unquote(path))

    @property
    def plane(self) -> str:
        """literal, semantic, search or state."""
        if self.path.startswith("?"):
            return "search"
        if self.path.startswith("_"):
            return "state"
        if self.path.startswith("@") or "/@" in self.path:
            return "semantic"
        return "literal"

    @property
    def segments(self) -> list[str]:
        return [s for s in self.path.split("/") if s]
