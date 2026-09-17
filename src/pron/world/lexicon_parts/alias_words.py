"""The words of aliases (spec 05, spec 13): an AnchorDoc names something as a form, and each
of its forms is a word — only when the projection wants that alias and everything its form
points at is inside the projection. A ref that is not a form names nothing; the lint says so.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.word import Word
from pron.sexpr.forms.refs import models_and_relations, parse as parse_ref

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class AliasWords:
    """Appends the alias words of the lexicon's stores to a lexicon being built."""

    def __init__(self, lex: "Lexicon") -> None:
        self.lex = lex

    def __call__(self) -> None:
        wanted = self.lex.projection.get("aliases") or ["all"]
        seen: set[str] = set()
        for s in self.lex.stores:
            if "AnchorDoc" not in self.lex.world.model_names(s):
                continue
            for d in self.lex.world.store.docs_of("AnchorDoc", s):
                if d.name in seen:
                    continue
                seen.add(d.name)
                self._alias_word(d, wanted)

    def _alias_word(self, d: Any, wanted: list[str]) -> None:
        p = d.payload
        if "all" not in wanted and p["symbol"] not in wanted:
            return
        try:
            ref = parse_ref(p["ref"], p.get("steps") or [])
        except ValueError:
            return  # a ref that is not a form names nothing; the lint reports it
        if not self._in_projection(ref):
            return  # its target is outside this projection: the word does not exist here (spec 01, 05)
        payload = {
            "symbol": p["symbol"],
            "ref": ref.text,
            "steps": ref.steps,
            "where": ref.where,
            "verb": ref.verb,
            "value": ref.value,
        }
        for form in p.get("forms") or [p["symbol"]]:
            self.lex.words.append(
                Word(
                    form,
                    f"alias-{ref.kind}",
                    ref.text,
                    p.get("motive", ""),
                    f"AnchorDoc {d.name}",
                    model=ref.model,
                    field_name=ref.field_name,
                    relation=ref.relation,
                    payload=payload,
                )
            )

    def _in_projection(self, ref: Any) -> bool:
        """An alias enters only if every model, relation and action verb it points at is in the projection."""
        lex = self.lex
        models, relations = models_and_relations(ref)
        for m in models:
            if m not in lex.models and not set(lex.world.family_of(m)) & set(
                lex.models
            ):
                return False
        if any(r not in lex.relation_types for r in relations):
            return False
        if ref.kind == "action" and ref.verb not in lex.actions:
            return False
        return not any(
            s.get("do") in ("create", "change") and s["do"] not in lex.actions
            for s in ref.steps
        )
