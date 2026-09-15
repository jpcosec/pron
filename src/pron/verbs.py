"""Transitive verbs (spec 03): read edges from kgdb with a fallback to the RelationDocs
in sldb; verify a verb against its RelationTypeDoc in sldb; evaluate conditions with
sldb over the subject; assert by creating a RelationDoc; transitions as guarded field
changes. pron never assembles edges.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from pron.graph import doc_id
from pron.ids import (
    is_local,
    join_id,
    model_of,
    qualify,
    relativize,
    scope as _scope,
    split_id,
    store_of,
)
from pron.lexicon import Lexicon
from pron.store import StoreError

BRACE_RE = re.compile(r"\{([A-Za-z_][\w]*)\}")


@dataclass
class EdgeRead:
    edges: list[dict[str, Any]]  # {source, target, relation, metadata}
    source: str  # "graph" | "sldb"
    queries: list[str] = field(default_factory=list)


class Verbs:
    def __init__(self, lex: Lexicon, write_store: str | None = None):
        self.lex = lex
        self.world = lex.world
        self.store = lex.world.store
        self.stores = list(lex.stores)  # where edges are looked for
        self.write_store = (
            write_store
            if write_store is not None
            else (None if lex.stores[0] == "local" else lex.stores[0])
        )  # where a new RelationDoc goes

    # -- reading ------------------------------------------------------------------------

    def _in_graph(self, export_id: str) -> bool:
        """The typed graph covers the local store; a linked store's document is read from sldb."""
        return (
            is_local(store_of(export_id))
            and self.world.graph_is_fresh()
            and self.world.graph.has_node(doc_id(export_id))
        )

    def edges_from(self, export_id: str, relation: str | None = None) -> EdgeRead:
        if self._in_graph(export_id):
            edges = self.world.graph.edges_from(doc_id(export_id), relation)
            return EdgeRead(
                [_strip(e) for e in edges],
                "graph",
                [f"kgdb edges_from({export_id}, {relation or '*'}) → {len(edges)}"],
            )
        return self._edges_sldb("source_id", export_id, relation)

    def edges_to(self, export_id: str, relation: str | None = None) -> EdgeRead:
        if self._in_graph(export_id):
            edges = self.world.graph.edges_to(doc_id(export_id), relation)
            return EdgeRead(
                [_strip(e) for e in edges],
                "graph",
                [f"kgdb edges_to({export_id}, {relation or '*'}) → {len(edges)}"],
            )
        return self._edges_sldb("target_id", export_id, relation)

    def _edges_sldb(self, side: str, export_id: str, relation: str | None) -> EdgeRead:
        """The authored edges as documents, in every store of the projection, when the graph
        is absent, stale, or does not hold the document."""
        queries = []
        found: list[str] = []
        for s in self.stores:
            sc = _scope(s, "RelationDoc", family=False)
            local_id = relativize(
                export_id, None if is_local(s) else s
            )  # a store's documents name their own documents without prefix
            hits = self.store.find(sc, f'{side} = "{local_id}"')
            queries.append(
                f"find '{sc}' --where '{side} = \"{local_id}\"' → {len(hits)} (graph not fresh)"
            )
            if relation:
                by_rel = set(self.store.find(sc, f'relation_type = "{relation}"'))
                queries.append(
                    f"find '{sc}' --where 'relation_type = \"{relation}\"' → {len(by_rel)}"
                )
                hits = [a for a in hits if a in by_rel]
            found += hits
        edges = []
        for a in found:
            name = a.split("}.", 1)[1]
            d = self.store.doc(
                "RelationDoc", name, a.split(":", 1)[0] if ":st.{" in a else "local"
            )
            if d is None:
                continue
            p = d.payload
            rt = self.lex.relation_types.get(p["relation_type"], {})
            here = None if d.store_name == "local" else d.store_name
            edges.append(
                {
                    "source": qualify(p["source_id"], here),
                    "target": qualify(p["target_id"], here),
                    "relation": p["relation_type"],
                    "metadata": {
                        "origin": "relation_doc",
                        "relation_doc": name,
                        "relation_store": d.store_name,
                        "condition": p.get("condition") or rt.get("condition", ""),
                        "axis": rt.get("axis", ""),
                    },
                }
            )
        return EdgeRead(edges, "sldb", queries)

    def targets_of(self, export_id: str, relation: str) -> list[str]:
        return [e["target"] for e in self.edges_from(export_id, relation).edges]

    # -- verifying ---------------------------------------------------------------------

    def relation_type(self, name: str) -> dict[str, Any]:
        rt = self.lex.relation_types.get(name)
        if rt is None:
            raise StoreError(f"'{name}' is not a relation type of this world")
        return rt

    def applies(
        self, name: str, source_model: str, target_model: str
    ) -> tuple[bool, str]:
        rt = self.relation_type(name)
        if rt.get("source_types") and not set(self.world.family_of(source_model)) & set(
            rt["source_types"]
        ):
            return (
                False,
                f"{name} takes {', '.join(rt['source_types'])} as subject, not {source_model}",
            )
        if rt.get("target_types") and not set(self.world.family_of(target_model)) & set(
            rt["target_types"]
        ):
            return (
                False,
                f"{name} takes {', '.join(rt['target_types'])} as object, not {target_model}",
            )
        return True, ""

    def cardinality_ok(self, name: str, source: str, target: str) -> tuple[bool, str]:
        card = self.relation_type(name).get("cardinality", "many_to_many")
        if card in ("one_to_one", "many_to_one"):
            existing = [
                e
                for e in self._edges_sldb("source_id", source, name).edges
                if e["target"] != target
            ]
            if existing:
                return (
                    False,
                    f"{source} already has {name} → {existing[0]['target']} and cardinality is {card}",
                )
        if card in ("one_to_one", "one_to_many"):
            existing = [
                e
                for e in self._edges_sldb("target_id", target, name).edges
                if e["source"] != source
            ]
            if existing:
                return (
                    False,
                    f"{target} already is {name} of {existing[0]['source']} and cardinality is {card}",
                )
        return True, ""

    def condition_holds(
        self,
        condition: str,
        subject: str,
        over: str | None = None,
        overlay: dict[str, dict[str, Any]] | None = None,
    ) -> tuple[bool, str]:
        """Evaluate an sldb predicate. `{field}` takes the subject's values; the predicate runs over
        `over` (an export id) when given, else over the subject itself. `overlay` maps export ids
        to payloads a move has not written yet: those are read instead of the store, and the
        predicate over one of them goes through sldb's evaluator on that payload (spec 11 §7)."""
        if not condition.strip():
            return True, ""
        overlay = overlay or {}
        s_payload = overlay.get(subject) or self.store.payload_of(subject)
        where = BRACE_RE.sub(lambda m: str(s_payload.get(m.group(1), "")), condition)
        target = over or subject
        t_store, t_model, t_doc = split_id(target)
        if target in overlay:
            ok = (
                self.store.matches_of(target, where, overlay[target])
                if t_doc != "$created"
                else _pending_matches(
                    self.store, t_model, where, overlay[target], t_store
                )
            )
            return ok, f"where '{where}' over the pending payload of {target} (dry run)"
        sc = _scope(t_store, t_model)
        found = self.store.find(sc, where)
        query = f"find '{sc}' --where '{where}'"
        ok = any(a.endswith("}." + t_doc) for a in found)
        return ok, query

    # -- asserting -------------------------------------------------------------------

    def assert_edge(
        self, name: str, source: str, target: str, naming: str | None = None
    ) -> tuple[str, str]:
        """Create the RelationDoc for source -[name]-> target. Returns (doc name, export id)."""
        rt = self.relation_type(name)
        s_model, t_model = model_of(source), model_of(target)
        ok, why = self.applies(name, s_model, t_model)
        if not ok:
            raise StoreError(why)
        ok, why = self.cardinality_ok(name, source, target)
        if not ok:
            raise StoreError(why)
        if rt.get("condition"):
            holds, query = self.condition_holds(rt["condition"], source, over=target)
            if not holds:
                raise StoreError(
                    f"condition '{rt['condition']}' does not hold for {source} → {target} ({query})"
                )
        src, tgt = (
            relativize(source, self.write_store),
            relativize(target, self.write_store),
        )  # written as the store reads itself
        doc_name = (naming or "{relation_type}--{source_id}--{target_id}").format(
            relation_type=name, source_id=src, target_id=tgt
        )
        path = self.store.root_of(self.write_store) / "relations" / f"{doc_name}.md"
        payload = {
            "title": f"{src} {name} {tgt}",
            "source_id": src,
            "target_id": tgt,
            "relation_type": name,
            "condition": "",
            "notes": "",
        }
        return doc_name, self.store.create(
            "RelationDoc", doc_name, payload, path, self.write_store
        )

    def negate_edge(
        self, name: str, source: str, target: str
    ) -> tuple[str | None, str]:
        for e in self._edges_sldb("source_id", source, name).edges:
            if e["target"] == target:
                rel_doc = e["metadata"]["relation_doc"]
                self.store.untrack(
                    rel_doc, e["metadata"].get("relation_store", "local")
                )
                return rel_doc, "untracked"
        for e in self.edges_from(source, name).edges:
            if e["target"] == target and e["metadata"].get("origin") == "link":
                return (
                    None,
                    f"that edge is written in prose ({e['metadata']}); edit the text",
                )
        return None, "no such edge"

    # -- transitions ------------------------------------------------------------------------

    def machine(self, model: str, fld: str) -> dict[str, str]:
        """value -> State export id for Model.field, empty when the field has no state documents."""
        out: dict[str, str] = {}
        for s in self.stores:
            if "State" not in self.world.model_names(s):
                continue
            for d in self.store.docs_of("State", s):
                if d.payload.get("machine") == f"{model}.{fld}":
                    out.setdefault(
                        str(d.payload.get("name")),
                        join_id(None if s == "local" else s, "State", d.name),
                    )
        return out

    def transition(
        self,
        model: str,
        fld: str,
        subject: str,
        current: Any,
        new: Any,
        overlay: dict[str, dict[str, Any]] | None = None,
    ) -> tuple[bool, str, list[str]]:
        """Is changing Model.field from current to new legal for subject? (legal, reason, queries).
        With `overlay`, the condition is evaluated over the payload the move is about to leave."""
        states = self.machine(model, fld)
        if not states:
            return True, "no state machine on this field", []
        queries: list[str] = []
        src, tgt = states.get(str(current)), states.get(str(new))
        if src is None or tgt is None:
            return (
                False,
                f"no state document for {current!r} or {new!r} on {model}.{fld}",
                queries,
            )
        read = self._edges_sldb("source_id", src, "transitions_to")
        queries += read.queries
        edge = next((e for e in read.edges if e["target"] == tgt), None)
        if edge is None:
            return False, f"no transition {current} → {new} on {model}.{fld}", queries
        cond = edge["metadata"].get("condition", "")
        ok, q = self.condition_holds(cond, subject, overlay=overlay)
        if q:
            queries.append(q)
        if not ok:
            return (
                False,
                f"cannot go {current} → {new}: the condition is {cond}",
                queries,
            )
        return (
            True,
            f"{current} → {new} is legal" + (f" ({cond})" if cond else ""),
            queries,
        )

    # -- re-evaluation after a write ----------------------------------------------------

    def broken_conditions(self, export_id: str) -> list[str]:
        """Conditions of edges from and to a document that no longer hold."""
        warnings = []
        for e in (
            self._edges_sldb("source_id", export_id, None).edges
            + self._edges_sldb("target_id", export_id, None).edges
        ):
            cond = e["metadata"].get("condition", "")
            if not cond:
                continue
            ok, _ = self.condition_holds(cond, e["source"], over=e["target"])
            if not ok:
                warnings.append(
                    f"{e['relation']} → {e['target']} requires {cond}, which no longer holds"
                )
        return warnings


def _pending_matches(
    store, model: str, where: str, payload: dict[str, Any], in_store: str | None = None
) -> bool:
    """sldb's evaluator over a document that does not exist yet: any document of the model
    lends its runtime shape, the payload is the pending one."""
    from dataclasses import replace

    from sldb.store.query_engine.filter import DocumentFilter
    from sldb.store.query_engine.where_parse import WherePredicateError
    from sldb.cli.model_utils import resolve_model_ref

    sample = next(iter(store.docs_of(model, in_store or "local")), None) or next(
        iter(store.docs_of(model, "*")), None
    )
    if sample is None:
        return (
            True  # nothing to compare the shape against; the write itself will validate
        )
    try:
        return DocumentFilter.where_matches(
            replace(sample, name="$created", payload=payload),
            where,
            resolve_model_ref,
            store.pythonpath,
        )
    except WherePredicateError as e:
        raise StoreError(str(e)) from e


def _strip(e: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": e["source"].replace("sldb://document/", ""),
        "target": e["target"].replace("sldb://document/", ""),
        "relation": e["relation"],
        "metadata": e.get("metadata", {}),
    }
