"""The phrase of the sentence each slot of a compose alias takes (spec 05, 13).

`$referent:M` takes the referent of the sentence — the pronoun it said, or an implicit one
built from the words that were there; `$object:M` takes a phrase whose class is in M's
family. A composition compiled from forms already carries its slots filled, and then
nothing is guessed: the form said which phrase goes where.
"""

from __future__ import annotations

from pron.kernel.noun_phrase import NounPhrase
from pron.kernel.part import Part
from pron.sexpr.collaborator import Collaborator


class ComposeSlots(Collaborator):
    """Which noun phrase of the sentence fills each slot of a composition."""

    def __call__(self, part: Part) -> dict[str, NounPhrase]:
        assert part.verb is not None
        if "_slots" in part.payload:
            return dict(part.payload["_slots"])
        nps: list[NounPhrase] = part.payload.get("_nps", [])
        slots: dict[str, NounPhrase] = {}
        for step in part.verb.payload.get("steps", []):
            self._step(step, part, nps, slots)
        return slots

    def _step(
        self,
        step: dict,
        part: Part,
        nps: list[NounPhrase],
        slots: dict[str, NounPhrase],
    ) -> None:
        for slot_key in ("source", "target"):
            slot = step.get(slot_key)
            if _takes_a_phrase(slot, slots):
                self._fill(str(slot), part, nps, slots)

    def _fill(
        self,
        slot: str,
        part: Part,
        nps: list[NounPhrase],
        slots: dict[str, NounPhrase],
    ) -> None:
        kind, _, model = slot[1:].partition(":")
        if kind == "referent":
            slots[slot] = _referent(part, nps)
        elif kind == "object":
            np = self._of_family(nps, model)
            if np is not None:
                slots[slot] = np

    def _of_family(self, nps: list[NounPhrase], model: str) -> NounPhrase | None:
        return next(
            (n for n in nps if n.model and model in self.s.world.family_of(n.model)),
            None,
        )


def _takes_a_phrase(slot, slots: dict[str, NounPhrase]) -> bool:
    """`$created` is what the composition itself makes, and a slot filled once stays filled."""
    return (
        isinstance(slot, str)
        and slot.startswith("$")
        and slot != "$created"
        and slot not in slots
    )


def _referent(part: Part, nps: list[NounPhrase]) -> NounPhrase:
    found = next((n for n in nps if n.referent is not None), None)
    return found or NounPhrase(None, None, "singular", referent=_pronoun_item(part))


def _pronoun_item(part: Part):
    from pron.kernel.item import Item

    last = part.items[0].text.split()[-1] if part.items else "it"
    return Item(
        "referent", last, number="singular", meta={"who": "singular", "implicit": True}
    )
