"""What a word names, as a form (spec 05, 13), read into its parts: the kind of thing the
ref points at and, when it has one, the model, the field, the relation, the predicate, the
action verb, the value and the steps of a composed sentence. `text` is the form written back.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pron.kernel.sexp import write


@dataclass
class Ref:
    form: Any
    kind: str  # model | field | value | predicate | relation | action | doc | compose
    model: str | None = None
    field_name: str | None = None
    relation: str | None = None
    where: str | None = None
    verb: str | None = None
    value: Any = None
    steps: list[dict[str, Any]] = field(default_factory=list)

    @property
    def text(self) -> str:
        return write(self.form)
