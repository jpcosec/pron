"""How the lexicon says things back (spec 05 §Anchors, PLAN 11 P4): the preferred spoken form
of a model or a field — an alias over the identifier — and a few example sentences a
projection can actually resolve, built from its own words, never written by a world.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.word import Word

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class SpokenForms:
    """The forms one lexicon prefers when it speaks."""

    def __init__(self, lex: "Lexicon") -> None:
        self.lex = lex

    def model_form(self, model: str) -> str:
        """The lexicon's preferred spoken form of a model: its own word (an alias if one
        exists, else the identifier lowered — 05 §Anchors)."""
        return self._form("model", model, None, model.lower())

    def field_form(self, model: str, field_name: str) -> str:
        """The lexicon's preferred spoken form of a field: an alias over the field's own
        identifier form (05 §Anchors)."""
        return self._form(
            "alias-field",
            model,
            field_name,
            self._form("field", model, field_name, field_name.replace("_", " ")),
        )

    def _form(self, kind: str, model: str, field_name: str | None, default: str) -> str:
        """The first word of that kind for the model (and field), else `default`."""
        return next(
            (
                w.form
                for w in self.lex.words
                if w.kind == kind
                and w.model == model
                and (field_name is None or w.field_name == field_name)
            ),
            default,
        )

    def examples(self, k: int = 6) -> list[str]:
        """PLAN 11 P4 (spec 05): a few sentences this projection can actually resolve, built
        from its own words — never written by a world. Used so 'what can I say?' offers
        something real instead of the restaurant's own hint text."""
        if not self.lex.models:
            return []
        model = self.lex.models[0]
        singular = self.model_form(model)
        out: list[str] = [f"the {self._plural(model, singular) or singular}"]
        value_word = next(
            (w for w in self.lex.of_kind("value") if w.model == model), None
        )
        if value_word is not None:
            out.append(self._with_value(model, singular, value_word))
        if "create" in self.lex.actions:
            out.append(f"create a {singular}")
        return out[:k]

    def _with_value(self, model: str, singular: str, value_word: Word) -> str:
        """`the <model> <field> <value>`: the model narrowed by one of its value words."""
        term = self.field_form(model, value_word.field_name or "")
        return f"the {singular} {term} {value_word.form}"

    def _plural(self, model: str, singular: str) -> str | None:
        """A model word for the same model other than its singular form, if there is one."""
        return next(
            (
                w.form
                for w in self.lex.of_kind("model")
                if w.model == model and w.form != singular
            ),
            None,
        )
