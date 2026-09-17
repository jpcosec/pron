"""Proper names of a noun phrase (spec 02): in name position, the model's key field when the
name looks like a key value, else the document's name. When neither finds anything, the
`name` or `title` field is tried; and when that fails too, the documents whose names are
nearest are offered.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.ids import address_of, join_id, scope as _scope
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.sexpr.resolving.field_kind import field_kind
from pron.sexpr.resolving.resolution import normalize_addresses

if TYPE_CHECKING:
    from pron.world.lexicon import Lexicon

NAME_FIELDS = ("name", "title")


class ProperNames:
    """What a phrase's proper names ask sldb, and what they come near to."""

    def __init__(self, lex: Lexicon):
        self.lex, self.store = lex, lex.world.store

    def predicates(self, np: NounPhrase) -> list[str]:
        """A proper name in name position: the model's key field when the name looks like a
        key value, else the document name."""
        assert np.model is not None
        key = (self.lex.projection.get("key") or {}).get(np.model)
        return [self._predicate(np.model, key, name) for name in np.proper]

    def _predicate(self, model: str, key: str | None, name: str) -> str:
        if key and (name.isdigit() or field_kind(self.lex, model, key) == "string"):
            return f"{key} = {name if name.isdigit() else chr(34) + name + chr(34)}"
        return f'doc ~ "{_slug(name)}"'

    def by_name_fields(self, np: NounPhrase, queries: list[str]) -> list[str] | None:
        """The documents every proper name matches in the first name/title field that finds any."""
        assert np.model is not None
        schema = self.lex.world.schema(np.model, self.lex.stores)
        for fld in NAME_FIELDS:
            if any(f["name"] == fld for f in schema):
                found = self._every_name(np.model, fld, np.proper, queries)
                if found:
                    return normalize_addresses(found)
        return None

    def _every_name(
        self, model: str, fld: str, names: list[str], queries: list[str]
    ) -> list[str] | None:
        alt: list[str] | None = None
        for name in names:
            found: list[str] = []
            for scope in (_scope(s, model) for s in self.lex.stores):
                hits = self.store.find(scope, f'{fld} ~ "{name}"')
                queries.append(
                    f"find '{scope}' --where '{fld} ~ \"{name}\"' → {len(hits)}"
                )
                found += hits
            alt = found if alt is None else [a for a in alt if a in set(found)]
        return alt

    def near(self, np: NounPhrase, threshold: float) -> list[str]:
        """The documents whose name, `name` or `title` come nearest to the proper names."""
        assert np.model is not None
        if not np.proper:
            return []
        candidates = [
            (
                address_of(join_id(None if s == "local" else s, np.model, d.name)),
                f"{d.name} {d.payload.get('name', '')} {d.payload.get('title', '')}",
            )
            for s in self.lex.stores
            for d in self.store.docs_of(np.model, s)
        ]
        ranked = self.lex.matcher.rank(
            " ".join(np.proper), candidates, k=3, threshold=threshold
        )
        return [key for key, _ in ranked]


def _slug(text: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in text).strip("-")
