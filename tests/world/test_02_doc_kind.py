"""What pron does with a model's documents, declared once (spec 05, 07, 10, 12 §5b): the
registry answers by model name, a world's models get the default, and every caller that
used to read one of the five old constants asks the registry directly now."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from pron.corpus import IndexProjection
from pron.world import doc_kind
from pron.world.doc_kind import DocKind, kind_of
from pron.world.graph import Graph

BOOKKEEPING = {"RelationTypeDoc", "RelationDoc", "ProjectionDoc", "AnchorDoc"}


def test_a_model_of_the_world_gets_the_default_kind():
    assert kind_of("Table") == DocKind("Table")
    k = kind_of("Table")
    assert k.in_graph and k.in_lexicon and k.suggests_values and k.in_corpus
    assert not k.is_ledger and k.type_tag is None


def test_pron_declares_only_its_bookkeeping_models():
    assert {k.model for k in doc_kind.declared()} == BOOKKEEPING | {"MoveDoc"}
    for model in BOOKKEEPING:
        k = kind_of(model)
        assert not k.in_lexicon and not k.suggests_values
        assert k.in_graph and k.in_corpus and not k.is_ledger


def test_the_ledger_is_a_word_but_no_node_and_no_source_of_values():
    k = kind_of("MoveDoc")
    assert k.is_ledger and k.in_lexicon
    assert not k.in_graph and not k.suggests_values
    assert doc_kind.ledger_model() == "MoveDoc"


def test_the_tag_left_out_of_the_graph_is_the_one_move_doc_carries():
    from pron.models.move import MoveDoc

    family, leaf = MoveDoc.__semantics__["type"]
    assert doc_kind.tags_outside_graph() == (f"type.{family}.{leaf}",)


def test_the_five_old_constants_are_gone():
    import pron.world.lexicon_parts.vocabulary as vocabulary

    assert not hasattr(vocabulary, "INTERNAL_MODELS")
    assert not hasattr(vocabulary, "UNSUGGESTED_MODELS")
    # graph_file.py (LEDGER_MODEL's old home) no longer exists at all: reading the typed
    # graph is sldb.api.load_edge_index now, and LEDGER_MODEL moved to WorldFingerprint's
    # only other caller, ledger_model() itself.
    import importlib

    import pytest

    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("pron.world.graph_file")
    # no tuple baked in at import time: Graph resolves exclude_tags from DocKind each call
    assert Graph.__init__.__defaults__ == (None,)


def test_a_projection_with_no_models_admits_what_doc_kind_puts_in_the_corpus(
    monkeypatch,
):
    assert IndexProjection().admits("Table") and IndexProjection().admits("MoveDoc")
    monkeypatch.setitem(doc_kind._DECLARED, "Table", DocKind("Table", in_corpus=False))
    assert not IndexProjection().admits("Table")
    assert IndexProjection.of(models=["Table"]).admits("Table")


def test_asking_the_registry_imports_no_model_class():
    code = "import sys, pron, pron.world.doc_kind, pron.world.doc_id; print('pydantic' in sys.modules, 'sldb' in sys.modules)"
    env = {**os.environ, "PYTHONPATH": str(Path(doc_kind.__file__).parents[2])}
    out = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    assert out.stdout.split() == ["False", "False"]
