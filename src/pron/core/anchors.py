"""Anchor registry: symbol -> {kind, ref, motive} from tracked AnchorDocs.

Implements atom-the-anchor-table-is-declared-as-sldb-documents-not-code and
atom-unanchored-symbols-fail-with-an-explicit-semantic-error.
"""

from __future__ import annotations

from dataclasses import dataclass

from pron.bridges.sldb_bridge import SldbBridge
from pron.core.results import SemanticError

KINDS = ("model", "doc", "relation", "operation", "projection")


@dataclass(frozen=True)
class Anchor:
    """One resolved grammar symbol."""

    symbol: str
    kind: str
    ref: str
    motive: str


class AnchorRegistry:
    """Loads AnchorDocs from the store; never invents anchors."""

    def __init__(self, bridge: SldbBridge) -> None:
        self._bridge = bridge
        self._table: dict[str, Anchor] | None = None

    def _load(self) -> dict[str, Anchor]:
        if self._table is None:
            self._table = {}
            for doc in self._bridge.documents_of_model("AnchorDoc"):
                p = doc.payload
                self._table[p["symbol"]] = Anchor(
                    symbol=p["symbol"],
                    kind=p["kind"],
                    ref=p["ref"],
                    motive=p["motive"],
                )
        return self._table

    def lookup(self, symbol: str) -> Anchor | SemanticError:
        """The anchor for a symbol, or an explicit semantic error."""
        anchor = self._load().get(symbol)
        if anchor is not None:
            return anchor
        return SemanticError(
            symbol=symbol,
            message=f"'{symbol}' no tiene anchor.",
            hint=(
                "Declara uno: knowledge anchor add "
                f"{symbol} --kind <model|doc|relation|operation|projection> ..."
            ),
        )

    def all(self) -> list[Anchor]:
        """The living grammar, for `knowledge anchors` and derived help."""
        return sorted(self._load().values(), key=lambda a: (a.kind, a.symbol))

    def by_kind(self, kind: str) -> list[Anchor]:
        """Anchors of one kind (used by the desugarer to classify tokens)."""
        return [a for a in self.all() if a.kind == kind]
