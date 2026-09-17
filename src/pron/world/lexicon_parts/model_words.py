"""The words a model brings to the lexicon (spec 05): the model itself, its identifier split
into words, one word per field, one per enum value, and the values already used in a
`system` or `tags` field.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from pron.kernel.parts.word import Word
from pron.kernel.sexp.read_write import Sym, write
from pron.world.lexicon_parts.document_values import DocumentValues
from pron.world.lexicon_parts.vocabulary import UNSUGGESTED_MODELS, word_ref

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class ModelWords:
    """Appends the words of one model to a lexicon being built."""

    def __init__(self, lex: "Lexicon") -> None:
        self.lex = lex

    def __call__(self, m: str) -> None:
        try:
            model_type = self.lex.world.model_type(m, self.lex.stores)
        except Exception:  # noqa: BLE001 - an unresolvable model has no words
            return
        doc = (model_type.__doc__ or "").strip().splitlines()
        self._model(m, doc[0] if doc else f"a {m}")
        for f in self.lex.world.schema(m, self.lex.stores):
            self._field(m, f)

    def _model(self, m: str, motive: str) -> None:
        words = self.lex.words
        words.append(
            Word(m.lower(), "model", word_ref("model", m), motive, f"model {m}", model=m)
        )
        split = " ".join(re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+", m)).lower()
        if (
            split and split != m.lower()
        ):  # "cli command doc": the identifier split into words, until an alias says better (spec 05)
            words.append(
                Word(
                    split,
                    "model",
                    word_ref("model", m),
                    motive,
                    f"model {m} (identifier split into words)",
                    model=m,
                )
            )

    def _field(self, m: str, f: dict[str, Any]) -> None:
        fname = f["name"]
        self.lex.words.append(
            Word(
                fname.replace("_", " "),
                "field",
                word_ref("field", m, fname),
                f["description"] or fname,
                f"field {m}.{fname}",
                model=m,
                field_name=fname,
                payload=f,
            )
        )
        for v in f.get("enum") or []:
            self._value(m, fname, v, f"enum {m}.{fname}")
        if (
            fname in ("system", "tags")
            and f["kind"] in ("string", "stringlist")
            and m not in UNSUGGESTED_MODELS
        ):
            # spec 05 / PLAN 11 P3: values already used in a "system" or "tags" field
            # are lexicon too, unlike other free text (never entered otherwise).
            used = DocumentValues(self.lex)([m], fname, f["kind"] == "stringlist")
            for v in used:
                self._value(m, fname, v, "used value")

    def _value(self, m: str, fname: str, v: Any, source: str) -> None:
        self.lex.words.append(
            Word(
                str(v),
                "value",
                write([Sym("value"), Sym(m), Sym(fname), v]),
                f"{fname} = {v}",
                source,
                model=m,
                field_name=fname,
                payload={"value": v},
            )
        )
