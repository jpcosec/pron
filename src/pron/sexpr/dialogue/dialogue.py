"""The dialogue: the only state pron keeps per session (spec 06). A pending question
of one of two kinds, the referents recent turns left, and who is speaking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pron.kernel.ids import address_of, export_id, model_of
from pron.sexpr.dialogue.designation import by_label, ordinal, within
from pron.sexpr.dialogue.pending import Pending
from pron.world.lexicon import FUNCTION_WORDS


@dataclass
class Dialogue:
    speaker: str = ""
    speaker_address: str | None = None
    pending: Pending | None = None
    singular: dict[str, str] = field(
        default_factory=dict
    )  # model -> last singular address
    last_singular: str | None = None
    last_set: list[str] = field(default_factory=list)
    last_set_model: str | None = None
    last_written: str | None = None  # last address written, for "why?"
    last_missing: dict[str, Any] | None = (
        None  # the hole a missing turn left, for a correction (spec 06)
    )

    @property
    def state(self) -> str:
        return "pendiente" if self.pending else "libre"

    # -- referents ----------------------------------------------------------------

    def remember(self, addresses: list[str], model: str | None) -> None:
        if len(addresses) == 1:
            self.last_singular = addresses[0]
            if model:
                self.singular[model] = addresses[0]
            self.last_set = list(addresses)
            self.last_set_model = model
        elif addresses:
            self.last_set = list(addresses)
            self.last_set_model = model

    def name(self, address: str, model: str | None) -> None:
        """A document a sentence named on its own (a read's subject): the singular antecedent
        of its class. It is no set, so "them" still means what the read answered."""
        self.last_singular = address
        if model:
            self.singular[model] = address

    def referent(
        self, number: str, model: str | None, family: list[str] | None = None
    ) -> list[str] | None:
        """The antecedent for a pronoun: singular by class (a set of one counts), plural = the last set.
        Without a model, family is the classes any of which will do, and the latest one wins."""
        if number == "plural":
            return list(self.last_set) if self.last_set else None
        last = self.last_singular
        if model is None and family and last and model_of(export_id(last)) in family:
            return [last]
        for m in family or ([model] if model else []):
            if m in self.singular:
                return [self.singular[m]]
        if model is None and self.last_singular:
            return [self.last_singular]
        return None

    def forget(self, export_id: str) -> None:
        """A document that left the store (an undone create) is no antecedent any more; "why?" can still ask about it."""
        gone = address_of(export_id)
        self.singular = {m: a for m, a in self.singular.items() if a != gone}
        if self.last_singular == gone:
            self.last_singular = None
        self.last_set = [a for a in self.last_set if a != gone]

    def speaker_referent(self) -> list[str] | None:
        return [self.speaker_address] if self.speaker_address else None

    # -- pending -----------------------------------------------------------------------

    def open(self, pending: Pending) -> None:
        self.pending = pending

    def close(self) -> None:
        self.pending = None

    def classify_reply(self, text: str, items_kinds: list[str]) -> str:
        """answer | order | unclear, per spec 06 continuation rules."""
        if self.pending is None:
            return "order"
        t = text.strip().lower().rstrip("?.! ")
        if t in {w.lower() for w in FUNCTION_WORDS["designation"]["none"]}:
            return "answer"
        has_verb = any(k in ("action", "relation") for k in items_kinds)
        if self.pending.kind == "choice":
            if has_verb:
                return "order"
            return "answer"
        # data: a literal that fits the field, else an order if it has a verb
        if has_verb:
            return "order"
        return "answer"

    def pick(self, text: str, matcher) -> list[int]:
        """Indexes of candidates a designation selects: a number, an ordinal, or a name matched against labels."""
        if self.pending is None:
            return []
        n = len(self.pending.candidates)
        t = text.strip().lower().rstrip("?.! ")
        if t.isdigit():
            return within(int(t) - 1, n)
        nth = ordinal(t)
        if nth is not None:
            return within(nth if nth >= 0 else n + nth, n)
        return by_label(t, self.pending.labels, matcher)
