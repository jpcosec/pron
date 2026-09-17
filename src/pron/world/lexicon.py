"""The lexicon (spec 05): every word a session can say, derived from the world and cut by the
projection. Nothing in it is written in code except pron's function words; a word
of a world comes from a model, a field, an enum value, a relation type, or an alias.

The words are built in pron.world.lexicon_parts — model words, relation and kernel words,
alias words, in that order — and read here, with the reading classes there too (spoken
forms, the verbs of a class, the values a field holds).
"""

from __future__ import annotations

from typing import Any, Iterable

from pron.kernel.parts.word import Word
from pron.world.lexicon_parts.alias_words import AliasWords
from pron.world.lexicon_parts.document_values import DocumentValues
from pron.world.lexicon_parts.model_words import ModelWords
from pron.world.lexicon_parts.relation_words import RelationWords
from pron.world.lexicon_parts.spoken_forms import SpokenForms
from pron.world.lexicon_parts.verbs_for import VerbsFor
from pron.world.lexicon_parts.vocabulary import (  # noqa: F401 - read from pron.world.lexicon
    FUNCTION_WORDS,
    INTERNAL_MODELS,
    UNSUGGESTED_MODELS,
)
from pron.world.matching.difflib_matcher import normalize
from pron.world.matching.matcher import Matcher
from pron.world.world import World


class Lexicon:
    def __init__(
        self, world: World, projection: dict[str, Any], matcher: Matcher | None = None
    ):
        self.world = world
        self.projection = projection
        self.matcher = matcher or Matcher()
        self.words: list[Word] = []
        self._by_form: dict[str, list[Word]] = {}
        self.models: list[str] = []
        self.relation_types: dict[str, dict] = {}
        self.actions: list[str] = list(projection.get("actions") or [])
        self.stores: list[str] = list(
            projection.get("stores") or ["local"]
        )  # where the nouns live; the first is where the session writes
        self._build()

    def _build(self) -> None:
        self.models = projection_models(self.world, self.projection)
        model_words = ModelWords(self)
        for m in self.models:
            model_words(m)
        RelationWords(self).relations()
        RelationWords(self).kernel()
        AliasWords(self)()
        for w in self.words:
            self._by_form.setdefault(normalize(w.form), []).append(w)

    # -- reading ----------------------------------------------------------------------

    def lookup(self, form: str) -> list[Word]:
        return list(self._by_form.get(normalize(form), []))

    def forms(self) -> list[str]:
        return sorted(self._by_form)

    def of_kind(self, *kinds: str) -> list[Word]:
        return [w for w in self.words if w.kind in kinds]

    def fields_of(self, model: str) -> list[Word]:
        family = self.world.family_of(model)
        return [w for w in self.words if w.kind == "field" and w.model in family]

    def values_of(self, model: str, field_name: str) -> list[Word]:
        return [
            w
            for w in self.words
            if w.kind == "value" and w.model == model and w.field_name == field_name
        ]

    def distinct_values(self, model: str, field_name: str) -> list[str]:
        """The distinct values a string field actually holds across this projection's stores
        and the model's family, read straight from the documents (spec 05 §Calce aproximado,
        PLAN 11 P1/P2). Free text never becomes a lexicon word (P3 only does that for
        `system`/`tags`); this is what a value suggestion ranks against."""
        return DocumentValues(self)(set(self.world.family_of(model)), field_name)

    def model_form(self, model: str) -> str:
        """The lexicon's preferred spoken form of a model: its own word (an alias if one
        exists, else the identifier lowered — 05 §Anchors)."""
        return SpokenForms(self).model_form(model)

    def field_form(self, model: str, field_name: str) -> str:
        """The lexicon's preferred spoken form of a field: an alias over the field's own
        identifier form (05 §Anchors)."""
        return SpokenForms(self).field_form(model, field_name)

    def examples(self, k: int = 6) -> list[str]:
        """PLAN 11 P4 (spec 05): a few sentences this projection can actually resolve, built
        from its own words — never written by a world. Used so 'what can I say?' offers
        something real instead of the restaurant's own hint text."""
        return SpokenForms(self).examples(k)

    def verbs_for(self, model: str) -> list[Word]:
        """Every verb a class can take, derived: relation types naming it or an ancestor
        as source or target, action aliases on its fields, compose aliases that create it,
        and the kernel verbs the projection allows."""
        return VerbsFor(self)(model)

    def near(
        self, query: str, kinds: Iterable[str] | None = None, k: int | None = None
    ) -> list[tuple[Word, float]]:
        """Neighbors of an unknown word among the lexicon's forms and motives. Never executed, only offered."""
        matching = self.projection.get("matching") or {}
        k = k or int(matching.get("neighbors", 3))
        threshold = float(matching.get("threshold", 0.55))
        pool = [w for w in self.words if kinds is None or w.kind in kinds]
        candidates = [(str(i), f"{w.form} {w.motive}") for i, w in enumerate(pool)]
        return [
            (pool[int(key)], round(score, 3))
            for key, score in self.matcher.rank(
                query, candidates, k=k, threshold=threshold
            )
        ]

    def table(self, model: str | None = None) -> list[dict[str, str]]:
        words = self.verbs_for(model) + self.fields_of(model) if model else self.words
        return [
            {
                "form": w.form,
                "kind": w.kind,
                "ref": w.ref,
                "motive": w.motive,
                "source": w.source,
            }
            for w in words
        ]


def projection_models(world: World, projection: dict[str, Any]) -> list[str]:
    """The models a projection can name: its list, or every model of its stores but pron's own."""
    stores = list(projection.get("stores") or ["local"])
    known: list[str] = []
    for s in stores:
        for m in world.model_names(s):
            if m not in known:
                known.append(m)
    wanted = projection.get("models") or []
    if wanted:
        return [m for m in wanted if m in known]
    return [m for m in known if m not in INTERNAL_MODELS]
