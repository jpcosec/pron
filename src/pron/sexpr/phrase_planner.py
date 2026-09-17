"""Resolving one noun phrase of a part against the world (spec 02, 06, 13).

Three ways a phrase can name documents, tried in this order: it was said by address —
`(doc "Model:name")` — and then every id must exist, unless it is a create of this same
move the store has not written yet; it is a referent of the dialogue ("it", "them", "me")
and the antecedent is whatever a recent turn left, of the class this part needs; or it
describes a query, and sldb answers it. Whatever a phrase read on the way is noted on the
move (spec 07).
"""

from __future__ import annotations

from typing import Any

from pron.kernel.ids import model_of
from pron.kernel.noun_phrase import NounPhrase
from pron.sexpr.collaborator import Collaborator
from pron.sexpr.note_reads import note_reads
from pron.sexpr.resolution import Resolution, address_to_export_id
from pron.sexpr.resolve import resolve
from pron.world.store_error import StoreError


class PhrasePlanner(Collaborator):
    """One noun phrase, resolved to the addresses it names."""

    def __call__(
        self,
        np: NounPhrase,
        need_model: str | None,
        trace: list[str],
        record: dict[str, Any],
        pending: dict[str, str] | None = None,
    ) -> Resolution:
        if np.given:
            return self._given(np, record, pending or {})
        need_model = need_model or np.hint
        if np.referent is not None:
            return self._referent(np, need_model, trace)
        return self._query(np, trace, record)

    # -- said by address (spec 13 §Sustantivos) ------------------------------------------

    def _given(
        self, np: NounPhrase, record: dict[str, Any], pending: dict[str, str]
    ) -> Resolution:
        for a in np.given:
            gone = self._absent(address_to_export_id(a), pending)
            if gone is not None:
                return Resolution(np, [], "missing", note=gone)
        note_reads(self.s.world, np.given, record)
        return self._by_address(np)

    def _absent(self, eid: str, pending: dict[str, str]) -> str | None:
        if eid in pending:
            return None  # a create of this move the store has not written yet
        try:
            self.s.world.store.payload_of(eid)
        except StoreError:
            return f"there is no {eid}"
        return None

    @staticmethod
    def _by_address(np: NounPhrase) -> Resolution:
        if np.alternatives:
            return Resolution(
                np,
                list(np.given),
                "unico",
                candidates=list(np.alternatives),
                note=f"any: took {np.given[0]}; also {', '.join(np.alternatives)}",
            )
        return Resolution(np, list(np.given), "unico", note="by address")

    # -- a referent of the dialogue (spec 06) --------------------------------------------

    def _referent(
        self, np: NounPhrase, need_model: str | None, trace: list[str]
    ) -> Resolution:
        found = self._antecedent(np, need_model)
        if isinstance(found, Resolution):
            return found
        if np.number == "singular" and len(found) > 1:
            return Resolution(np, [], "ambiguo", candidates=found)
        assert np.referent is not None
        trace.append(f"'{np.referent.text}' → {', '.join(found)}")
        np.model = np.model or model_of(address_to_export_id(found[0]))
        return Resolution(np, found, "unico", note="referent")

    def _antecedent(
        self, np: NounPhrase, need_model: str | None
    ) -> list[str] | Resolution:
        assert np.referent is not None
        if np.referent.meta.get("who") == "speaker":
            found = self.s.dialogue.speaker_referent()
            if not found:
                note = "I don't know who you are in this world"
                return Resolution(np, [], "missing", note=note)
            return found
        family = self.s.world.family_of(need_model) if need_model else None
        found = self.s.dialogue.referent(np.number, need_model, family)
        return found or Resolution(np, [], "missing", note=_no_antecedent(np, need_model))

    # -- the query the phrase describes (spec 02) ----------------------------------------

    def _query(
        self, np: NounPhrase, trace: list[str], record: dict[str, Any]
    ) -> Resolution:
        res = resolve(np, self.s.lex)
        trace.extend(res.queries)
        record["queries"].extend(res.queries)
        if res.note:
            trace.append(res.note)
        note_reads(self.s.world, res.addresses + res.also_read, record)
        return res


def _no_antecedent(np: NounPhrase, need_model: str | None) -> str:
    assert np.referent is not None
    return f"'{np.referent.text}' has no antecedent" + (
        f" of class {need_model}" if need_model else ""
    )
