"""A noun phrase becomes addresses (spec 02): scope + one predicate per query, the
intersection of the address lists, and the determiner deciding what counts as unique,
ambiguous or missing. pron never reads a payload to filter.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from pron.ids import export_id as _export_id, normalize_address, scope as _scope
from pron.lexicon import Lexicon
from pron.surface.nouns import NounPhrase

_EQ_PREDICATE = re.compile(r'^(\w+)\s*=\s*"([^"]*)"$')


@dataclass
class Resolution:
    phrase: NounPhrase
    addresses: list[str]  # st.{Model}.doc
    outcome: str  # unico | ambiguo | missing
    queries: list[str] = field(default_factory=list)  # the exact calls, copyable
    candidates: list[str] = field(default_factory=list)
    note: str = ""
    also_read: list[str] = field(
        default_factory=list
    )  # documents a complement resolved on the way (spec 07: reads)

    @property
    def cardinality(self) -> str:
        return "una" if self.phrase.number == "singular" else "conjunto"

    def export_ids(self) -> list[str]:
        return [address_to_export_id(a) for a in self.addresses]


def address_to_export_id(address: str) -> str:
    """st.{Model}.doc → Model:doc; A:st.{Model}.doc → A:Model:doc; an export id passes through."""
    return _export_id(address)


def resolve(np: NounPhrase, lex: Lexicon) -> Resolution:
    store = lex.world.store
    if np.model is None:
        return Resolution(np, [], "missing", note="a referent without an antecedent")
    if np.unknown_values:
        model, fld, text = np.unknown_values[0]
        near = [
            w.form
            for w, _ in lex.near(text, kinds=("value",))
            if w.model == model and w.field_name == fld
        ]
        allowed = [w.form for w in lex.values_of(model, fld)]
        return Resolution(
            np,
            [],
            "missing",
            candidates=near or allowed,
            note=f"'{text}' is not a value of {model}.{fld}",
        )
    scopes = [
        _scope(s, np.model) for s in lex.stores
    ]  # one scope per store of the projection (spec 01)
    queries: list[str] = []
    result: list[str] | None = None
    # complements: the edges of a relation to what "of X" names, crossed with the predicates (spec 02)
    also_read: list[str] = []
    for comp in np.complements:
        linked = _linked(np, comp, lex, queries, also_read)
        if linked is None:
            if isinstance(comp, NounPhrase):
                return Resolution(
                    np,
                    [],
                    "missing",
                    queries,
                    note=f"no relation joins {np.model} and {comp.describe()}",
                )
            np.proper += comp  # not a related document: a proper name of the head
            continue
        result = linked if result is None else [a for a in result if a in set(linked)]
    predicates = list(np.predicates) + _proper_predicates(np, lex)
    for where in predicates:
        found: list[str] = []
        for scope in scopes:
            hits = _normalize_addresses(
                store.find(scope, where)
            )  # st.{M+}.doc and st.{M}.doc are the same address
            queries.append(f"find '{scope}' --where '{where}' → {len(hits)}")
            found += hits
        result = found if result is None else [a for a in result if a in set(found)]
    if result is None:
        result = []
        for scope in scopes:
            names = store.list(scope)
            result += [f"{scope}.{name}" for name in names]
            queries.append(f"ls '{scope}' → {len(names)}")
    elif len(predicates) + len(np.complements) > 1:
        queries.append(f"∩ → {len(result)}")
    result = _normalize_addresses(result)
    decided = _decide(np, result, queries, lex)
    decided.also_read = also_read
    return decided


def _linked(
    np: NounPhrase, comp: Any, lex: Lexicon, queries: list[str], also_read: list[str]
) -> list[str] | None:
    """The heads related to what the complement names: for each relation type between the head's
    family and another class, resolve the complement in that class and read the edges (kgdb, or
    the RelationDocs in sldb). None when no relation and class take the complement."""
    from pron.verbs import Verbs

    assert np.model is not None
    family = set(lex.world.family_of(np.model))
    verbs = Verbs(lex)
    for rel, rt in lex.relation_types.items():
        sides = []
        if family & set(rt.get("source_types") or []):
            sides.append(("to", rt.get("target_types") or []))
        if family & set(rt.get("target_types") or []):
            sides.append(("from", rt.get("source_types") or []))
        for direction, others in sides:
            for other in others:
                if isinstance(comp, NounPhrase):
                    if comp.model is None or other not in lex.world.family_of(
                        comp.model
                    ):
                        continue
                    inner = resolve(comp, lex)
                else:
                    inner = resolve(
                        NounPhrase(other, "all", "plural", proper=list(comp)), lex
                    )
                queries.extend("  " + q for q in inner.queries)
                if inner.outcome != "unico" or not inner.addresses:
                    continue
                also_read.extend(inner.addresses + inner.also_read)
                heads: list[str] = []
                for eid in inner.export_ids():
                    read = (
                        verbs.edges_to(eid, rel)
                        if direction == "to"
                        else verbs.edges_from(eid, rel)
                    )
                    queries.extend(read.queries)
                    heads += [
                        e["source"] if direction == "to" else e["target"]
                        for e in read.edges
                    ]
                from pron.ids import address_of

                return sorted({address_of(h) for h in heads})
    return None


def _proper_predicates(np: NounPhrase, lex: Lexicon) -> list[str]:
    """A proper name in name position: the model's key field when the name looks like a
    key value, else the document name, else a name/title field."""
    assert np.model is not None
    out = []
    key = (lex.projection.get("key") or {}).get(np.model)
    for name in np.proper:
        if key and (name.isdigit() or _field_kind(lex, np.model, key) == "string"):
            out.append(
                f"{key} = {name if name.isdigit() else chr(34) + name + chr(34)}"
            )
        else:
            out.append(f'doc ~ "{_slug(name)}"')
    return out


def _decide(
    np: NounPhrase, result: list[str], queries: list[str], lex: Lexicon
) -> Resolution:
    assert np.model is not None
    if not result and np.proper:
        # a proper name that is not the doc name: try name/title fields, then offer neighbors
        for fld in ("name", "title"):
            if any(f["name"] == fld for f in lex.world.schema(np.model, lex.stores)):
                alt: list[str] | None = None
                for name in np.proper:
                    found: list[str] = []
                    for scope in (_scope(s, np.model) for s in lex.stores):
                        hits = lex.world.store.find(scope, f'{fld} ~ "{name}"')
                        queries.append(
                            f"find '{scope}' --where '{fld} ~ \"{name}\"' → {len(hits)}"
                        )
                        found += hits
                    alt = found if alt is None else [a for a in alt if a in set(found)]
                if alt:
                    result = _normalize_addresses(alt)
                    break
    if np.number == "singular":
        if len(result) == 1:
            return Resolution(np, result, "unico", queries)
        if len(result) > 1 and np.determiner == "any":
            return Resolution(
                np,
                result[:1],
                "unico",
                queries,
                candidates=result[1:],
                note=f"any: took {result[0]}; also {', '.join(result[1:])}",
            )
        if len(result) > 1:
            return Resolution(np, [], "ambiguo", queries, candidates=result)
        return _missing_with_value_suggestions(np, queries, lex)
    return Resolution(np, result, "unico", queries)


def _missing_with_value_suggestions(
    np: NounPhrase, queries: list[str], lex: Lexicon
) -> Resolution:
    hit = _value_suggestions(np, lex, queries)
    if hit is not None:
        model, fld, text, ranked = hit
        np.unknown_values.append((model, fld, text))
        return Resolution(
            np,
            [],
            "missing",
            queries,
            candidates=ranked,
            note=f"no {np.model} matches {np.describe()}",
        )
    near = _near_names(np, lex)
    return Resolution(
        np,
        [],
        "missing",
        queries,
        candidates=near,
        note=f"no {np.model} matches {np.describe()}",
    )


def _value_suggestions(
    np: NounPhrase, lex: Lexicon, queries: list[str]
) -> tuple[str, str, str, list[str]] | None:
    """PLAN 11 P1 (spec 05 §Calce aproximado): for each equality predicate on a string,
    non-enum field, rank the text that did not match against the field's existing distinct
    values (family included, stores of the projection) and offer the nearest as candidates.
    Never entered as lexicon, never executed on its own — only offered. Returns
    (model, field, text, ranked) for the first predicate with a hit, or None."""
    assert np.model is not None
    matching = lex.projection.get("matching") or {}
    max_values = int(matching.get("max_values", 500))
    neighbors = int(matching.get("neighbors", 3))
    threshold = float(matching.get("threshold", 0.55))
    for where in np.predicates:
        m = _EQ_PREDICATE.match(where)
        if not m:
            continue
        fld, text = m.group(1), m.group(2)
        if _field_kind(lex, np.model, fld) != "string":
            continue
        values = lex.distinct_values(np.model, fld)
        if not values:
            continue
        if len(values) > max_values:
            queries.append(
                f"{np.model}.{fld}: {len(values)} distinct values over matching.max_values"
                f" ({max_values}), no value suggestion"
            )
            continue
        ranked = [
            key
            for key, _ in lex.matcher.rank(
                text, [(v, v) for v in values], k=neighbors, threshold=threshold
            )
        ]
        if ranked:
            return np.model, fld, text, ranked
    return None


def _near_names(np: NounPhrase, lex: Lexicon) -> list[str]:
    assert np.model is not None
    if not np.proper:
        return []
    from pron.ids import address_of, join_id

    candidates = []
    for s in lex.stores:
        for d in lex.world.store.docs_of(np.model, s):
            candidates.append(
                (
                    address_of(join_id(None if s == "local" else s, np.model, d.name)),
                    f"{d.name} {d.payload.get('name', '')} {d.payload.get('title', '')}",
                )
            )
    return [
        key
        for key, _ in lex.matcher.rank(
            " ".join(np.proper),
            candidates,
            k=3,
            threshold=float(
                (lex.projection.get("matching") or {}).get("threshold", 0.55)
            ),
        )
    ]


def _normalize_addresses(addresses: list[str]) -> list[str]:
    """[store:]st.{Model+}.doc → [store:]st.{Model}.doc."""
    return sorted({normalize_address(a) for a in addresses})


def _field_kind(lex: Lexicon, model: str, fld: str) -> str:
    for f in lex.world.schema(model, lex.stores):
        if f["name"] == fld:
            return f["kind"]
    return "string"


def _slug(text: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in text).strip("-")
