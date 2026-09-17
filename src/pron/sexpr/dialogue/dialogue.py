"""The dialogue: the only state pron keeps per session (spec 06). A pending question
of one of two kinds, the referents recent turns left, and who is speaking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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

    def referent(
        self, number: str, model: str | None, family: list[str] | None = None
    ) -> list[str] | None:
        """The antecedent for a pronoun: singular by class (a set of one counts), plural = the last set."""
        if number == "plural":
            return list(self.last_set) if self.last_set else None
        for m in family or ([model] if model else []):
            if m in self.singular:
                return [self.singular[m]]
        if model is None and self.last_singular:
            return [self.last_singular]
        return None

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
            return _within(int(t) - 1, n)
        ordinal = _ordinal(t)
        if ordinal is not None:
            return _within(ordinal if ordinal >= 0 else n + ordinal, n)
        return _by_label(t, self.pending.labels, matcher)


def _within(i: int, n: int) -> list[int]:
    return [i] if 0 <= i < n else []


def _ordinal(t: str) -> int | None:
    """The index an ordinal says — "second", "the second", "the second one" — negative from
    the end; None when it is not one."""
    ordinals = FUNCTION_WORDS["designation"]["ordinal"]
    return next(
        (
            idx
            for word, idx in ordinals.items()
            if t in (word, f"the {word}", f"the {word} one")
        ),
        None,
    )


def _by_label(t: str, labels: list[str], matcher) -> list[int]:
    """The candidates whose labels a name matches best, when it matches well enough."""
    if t.startswith("the ") and t.endswith(" one"):
        t = t[4:-4]
    ranked = matcher.rank(
        t,
        [(str(i), label) for i, label in enumerate(labels)],
        k=len(labels),
        threshold=0.0,
    )
    if not ranked:
        return []
    best = ranked[0][1]
    winners = [int(k) for k, s in ranked if s >= best - 1e-9]
    return winners if best >= 0.5 else []
