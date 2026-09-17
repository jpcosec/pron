"""What a move works with, as the projection was last loaded (spec 05, 06, 11).

The lexicon, the interpreter, the verbs, the kernel and the display are what one load of
the projection builds; the world, the matcher, the dialogue and the ledger outlive every
load. A move's phases take the pieces of this they use. It is a snapshot: when the world
changes and the projection is loaded again (spec 11 §5), whoever understands the move
again takes a new one from the `ProjectionState`, never this one.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pron.kernel.display import Display
from pron.kernel.kernel import Kernel
from pron.sexpr.dialogue.dialogue import Dialogue
from pron.sexpr.resolving.verbs import Verbs
from pron.sexpr.turn.ledger import Ledger
from pron.surface.interpreter import Interpreter
from pron.world.lexicon import Lexicon
from pron.world.matching.matcher import Matcher
from pron.world.world import World


@dataclass(frozen=True)
class TurnTools:
    """The world, the session-lived dialogue and ledger, and one load of the projection."""

    world: World
    matcher: Matcher
    dialogue: Dialogue
    ledger: Ledger
    projection: dict[str, Any]
    write_store: str | None
    lex: Lexicon
    interpreter: Interpreter
    verbs: Verbs
    kernel: Kernel
    display: Display
