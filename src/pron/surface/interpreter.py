"""From a sentence to an Interpretation (spec 06): the six steps, with the world
consulted only at steps 2 (lexicon), 4 (addresses) and 5 (types).

The constructions are fixed and listed in patterns.yaml; a world never adds one, it
adds words. A sentence coordinated with "and" is one move with several parts. Each
construction is a class in pron.surface.constructions, tried in patterns.yaml's order.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.parts.interpretation import Interpretation
from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part
from pron.surface.classifier import Classifier
from pron.surface.constructions.construction_registry import CONSTRUCTIONS
from pron.surface.interpret import PATTERNS, _split_on_and, _used
from pron.world.lexicon import Lexicon


class Interpreter:
    def __init__(self, lexicon: Lexicon, now: Any = None):
        self.lex = lexicon
        self.clf = Classifier(lexicon, now=now)

    def interpret(self, sentence: str) -> Interpretation:
        items = self.clf.classify(sentence)
        parts: list[Part] = []
        notes: list[str] = []
        for chunk in _split_on_and(items):
            part = self._part(chunk)
            if part is None:
                notes.append(
                    "no construction matches: " + " ".join(i.text for i in chunk)
                )
                parts.append(Part("none", items=chunk))
            else:
                parts.append(part)
        unknown = [i for i in items if i.kind == "unknown" and not _used(i, parts)]
        return Interpretation(sentence, items, parts, unknown=unknown, notes=notes)

    def _part(self, items: list[Item]) -> Part | None:
        """The first construction, in patterns.yaml order, that recognises these items."""
        for c in PATTERNS:
            construction = CONSTRUCTIONS.get(c["name"])
            part = construction(items, self.lex) if construction else None
            if part is not None:
                part.items = items
                return part
        return None
