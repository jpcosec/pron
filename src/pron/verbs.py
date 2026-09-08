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
from pron.lexicon import Lexicon
from pron.store import StoreError

BRACE_RE = re.compile(r"\{([A-Za-z_][\w]*)\}")


@dataclass
class EdgeRead:
    edges: list[dict[str, Any]]        # {source, target, relation, metadata}
    source: str                         # "graph" | "sldb"
    queries: list[str] = field(default_factory=list)


class Verbs:
    def __init__(self, lex: Lexicon):
        self.lex = lex
        self.world = lex.world
        self.store = lex.world.store

    # -- reading ------------------------------------------------------------------------

    def edges_from(self, export_id: str, relation: str | None = None) -> EdgeRead:
        if self.world.graph_is_fresh():
            edges = self.world.graph.edges_from(doc_id(export_id), relation)
            return EdgeRead([_strip(e) for e in edges], "graph", [f"kgdb edges_from({export_id}, {relation or '*'}) → {len(edges)}"])
        return self._edges_sldb("source_id", export_id, relation)

    def edges_to(self, export_id: str, relation: str | None = None) -> EdgeRead:
        if self.world.graph_is_fresh():
            edges = self.world.graph.edges_to(doc_id(export_id), relation)
            return EdgeRead([_strip(e) for e in edges], "graph", [f"kgdb edges_to({export_id}, {relation or '*'}) → {len(edges)}"])
        return self._edges_sldb("target_id", export_id, relation)

    def _edges_sldb(self, side: str, export_id: str, relation: str | None) -> EdgeRead:
        """The authored edges as documents, when the graph is absent or stale."""
        queries = []
        found = self.store.find("st.{RelationDoc}", f'{side} = "{export_id}"')
        queries.append(f"find 'st.{{RelationDoc}}' --where '{side} = \"{export_id}\"' → {len(found)} (graph not fresh)")
        if relation:
            by_rel = set(self.store.find("st.{RelationDoc}", f'relation_type = "{relation}"'))
            queries.append(f"find 'st.{{RelationDoc}}' --where 'relation_type = \"{relation}\"' → {len(by_rel)}")
            found = [a for a in found if a in by_rel]
        edges = []
        for a in found:
            name = a.split("}.", 1)[1]
            d = self.store.doc("RelationDoc", name)
            if d is None:
                continue
            p = d.payload
            rt = self.lex.relation_types.get(p["relation_type"], {})
            edges.append({"source": p["source_id"], "target": p["target_id"], "relation": p["relation_type"],
                          "metadata": {"origin": "relation_doc", "relation_doc": name, "condition": p.get("condition") or rt.get("condition", ""), "axis": rt.get("axis", "")}})
        return EdgeRead(edges, "sldb", queries)

    def targets_of(self, export_id: str, relation: str) -> list[str]:
        return [e["target"] for e in self.edges_from(export_id, relation).edges]

    # -- verifying ---------------------------------------------------------------------

    def relation_type(self, name: str) -> dict[str, Any]:
        rt = self.lex.relation_types.get(name)
        if rt is None:
            raise StoreError(f"'{name}' is not a relation type of this world")
        return rt

    def applies(self, name: str, source_model: str, target_model: str) -> tuple[bool, str]:
        rt = self.relation_type(name)
        if rt.get("source_types") and not set(self.world.family_of(source_model)) & set(rt["source_types"]):
            return False, f"{name} takes {', '.join(rt['source_types'])} as subject, not {source_model}"
        if rt.get("target_types") and not set(self.world.family_of(target_model)) & set(rt["target_types"]):
            return False, f"{name} takes {', '.join(rt['target_types'])} as object, not {target_model}"
        return True, ""

    def cardinality_ok(self, name: str, source: str, target: str) -> tuple[bool, str]:
        card = self.relation_type(name).get("cardinality", "many_to_many")
        if card in ("one_to_one", "many_to_one"):
            existing = [e for e in self._edges_sldb("source_id", source, name).edges if e["target"] != target]
            if existing:
                return False, f"{source} already has {name} → {existing[0]['target']} and cardinality is {card}"
        if card in ("one_to_one", "one_to_many"):
            existing = [e for e in self._edges_sldb("target_id", target, name).edges if e["source"] != source]
            if existing:
                return False, f"{target} already is {name} of {existing[0]['source']} and cardinality is {card}"
        return True, ""

    def condition_holds(self, condition: str, subject: str, over: str | None = None) -> tuple[bool, str]:
        """Evaluate an sldb predicate. `{field}` takes the subject's values; the predicate runs over
        `over` (an export id) when given, else over the subject itself."""
        if not condition.strip():
            return True, ""
        s_model, s_doc = subject.split(":", 1)
        s_payload = self.store.payload(s_model, s_doc)
        where = BRACE_RE.sub(lambda m: str(s_payload.get(m.group(1), "")), condition)
        target = over or subject
        t_model, t_doc = target.split(":", 1)
        found = self.store.find(f"st.{{{t_model}+}}", where)
        query = f"find 'st.{{{t_model}+}}' --where '{where}'"
        ok = any(a.endswith("}." + t_doc) for a in found)
        return ok, query

    # -- asserting -------------------------------------------------------------------

    def assert_edge(self, name: str, source: str, target: str, naming: str | None = None) -> tuple[str, str]:
        """Create the RelationDoc for source -[name]-> target. Returns (doc name, export id)."""
        rt = self.relation_type(name)
        s_model, t_model = source.split(":", 1)[0], target.split(":", 1)[0]
        ok, why = self.applies(name, s_model, t_model)
        if not ok:
            raise StoreError(why)
        ok, why = self.cardinality_ok(name, source, target)
        if not ok:
            raise StoreError(why)
        if rt.get("condition"):
            holds, query = self.condition_holds(rt["condition"], source, over=target)
            if not holds:
                raise StoreError(f"condition '{rt['condition']}' does not hold for {source} → {target} ({query})")
        doc_name = (naming or "{relation_type}--{source_id}--{target_id}").format(relation_type=name, source_id=source, target_id=target)
        path = self.world.root / "relations" / f"{doc_name}.md"
        payload = {"title": f"{source} {name} {target}", "source_id": source, "target_id": target, "relation_type": name, "condition": "", "notes": ""}
        return doc_name, self.store.create("RelationDoc", doc_name, payload, path)

    def negate_edge(self, name: str, source: str, target: str) -> tuple[str | None, str]:
        for e in self._edges_sldb("source_id", source, name).edges:
            if e["target"] == target:
                rel_doc = e["metadata"]["relation_doc"]
                self.store.untrack(rel_doc)
                return rel_doc, "untracked"
        for e in self.edges_from(source, name).edges:
            if e["target"] == target and e["metadata"].get("origin") == "link":
                return None, f"that edge is written in prose ({e['metadata']}); edit the text"
        return None, "no such edge"

    # -- transitions ------------------------------------------------------------------------

    def machine(self, model: str, fld: str) -> dict[str, str]:
        """value -> State export id for Model.field, empty when the field has no state documents."""
        if "State" not in self.world.model_names():
            return {}
        out = {}
        for d in self.store.docs_of("State"):
            if d.payload.get("machine") == f"{model}.{fld}":
                out[str(d.payload.get("name"))] = f"State:{d.name}"
        return out

    def transition(self, model: str, fld: str, subject: str, current: str, new: str) -> tuple[bool, str, list[str]]:
        """Is changing Model.field from current to new legal for subject? (legal, reason, queries)."""
        states = self.machine(model, fld)
        if not states:
            return True, "no state machine on this field", []
        queries = []
        src, tgt = states.get(str(current)), states.get(str(new))
        if src is None or tgt is None:
            return False, f"no state document for {current!r} or {new!r} on {model}.{fld}", queries
        read = self._edges_sldb("source_id", src, "transitions_to")
        queries += read.queries
        edge = next((e for e in read.edges if e["target"] == tgt), None)
        if edge is None:
            return False, f"no transition {current} → {new} on {model}.{fld}", queries
        cond = edge["metadata"].get("condition", "")
        ok, q = self.condition_holds(cond, subject)
        if q: queries.append(q)
        if not ok:
            return False, f"cannot go {current} → {new}: the condition is {cond}", queries
        return True, f"{current} → {new} is legal" + (f" ({cond})" if cond else ""), queries

    # -- re-evaluation after a write ----------------------------------------------------

    def broken_conditions(self, export_id: str) -> list[str]:
        """Conditions of edges from and to a document that no longer hold."""
        warnings = []
        for e in self._edges_sldb("source_id", export_id, None).edges + self._edges_sldb("target_id", export_id, None).edges:
            cond = e["metadata"].get("condition", "")
            if not cond:
                continue
            ok, _ = self.condition_holds(cond, e["source"], over=e["target"])
            if not ok:
                warnings.append(f"{e['relation']} → {e['target']} requires {cond}, which no longer holds")
        return warnings


def _strip(e: dict[str, Any]) -> dict[str, Any]:
    return {"source": e["source"].replace("sldb://document/", ""), "target": e["target"].replace("sldb://document/", ""), "relation": e["relation"], "metadata": e.get("metadata", {})}
