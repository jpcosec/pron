"""Characterization (golden master, spec 08): what each pron command does — exit code, stdout,
stderr, or the exception that escapes — for a normal invocation and an error one. Not the help
text nor the argument parser's wording: those belong to the parser, not to pron."""

from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import patch

import pytest
import test_05_cli_docs_lints as cli_docs_lints
from sldb.cli import main as sldb_main

from golden.cli import invoke
from golden.normalize import Normalizer
from golden.run import NOW, restaurant
from pron.cli.repl import run as repl
from pron.serve import Server

own = cli_docs_lints.own  # pron's own knowledge base, built from this repo
PRON_REPO = str(cli_docs_lints.PRON_REPO)


def _on(world_root, pythonpath) -> list[list[str]]:
    at = ["--world", str(world_root), "--pythonpath", str(pythonpath)]
    return [
        ["say", "the large tables", *at, "--trace", "--now", NOW, "--local"],
        ["say", "create a client named Zoe Lee, phone 1", *at, "--now", NOW, "--local"],
        [
            "eval",
            '(show (find Table (where "capacity >= 6")))',
            *at,
            "--trace",
            "--local",
        ],
        ["eval", "(show", *at, "--local"],
        ["lexicon", "Table", *at],
        ["check", *at],
        ["refresh", *at],
        ["docs", "--check", *at],  # a world without pron's knowledge models
    ]


def test_commands_on_a_world(tmp_path, capsys, snapshot):
    world, _ = restaurant(tmp_path)
    norm = Normalizer(tmp_path)
    runs = [invoke(argv, capsys, norm) for argv in _on(world.root, tmp_path)]
    assert runs == snapshot


@pytest.mark.parametrize(
    "argv",
    [
        ["say", "the tables"],
        ["eval", "(show (all Table))"],
        ["lexicon"],
        ["check"],
        ["refresh"],
        ["init"],
        ["docs", "--check"],
        ["repl"],
    ],
    ids=lambda argv: argv[0],
)
def test_a_world_that_does_not_exist(tmp_path, capsys, snapshot, argv):
    nowhere = ["--world", str(tmp_path / "nowhere"), "--pythonpath", str(tmp_path)]
    assert invoke([*argv, *nowhere], capsys, Normalizer(tmp_path)) == snapshot


@pytest.mark.parametrize(
    "argv",
    [[], ["nonsense"], ["say"], ["eval"], ["serve"], ["lexicon", "--projection"]],
    ids=lambda argv: " ".join(argv) or "nothing",
)
def test_usage_errors(tmp_path, capsys, snapshot, argv):
    assert invoke(argv, capsys, Normalizer(tmp_path)) == snapshot


def test_init_a_store(tmp_path, capsys, snapshot):
    assert sldb_main(["stores", "init", "--path", str(tmp_path / "fresh")]) == 0
    argv = ["init", "--world", str(tmp_path / "fresh"), "--pythonpath", str(tmp_path)]
    runs = [invoke(argv, capsys, Normalizer(tmp_path)) for _ in range(2)]  # idempotent
    assert runs == snapshot


def test_docs_and_check_on_pron_own_knowledge_base(own, capsys, snapshot):
    from pron.docs import synchronize_docs

    synchronize_docs(own)
    at = ["--world", str(own.root), "--pythonpath", PRON_REPO]
    norm = Normalizer(own.root.parent, repo=PRON_REPO)
    runs = [
        invoke([cmd, *extra, *at], capsys, norm)
        for cmd, *extra in (["docs", "--check"], ["check"])
    ]
    assert runs == snapshot


def test_repl(tmp_path, snapshot):
    world, session = restaurant(tmp_path)
    lines = ":help\n\ncreate a client named Ana Rojas, phone 9 5555 1234\n:trace\nwhat reservations does Ana have?\n1\n:state\n:lexicon Client\n:quit\nnever read\n"
    out = io.StringIO()
    code = repl(session, world.root.name, "all", stdin=io.StringIO(lines), stdout=out)
    assert Normalizer(tmp_path)({"exit": code, "stdout": out.getvalue()}) == snapshot


def test_serve_prints_its_worlds(tmp_path: Path, capsys, snapshot):
    with patch("pron.serve.Server", autospec=Server) as server_type:
        server_type.return_value.worlds.return_value = {"home": str(tmp_path)}
        run = invoke(
            ["serve", "--world", f"home={tmp_path}"], capsys, Normalizer(tmp_path)
        )
    assert run == snapshot
