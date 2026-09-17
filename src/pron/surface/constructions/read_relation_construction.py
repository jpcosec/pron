"""`read_relation` (spec 03, 11 §1): a relation word in a sentence that reads edges — "what
reservations does Ana have for Friday?". Which side is asked is decided by the interrogated
phrase's model; a bare proper name takes the other side. What attaches to neither side is
left over for the read to narrow its answer with.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.kernel.parts.part import Part
from pron.kernel.parts.word import Word
from pron.surface.interpret import _first, _in_np, _proper_phrase, _unattached
from pron.surface.nouns import find_noun_phrases

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class ReadRelationConstruction:
    name = "read_relation"

    def __call__(self, items: list[Item], lex: "Lexicon") -> Part | None:
        w = _first(items, "relation", "alias-relation")
        if w is None:
            return None
        nps = find_noun_phrases(items, lex)
        part = Part("read", verb=w, leftovers=_unattached(items, nps))
        self._sides(part, w, items, nps, lex)
        part.leftovers = [
            i
            for i in part.leftovers
            if not _in_np(i, [n for n in (part.subject, part.object) if n])
        ]
        return part

    def _sides(
        self,
        part: Part,
        w: Word,
        items: list[Item],
        nps: list[NounPhrase],
        lex: "Lexicon",
    ) -> None:
        rt = lex.relation_types.get(w.relation or "", {})
        sources = set(rt.get("source_types") or [])
        targets = set(rt.get("target_types") or [])
        interrogated = next((n for n in nps if n.interrogated), None)
        if interrogated is None:
            self._told(part, nps, sources, lex)
            return
        named = [i for i in items if i.kind == "unknown" and not _in_np(i, nps)]
        self._asked(part, interrogated, named, nps, (sources, targets), lex)

    @staticmethod
    def _asked(
        part: Part,
        interrogated: NounPhrase,
        named: list[Item],
        nps: list[NounPhrase],
        sides: tuple[set[str], set[str]],
        lex: "Lexicon",
    ) -> None:
        """The interrogated phrase is the side its model's family stands on."""
        sources, targets = sides
        # an interrogated phrase always has a head model: find_noun_phrases builds it from one
        if set(lex.world.family_of(interrogated.model)) & sources:  # type: ignore[arg-type]
            part.subject = interrogated
            part.object = _proper_phrase(named, targets, nps)
            part.payload["asked"] = "subject"
        else:
            part.object = interrogated
            part.subject = _proper_phrase(named, sources, nps)
            part.payload["asked"] = "object"

    @staticmethod
    def _told(
        part: Part, nps: list[NounPhrase], sources: set[str], lex: "Lexicon"
    ) -> None:
        """Nothing interrogated: the first phrase is the subject when it can be a source (or
        is a referent), else the object."""
        others = [n for n in nps if not n.interrogated]
        if not others:
            return
        fam = set(lex.world.family_of(others[0].model)) if others[0].model else set()
        if fam & sources or others[0].referent is not None:
            part.subject, part.payload["asked"] = others[0], "object"
        else:
            part.object, part.payload["asked"] = others[0], "subject"
