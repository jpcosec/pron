"""The other direction of the surface (spec 06, 13): a compiled Part written back as the
forms it says. `said` is what a sentence said, with every noun still a phrase; `resolved` is
what the move did, with every noun replaced by the addresses it resolved to — evaluating that
on the same world in the same state leaves the same writes, without the dialogue.

A part is rendered by pron.surface.render_said, a noun by pron.surface.render_noun, and the
addresses put in by pron.surface.render_addresses.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.part import Part
from pron.kernel.sexp.read_write import Sym
from pron.surface.render_addresses import AddressedPart
from pron.surface.render_said import SaidPart

if TYPE_CHECKING:
    from pron.sexpr.turn.turn_tools import TurnTools


def said(parts: list[Part], tools: TurnTools) -> Any:
    """tools: the lexicon, world and dialogue of the move, for the class each role needs,
    the slots of a composition and the predicates a read left over."""
    said_part = SaidPart(tools)
    return _one_or_move([said_part(p) for p in parts])


def resolved(parts: list[Part], plans: list[dict[str, Any]], tools: TurnTools) -> Any:
    """Evaluating this on the same world in the same state leaves the same writes, without the
    dialogue."""
    said_part, by_address = SaidPart(tools), AddressedPart(tools)
    return _one_or_move(
        [by_address(said_part(p), p, plan) for p, plan in zip(parts, plans)]
    )


def _one_or_move(forms: list[Any]) -> Any:
    return forms[0] if len(forms) == 1 else [Sym("move"), *forms]
