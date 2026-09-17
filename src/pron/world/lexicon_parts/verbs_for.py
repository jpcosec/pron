"""Every verb a class can take (spec 05), derived from the lexicon: relation types naming it
or an ancestor as source or target, action aliases on its fields, compose aliases that
create it, and the kernel verbs the projection allows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.word import Word

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon

ALIAS_VERB_KINDS = ("alias-action", "alias-relation", "alias-predicate")


class VerbsFor:
    """The verb words of one model's family, once each by (kind, ref, form)."""

    def __init__(self, lex: "Lexicon") -> None:
        self.lex = lex

    def __call__(self, model: str) -> list[Word]:
        family = set(self.lex.world.family_of(model))
        out: list[Word] = []
        seen: set[tuple[str, str, str]] = set()
        for w in self.lex.words:
            key = (w.kind, w.ref, w.form)
            if key not in seen and self._takes(w, family):
                seen.add(key)
                out.append(w)
        return out

    def _takes(self, w: Word, family: set[str]) -> bool:
        if w.kind == "relation":
            return self._touches(w.payload, family) or (
                not w.payload.get("source_types") and not w.payload.get("target_types")
            )
        if w.kind in ALIAS_VERB_KINDS:
            return w.model in family or (
                w.relation is not None
                and self._touches(self.lex.relation_types.get(w.relation, {}), family)
            )
        if w.kind == "alias-compose":
            first = next(
                (s for s in w.payload.get("steps", []) if isinstance(s, dict)), {}
            )
            return first.get("model") in family
        return w.kind == "action"

    @staticmethod
    def _touches(rt: dict, family: set[str]) -> bool:
        """Whether a relation type names one of the family as source or target."""
        return bool(family & set(rt.get("source_types") or [])) or bool(
            family & set(rt.get("target_types") or [])
        )
