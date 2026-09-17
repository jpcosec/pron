"""A noun phrase becomes addresses (spec 02): scope + one predicate per query, the
intersection of the address lists, and the determiner deciding what counts as unique,
ambiguous or missing. pron never reads a payload to filter.

The stages are the `Resolver`'s: the complements read through their relations
(pron.sexpr.resolving.complement_links), the predicates and proper names
(pron.sexpr.resolving.proper_names) asked of every store of the projection, and the decision
(pron.sexpr.resolving.decision).
"""

from __future__ import annotations

from pron.kernel.ids import scope as _scope
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.sexpr.resolving.complement_links import ComplementLinks
from pron.sexpr.resolving.decision import Decision
from pron.sexpr.resolving.proper_names import ProperNames
from pron.sexpr.resolving.resolution import Resolution, normalize_addresses
from pron.world.lexicon import Lexicon


def resolve(np: NounPhrase, lex: Lexicon) -> Resolution:
    return Resolver(lex, np)()


class Resolver:
    """One noun phrase resolved, stage by stage, with the exact queries each stage took."""

    def __init__(self, lex: Lexicon, np: NounPhrase):
        self.lex, self.np, self.store = lex, np, lex.world.store
        self.queries: list[str] = []
        self.also_read: list[
            str
        ] = []  # documents a complement resolved on the way (spec 07)
        self.result: list[str] | None = (
            None  # None until some stage narrows the documents
        )
        self.names = ProperNames(lex)
        # one scope per store of the projection (spec 01)
        self.scopes = [_scope(s, np.model) for s in lex.stores] if np.model else []

    def __call__(self) -> Resolution:
        unresolvable = self._unresolvable()
        if unresolvable is not None:
            return unresolvable
        missing = self._complements()
        if missing is not None:
            return missing
        self._predicates()
        decided = Decision(self.lex, self.names)(
            self.np, normalize_addresses(self.result or []), self.queries
        )
        decided.also_read = self.also_read
        return decided

    def _unresolvable(self) -> Resolution | None:
        """A referent without an antecedent, or a value the field does not have."""
        np = self.np
        if np.model is None:
            return Resolution(
                np, [], "missing", note="a referent without an antecedent"
            )
        if not np.unknown_values:
            return None
        model, fld, text = np.unknown_values[0]
        near = [
            w.form
            for w, _ in self.lex.near(text, kinds=("value",))
            if w.model == model and w.field_name == fld
        ]
        allowed = [w.form for w in self.lex.values_of(model, fld)]
        note = f"'{text}' is not a value of {model}.{fld}"
        return Resolution(np, [], "missing", candidates=near or allowed, note=note)

    def _complements(self) -> Resolution | None:
        """The edges of a relation to what "of X" names, crossed with each other (spec 02); a
        complement no relation takes is a proper name of the head, unless it is a phrase."""
        if not self.np.complements:
            return None
        links = ComplementLinks(self.lex, resolve, self.queries, self.also_read)
        for comp in self.np.complements:
            linked = links(self.np, comp)
            if linked is None and isinstance(comp, NounPhrase):
                note = f"no relation joins {self.np.model} and {comp.describe()}"
                return Resolution(self.np, [], "missing", self.queries, note=note)
            if linked is None:
                self.np.proper += (
                    comp  # not a related document: a proper name of the head
                )
            else:
                self._narrow(linked)
        return None

    def _predicates(self) -> None:
        """Each predicate asked of every store, the answers crossed; with none, every document."""
        predicates = list(self.np.predicates) + self.names.predicates(self.np)
        for where in predicates:
            self._narrow(self._find(where))
        if self.result is None:
            self.result = self._every_document()
        elif len(predicates) + len(self.np.complements) > 1:
            self.queries.append(f"∩ → {len(self.result)}")

    def _find(self, where: str) -> list[str]:
        found: list[str] = []
        for scope in self.scopes:
            # st.{M+}.doc and st.{M}.doc are the same address
            hits = normalize_addresses(self.store.find(scope, where))
            self.queries.append(f"find '{scope}' --where '{where}' → {len(hits)}")
            found += hits
        return found

    def _every_document(self) -> list[str]:
        result: list[str] = []
        for scope in self.scopes:
            names = self.store.list(scope)
            result += [f"{scope}.{name}" for name in names]
            self.queries.append(f"ls '{scope}' → {len(names)}")
        return result

    def _narrow(self, addresses: list[str]) -> None:
        self.result = (
            addresses
            if self.result is None
            else [a for a in self.result if a in set(addresses)]
        )
