"""The words of relation types and of kernel verbs (spec 05): a relation type the projection
admits is a word under its name and its name with spaces, and each action verb the
projection allows is a word under every form pron's function words list for it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.word import Word
from pron.world.lexicon_parts.vocabulary import FUNCTION_WORDS, word_ref

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class RelationWords:
    """Appends relation and kernel-verb words to a lexicon being built."""

    def __init__(self, lex: "Lexicon") -> None:
        self.lex = lex

    def relations(self) -> None:
        """Every relation type of the lexicon's stores the projection admits, with its mode."""
        allowed = {
            r["name"]: r.get("mode", "read")
            for r in self.lex.projection.get("relations") or []
        }
        for name, rt in self.lex.world.relation_types(self.lex.stores).items():
            if allowed and name not in allowed:
                continue
            payload = {**rt, "mode": allowed.get(name, "read and assert")}
            for form in dict.fromkeys((name, name.replace("_", " "))):
                self.lex.words.append(
                    Word(
                        form,
                        "relation",
                        word_ref("relation", name),
                        rt.get("description", name),
                        f"RelationTypeDoc {rt.get('doc', name)}",
                        relation=name,
                        payload=payload,
                    )
                )
            self.lex.relation_types[name] = payload

    def kernel(self) -> None:
        """The action verbs; an empty actions list means no action verbs at all."""
        for verb, spec in FUNCTION_WORDS["kernel"].items():
            if verb not in self.lex.actions:
                continue
            for form in spec["forms"]:
                self.lex.words.append(
                    Word(
                        form,
                        "action",
                        word_ref("action", verb),
                        spec["motive"],
                        "kernel",
                        payload={"verb": verb},
                    )
                )
