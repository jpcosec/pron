"""Atom-compliance tests: each test targets one atom and proves its claim.

The test id carries the atom id. If a test fails, either the code drifted from
the knowledge or the atom overclaims — both are defects. This operationalizes
atom-clean-code-reduces-knowledge-drift.

Run: PYTHONPATH=src pytest tests/test_atom_compliance.py -q
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

ATOMS = ROOT / "knowledge" / "atoms"


def atom_exists(atom_id: str) -> None:
    """Every compliance test first proves its atom is real and impl:here."""
    path = ATOMS / f"{atom_id}.md"
    assert path.exists(), f"atom {atom_id} missing"
    text = path.read_text()
    assert "impl:here" in text, f"{atom_id} is not marked impl:here"


# ── atom-sexpr-serialization-quotes-selectors-and-roundtrips ────────────────


def test_atom_sexpr_serialization_quotes_selectors_and_roundtrips():
    atom_exists("atom-sexpr-serialization-quotes-selectors-and-roundtrips")
    from knowledge.core.sexpr import parse, serialize

    cases = [
        '(check (doc atom "atom-x") :project title)',
        '(check (rel tagged (doc atom "with \\"quotes\\"")))',
        '(next (docs task) :where "has(status)" :project summary)',
        '(check (common (doc book "a") (doc book "b")))',
    ]
    for text in cases:
        assert serialize(parse(text)) == text


# ── atom-sexpr-py-is-the-dependency-free-meaning-kernel ─────────────────────


def test_atom_sexpr_py_is_the_dependency_free_meaning_kernel():
    atom_exists("atom-sexpr-py-is-the-dependency-free-meaning-kernel")
    source = (ROOT / "src/knowledge/core/sexpr.py").read_text()
    tree = ast.parse(source)
    imports = [
        node.module if isinstance(node, ast.ImportFrom) else alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in (node.names if isinstance(node, ast.Import) else [None])
    ]
    project_imports = [i for i in imports if i and "knowledge" in str(i)]
    assert not project_imports, (
        f"sexpr.py must import nothing from the project: {project_imports}"
    )


# ── atom-resolution-outcomes-are-typed-values-not-exceptions ────────────────


def test_atom_resolution_outcomes_are_typed_values_not_exceptions():
    atom_exists("atom-resolution-outcomes-are-typed-values-not-exceptions")
    from knowledge.core.results import Ambiguous, Missing, Resolved
    from knowledge.core.resolution import resolve_noun

    class FakeDoc:
        def __init__(self, name, title=""):
            self.name, self.model_name, self.path = name, "M", name
            self.payload = {"title": title}
            self.semantic_tags = []

    class FakeBridge:
        def __init__(self, docs):
            self._d = docs

        def documents_of_model(self, m):
            return self._d

    docs = [FakeDoc("doc-a", "Alpha"), FakeDoc("doc-ab", "Beta")]
    assert isinstance(resolve_noun(FakeBridge(docs), "M", "doc-a", "m"), Resolved)
    assert isinstance(resolve_noun(FakeBridge(docs), "M", "doc-", "m"), Ambiguous)
    assert isinstance(resolve_noun(FakeBridge(docs), "M", "zzz", "m"), Missing)
    assert isinstance(resolve_noun(FakeBridge([]), "M", "x", "m"), Missing)


# ── atom-resolution-py-implements-the-selector-cascade ──────────────────────


def test_atom_resolution_py_implements_the_selector_cascade():
    atom_exists("atom-resolution-py-implements-the-selector-cascade")
    from knowledge.core.resolution import resolve_noun

    class FakeDoc:
        def __init__(self, name, title="", tags=()):
            self.name, self.model_name, self.path = name, "M", name
            self.payload = {"title": title}
            self.semantic_tags = list(tags)

    class FakeBridge:
        def __init__(self, docs):
            self._d = docs

        def documents_of_model(self, m):
            return self._d

    docs = [
        FakeDoc("doc-exact", "Exact Title"),
        FakeDoc("doc-tagged", "Other", tags=["k:v"]),
        FakeDoc("doc-substr", "Unique Needle Here"),
    ]
    b = FakeBridge(docs)
    assert resolve_noun(b, "M", "doc-exact", "m").name == "doc-exact"  # name
    assert resolve_noun(b, "M", "Exact Title", "m").name == "doc-exact"  # title
    assert resolve_noun(b, "M", "doc-e", "m").name == "doc-exact"  # prefix
    assert resolve_noun(b, "M", "k:v", "m").name == "doc-tagged"  # semantic tag
    assert resolve_noun(b, "M", "Needle", "m").name == "doc-substr"  # substring


# ── atom-session-expires-by-ttl-and-store-hash ──────────────────────────────


def test_atom_session_expires_by_ttl_and_store_hash(tmp_path):
    atom_exists("atom-session-expires-by-ttl-and-store-hash")
    import time
    from knowledge.core import session as mod
    from knowledge.core.session import Session

    s = Session(tmp_path, store_hash="h1")
    s.save("(check _)", ["a", "b"])
    assert s.load()["candidates"] == ["a", "b"]

    # store hash change invalidates
    s2 = Session(tmp_path, store_hash="h2")
    assert s2.load() is None
    assert not s2.path.exists()

    # TTL expiry invalidates
    s.save("(check _)", ["a"])
    import json as j

    raw = j.loads(s.path.read_text())
    raw["created_at"] = time.time() - mod.TTL_SECONDS - 60
    s.path.write_text(j.dumps(raw))
    assert s.load() is None


# ── atom-bridges-are-the-only-doors-to-sldb-and-kgdb ────────────────────────


def test_atom_bridges_are_the_only_doors_to_sldb_and_kgdb():
    atom_exists("atom-bridges-are-the-only-doors-to-sldb-and-kgdb")
    offenders = []
    for py in (ROOT / "src/knowledge").rglob("*.py"):
        if "bridges" in py.parts:
            continue
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            module = getattr(node, "module", "") or ""
            names = [a.name for a in getattr(node, "names", [])]
            if (
                module.startswith("sldb")
                or module.startswith("kgdb")
                or any(n.startswith(("sldb", "kgdb")) for n in names)
            ):
                offenders.append(str(py.relative_to(ROOT)))
    assert not offenders, f"sldb/kgdb imported outside bridges: {offenders}"


# ── atom-one-file-one-component-one-motive ──────────────────────────────────


def test_atom_one_file_one_component_one_motive():
    atom_exists("atom-one-file-one-component-one-motive")
    expected = {
        "core/sexpr.py",
        "core/anchors.py",
        "core/resolution.py",
        "core/session.py",
        "core/evaluator.py",
        "core/results.py",
        "ops/read.py",
        "bridges/sldb_bridge.py",
        "bridges/kgdb_bridge.py",
        "infra/projector.py",
        "cli/surface.py",
        "cli/render.py",
        "cli/main.py",
    }
    src = ROOT / "src/knowledge"
    actual = {
        str(p.relative_to(src))
        for p in src.rglob("*.py")
        if p.name not in ("__init__.py", "__main__.py", "knowledge_legacy.py")
    }
    assert expected <= actual, f"missing components: {expected - actual}"
    for rel in expected:
        first_line = (src / rel).read_text().lstrip().splitlines()[0]
        assert first_line.startswith('"""'), f"{rel} lacks a motive docstring"


# ── atom-unanchored-symbols-fail-with-an-explicit-semantic-error ────────────


def test_atom_unanchored_symbols_fail_with_an_explicit_semantic_error():
    atom_exists("atom-unanchored-symbols-fail-with-an-explicit-semantic-error")
    from knowledge.core.anchors import AnchorRegistry
    from knowledge.core.results import SemanticError

    class EmptyBridge:
        def documents_of_model(self, m):
            return []

    err = AnchorRegistry(EmptyBridge()).lookup("frobnicate")
    assert isinstance(err, SemanticError)
    assert "frobnicate" in err.message
    assert "anchor add" in err.hint  # actionable next step


# ── atom-anchor-ref-is-a-typed-string-with-a-scheme-per-kind ────────────────


def test_atom_anchor_ref_is_a_typed_string_with_a_scheme_per_kind():
    atom_exists("atom-anchor-ref-is-a-typed-string-with-a-scheme-per-kind")
    sys.path.insert(0, "/home/jp/proyectos/hum-ecosystem/tools/sldb/src")
    from sldb.models.knowledge_surface import AnchorDoc

    ok = [
        ("model", "model:UserDoc"),
        ("doc", "doc:atom-x"),
        ("relation", "edge:tagged_as"),
        ("relation", "edge:follows:in"),
        ("operation", "op:check"),
        ("projection", "fields:id,title"),
        ("projection", "view:summary"),
        ("expr", "expr:(rel tagged _)"),
    ]
    for kind, ref in ok:
        AnchorDoc(id="a", symbol="s", kind=kind, ref=ref, motive="m")
    import pydantic

    with pytest.raises(pydantic.ValidationError):
        AnchorDoc(id="a", symbol="s", kind="model", ref="not-a-scheme", motive="m")


# ── atom-expr-anchors-declare-derived-relations-neither-store-can-hold ──────


def test_atom_expr_anchors_declare_derived_relations():
    atom_exists("atom-expr-anchors-declare-derived-relations-neither-store-can-hold")
    from knowledge.core.evaluator import _fill
    from knowledge.core.sexpr import parse, serialize

    template = parse("(common (doc atom _) (doc atom _))")
    filled = _fill(template, iter(["a", "b"]))
    assert serialize(filled) == '(common (doc atom "a") (doc atom "b"))'


# ── atom-render-py-maps-result-values-to-output-and-exit-codes ──────────────


def test_atom_render_py_maps_result_values_to_output_and_exit_codes():
    atom_exists("atom-render-py-maps-result-values-to-output-and-exit-codes")
    from knowledge.cli.render import render
    from knowledge.core.results import (
        Ambiguous,
        Missing,
        OperationResult,
        SemanticError,
    )

    assert render(OperationResult(status="ok"))[1] == 0
    assert render(OperationResult(status="error"))[1] == 1
    assert render(Ambiguous(question="?", candidates=["a"]))[1] == 2
    assert render(Missing(motive="m", nearest=[]))[1] == 1
    assert render(SemanticError(symbol="x", message="m"))[1] == 1


# ── atom-every-read-response-carries-refs-for-auditability ──────────────────


def test_atom_every_read_response_carries_refs_for_auditability():
    atom_exists("atom-every-read-response-carries-refs-for-auditability")
    from knowledge.core.results import OperationResult, Resolved
    from knowledge.ops import read

    doc = Resolved(name="d", model="M", path="p.md", payload={"title": "T"})

    class Doc:
        name, model_name, path = "d", "M", "p.md"
        payload = {"title": "T", "status": "active"}

    for fn, arg in (
        (read.check, doc),
        (read.return_, doc),
        (read.next_, {"kind": "docs", "docs": [Doc()]}),
    ):
        result = fn(None, [arg], None)
        assert isinstance(result, OperationResult)
        assert result.refs, f"{fn.__name__} returned no refs"


# ── atom-kgdb-bridge-py-guards-staleness-before-serving-graph-reads ─────────


def test_atom_kgdb_bridge_guards_staleness(tmp_path):
    atom_exists("atom-kgdb-bridge-py-guards-staleness-before-serving-graph-reads")
    import json
    from knowledge.bridges.kgdb_bridge import GRAPH_RELPATH, KgdbBridge

    graph = tmp_path / GRAPH_RELPATH
    graph.parent.mkdir(parents=True)
    graph.write_text(
        json.dumps(
            {
                "nodes": [
                    {
                        "id": "n1",
                        "schema": {"source": {"store": {"hash_a": "old-hash"}}},
                    }
                ]
            }
        )
    )
    bridge = KgdbBridge(tmp_path)
    assert bridge.is_stale("new-hash") is True
    assert bridge.is_stale("old-hash") is False


# ── atom-where-values-must-be-quoted-or-numeric ─────────────────────────────


def test_atom_where_values_must_be_quoted_or_numeric():
    atom_exists("atom-where-values-must-be-quoted-or-numeric")
    sys.path.insert(0, "/home/jp/proyectos/hum-ecosystem/tools/sldb/src")
    from sldb.store.query_engine.filter import DocumentFilter

    class Doc:
        payload = {"status": "active"}
        name = "d"

    assert DocumentFilter.where_matches(Doc(), 'status = "active"', None, None)
    assert not DocumentFilter.where_matches(Doc(), "status = active", None, None)


# ── atom-the-anchor-table-is-declared-as-sldb-documents-not-code ────────────


def test_atom_the_anchor_table_is_declared_as_sldb_documents_not_code():
    atom_exists("atom-the-anchor-table-is-declared-as-sldb-documents-not-code")
    # no hardcoded grammar table anywhere in src/
    for py in (ROOT / "src/knowledge").rglob("*.py"):
        text = py.read_text()
        assert "ANCHORS = [" not in text and "ANCHORS=[" not in text, (
            f"hardcoded anchor table in {py}"
        )
    # and the repo's grammar exists as tracked documents
    anchors_dir = ROOT / "knowledge" / "anchors"
    assert len(list(anchors_dir.glob("anchor-*.md"))) >= 10
