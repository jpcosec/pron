"""Wrapper tests: knowledge as a generic semantic layer over sldb+kgdb.

Builds an ephemeral KB (library domain: authors/books) from scratch inside the
test — models, data, and grammar all declared by the fixture. No atoms, no
dependency on this repo's store. This is the product test: any app should get
this exact behavior by declaring its own models and anchors.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

KNOWLEDGE_SRC = str(Path(__file__).resolve().parent.parent / "src")
SLDB_SRC = "/home/jp/proyectos/hum-ecosystem/tools/sldb/src"

MODELS = textwrap.dedent('''
    """Library domain models for the wrapper test."""
    from pydantic import Field

    from sldb import StructuredNLDoc


    class AuthorDoc(StructuredNLDoc):
        """A registered author."""

        __semantics__ = {"type": ["library", "author"], "workspace": ["kb", "authors"]}
        __template__ = """---
    id: ⸢rev•id⸥
    name: ⸢rev•name⸥
    tags: ⸢rev•tags⸥
    ---

    # ⸢render•name⸥

    ## Bio

    ⸢rev•bio⸥
    """.strip()

        id: str = Field(description="Stable id 'author-<slug>'.")
        name: str = Field(description="Display name.")
        bio: str = Field(description="Short bio.")
        tags: list[str] = Field(default_factory=list, description="Semantic tags.")


    class BookDoc(StructuredNLDoc):
        """A book written by an author."""

        __semantics__ = {"type": ["library", "book"], "workspace": ["kb", "books"]}
        __template__ = """---
    id: ⸢rev•id⸥
    title: ⸢rev•title⸥
    author: ⸢rev•author⸥
    status: ⸢rev•status⸥
    tags: ⸢rev•tags⸥
    ---

    # ⸢render•title⸥

    ## Synopsis

    ⸢rev•synopsis⸥
    """.strip()

        id: str = Field(description="Stable id 'book-<slug>'.")
        title: str = Field(description="Book title.")
        author: str = Field(description="author id (foreign key).")
        status: str = Field(description="pending | active | done.")
        synopsis: str = Field(description="One-line synopsis.")
        tags: list[str] = Field(default_factory=list, description="Semantic tags.")
''')

AUTHORS = [
    {
        "id": "author-gabriel-garcia",
        "name": "Gabriel García",
        "bio": "Realismo mágico.",
        "tags": ["lang:es"],
    },
    {
        "id": "author-gabriel-mistral",
        "name": "Gabriel Mistral",
        "bio": "Homónimo de prueba.",
        "tags": ["lang:es"],
    },
    {
        "id": "author-ursula",
        "name": "Ursula K. Le Guin",
        "bio": "Ciencia ficción.",
        "tags": ["lang:en"],
    },
]

BOOKS = [
    {
        "id": "book-cien-anos",
        "title": "Cien años de soledad",
        "author": "author-gabriel-garcia",
        "status": "done",
        "synopsis": "Macondo.",
        "tags": ["genre:novel"],
    },
    {
        "id": "book-otono",
        "title": "El otoño del patriarca",
        "author": "author-gabriel-garcia",
        "status": "active",
        "synopsis": "El dictador.",
        "tags": ["genre:novel"],
    },
    {
        "id": "book-dispossessed",
        "title": "The Dispossessed",
        "author": "author-ursula",
        "status": "pending",
        "synopsis": "Anarres y Urras.",
        "tags": ["genre:scifi"],
    },
]

ANCHORS = [
    ("check", "operation", "op:check", "Leer sin mutar."),
    ("next", "operation", "op:next", "El siguiente libro por estado."),
    ("show", "operation", "op:check", "Mostrar un documento."),
    ("list", "operation", "op:check", "Listar documentos."),
    ("author", "model", "model:AuthorDoc", "Un autor registrado."),
    ("book", "model", "model:BookDoc", "Un libro con autor y estado."),
    ("title", "projection", "fields:title", "Solo el título."),
    ("summary", "projection", "view:summary", "Vista resumida."),
    ("tagged", "relation", "edge:tagged_as", "Los tags de grafo de un documento."),
    (
        "works",
        "expr",
        "expr:(filter-by book author (doc author _))",
        "Los libros escritos por un autor: join por foreign key, no existe como edge.",
    ),
    (
        "shared",
        "expr",
        "expr:(common (doc book _) (doc book _))",
        "Lo que dos libros comparten en el grafo.",
    ),
]


def sh(cwd: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run(
        list(args),
        capture_output=True,
        text=True,
        cwd=cwd,
        env={**os.environ, "PYTHONPATH": KNOWLEDGE_SRC},
    )
    return r.returncode, (r.stdout or r.stderr)


def krun(kb: Path, *args: str) -> tuple[int, dict | str]:
    code, out = sh(kb, sys.executable, "-m", "pron", *args)
    try:
        return code, json.loads(out)
    except json.JSONDecodeError:
        return code, out


@pytest.fixture(scope="module")
def kb(tmp_path_factory) -> Path:
    """A fully declared KB knowledge has never seen: models + data + grammar."""
    root = tmp_path_factory.mktemp("library-kb")
    (root / "models.py").write_text(MODELS)

    assert (
        sh(root, sys.executable, "-m", "sldb", "stores", "init", "--path", ".")[0] == 0
    )
    for model in ("models:AuthorDoc", "models:BookDoc"):
        assert (
            sh(
                root,
                sys.executable,
                "-m",
                "sldb",
                "models",
                "add",
                model,
                "--store",
                ".sldb",
                "--pythonpath",
                ".",
            )[0]
            == 0
        )
    assert (
        sh(
            root,
            sys.executable,
            "-m",
            "sldb",
            "models",
            "add",
            "sldb.models.knowledge_surface:AnchorDoc",
            "--store",
            ".sldb",
            "--pythonpath",
            SLDB_SRC,
        )[0]
        == 0
    )

    for sub, model, rows in (
        ("authors", "AuthorDoc", AUTHORS),
        ("books", "BookDoc", BOOKS),
    ):
        (root / sub).mkdir()
        for row in rows:
            payload = root / "payload.json"
            payload.write_text(json.dumps(row))
            code, out = sh(
                root,
                sys.executable,
                "-m",
                "sldb",
                "docs",
                "create",
                "--model",
                model,
                "-o",
                f"{sub}/{row['id']}.md",
                str(payload),
                "--store",
                ".sldb",
                "--pythonpath",
                ".",
            )
            assert code == 0, out

    (root / "anchors").mkdir()
    for symbol, kind, ref, motive in ANCHORS:
        payload = root / "payload.json"
        payload.write_text(
            json.dumps(
                {
                    "id": f"anchor-{symbol}",
                    "symbol": symbol,
                    "kind": kind,
                    "ref": ref,
                    "motive": motive,
                    "tags": ["entity:anchor"],
                }
            )
        )
        code, out = sh(
            root,
            sys.executable,
            "-m",
            "sldb",
            "docs",
            "create",
            "--model",
            "AnchorDoc",
            "-o",
            f"anchors/anchor-{symbol}.md",
            str(payload),
            "--store",
            ".sldb",
            "--pythonpath",
            SLDB_SRC,
        )
        assert code == 0, out

    assert (
        sh(
            root,
            sys.executable,
            "-m",
            "sldb",
            "stores",
            "update",
            "--store",
            ".sldb",
            "--pythonpath",
            ".",
        )[0]
        == 0
    )
    code, out = krun(root, "project")
    assert code == 0, out
    return root


def _clear_session(kb: Path) -> None:
    (kb / ".pron" / "session.json").unlink(missing_ok=True)


def test_grammar_is_declared_data(kb):
    code, out = krun(kb, "anchors")
    assert code == 0
    symbols = {a["symbol"]: a for a in out["payload"]}
    assert {"check", "book", "works", "shared"} <= set(symbols)
    assert symbols["works"]["kind"] == "expr"
    assert symbols["works"]["motive"]


def test_unique_resolution_with_refs(kb):
    _clear_session(kb)
    code, out = krun(kb, "show", "book", "book-cien-anos", "--title")
    assert code == 0
    assert out["payload"] == {"title": "Cien años de soledad"}
    assert out["refs"] == ["books/book-cien-anos.md"]


def test_ambiguity_then_clarification(kb):
    _clear_session(kb)
    code, out = krun(kb, "show", "author", "gabriel")
    assert code == 2 and out["status"] == "ambiguous"
    assert set(out["candidates"]) == {"author-gabriel-garcia", "author-gabriel-mistral"}

    code, out = krun(kb, "author-gabriel-garcia")
    assert code == 0
    assert out["payload"]["name"] == "Gabriel García"


def test_missing_offers_nearest(kb):
    _clear_session(kb)
    code, out = krun(kb, "show", "author", "ursulla")
    assert code == 1 and out["status"] == "missing"
    assert "author-ursula" in out["nearest"]


def test_unanchored_symbol_is_semantic_error(kb):
    _clear_session(kb)
    code, out = krun(kb, "devour", "book")
    assert code == 1 and out["status"] == "semantic_error"
    assert "devour" in out["symbol"]


def test_derived_relation_foreign_key(kb):
    """works: a relation held by neither store, declared as grammar."""
    _clear_session(kb)
    code, out = krun(kb, "author", "garcia", "check", "works", "--title")
    assert code == 0
    titles = {p["title"] for p in out["payload"]}
    assert titles == {"Cien años de soledad", "El otoño del patriarca"}


def test_where_uses_sldb_engine(kb):
    _clear_session(kb)
    code, out = krun(kb, "list", "book", "--where", 'status = "active"', "--title")
    assert code == 0
    assert out["payload"] == [{"title": "El otoño del patriarca"}]


def test_next_by_status(kb):
    _clear_session(kb)
    code, out = krun(kb, "next", "book", "--summary")
    assert code == 0
    assert (
        out["payload"]["id"] == "book-otono"
    )  # active outranks pending; done excluded


def test_eval_equals_surface(kb):
    _clear_session(kb)
    _, surface = krun(kb, "show", "book", "book-dispossessed", "--title")
    _, meaning = krun(
        kb, "eval", '(check (doc book "book-dispossessed") :project title)'
    )
    assert surface["payload"] == meaning["payload"]


def test_graph_relation_traversal(kb):
    _clear_session(kb)
    code, out = krun(kb, "book", "book-cien-anos", "check", "tagged")
    assert code == 0
    tags = {p.get("tag") for p in out["payload"]}
    assert "type.library.book" in tags


def test_set_combinator_shared(kb):
    _clear_session(kb)
    code, out = krun(kb, "eval", '(check (shared "book-cien-anos" "book-otono"))')
    assert code == 0
    # two books of the same model share at least the model node and type tag
    assert any("type.library.book" in str(p) for p in out["payload"])


def test_staleness_guard_then_reproject(kb):
    """Mutating the store makes graph reads refuse stale answers until project."""
    _clear_session(kb)
    payload = kb / "payload.json"
    payload.write_text(
        json.dumps(
            {
                "id": "book-late",
                "title": "Libro tardío",
                "author": "author-ursula",
                "status": "pending",
                "synopsis": "Nuevo.",
                "tags": [],
            }
        )
    )
    assert (
        sh(
            kb,
            sys.executable,
            "-m",
            "sldb",
            "docs",
            "create",
            "--model",
            "BookDoc",
            "-o",
            "books/book-late.md",
            str(payload),
            "--store",
            ".sldb",
            "--pythonpath",
            ".",
        )[0]
        == 0
    )
    assert (
        sh(
            kb,
            sys.executable,
            "-m",
            "sldb",
            "stores",
            "update",
            "--store",
            ".sldb",
            "--pythonpath",
            ".",
        )[0]
        == 0
    )

    code, out = krun(kb, "book", "book-cien-anos", "check", "tagged")
    assert code == 1
    assert "desactualizado" in str(out["payload"])

    assert krun(kb, "project")[0] == 0
    code, out = krun(kb, "book", "book-cien-anos", "check", "tagged")
    assert code == 0
