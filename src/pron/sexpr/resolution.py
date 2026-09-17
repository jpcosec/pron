"""What resolving a noun phrase left (spec 02): the addresses it names, whether that is
unique, ambiguous or missing, the exact sldb calls it took (copyable, for the trace), the
candidates to offer when it is not unique, and what a complement read on the way (spec 07).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pron.kernel.ids import export_id as _export_id
from pron.kernel.noun_phrase import NounPhrase


@dataclass
class Resolution:
    phrase: NounPhrase
    addresses: list[str]  # st.{Model}.doc
    outcome: str  # unico | ambiguo | missing
    queries: list[str] = field(default_factory=list)  # the exact calls, copyable
    candidates: list[str] = field(default_factory=list)
    note: str = ""
    also_read: list[str] = field(
        default_factory=list
    )  # documents a complement resolved on the way (spec 07: reads)

    @property
    def cardinality(self) -> str:
        return "una" if self.phrase.number == "singular" else "conjunto"

    def export_ids(self) -> list[str]:
        return [address_to_export_id(a) for a in self.addresses]


def address_to_export_id(address: str) -> str:
    """st.{Model}.doc → Model:doc; A:st.{Model}.doc → A:Model:doc; an export id passes through."""
    return _export_id(address)
