"""pron command line. Every command is a thin door to a library function, one module per
command under pron.cli.commands; the docs of each command are generated from these
handlers' docstrings (spec 08 step 9).
"""

from __future__ import annotations

import sys

import click

from pron.cli.commands import check, docs, init, lexicon, mcp, refresh, repl, say, serve
from pron.cli.commands import eval as evaluate

cli = click.Group(
    "pron",
    help="pron: a SHRDLU over an sldb world.",
    context_settings={"help_option_names": ["-h", "--help"]},
)
for module in (init, refresh, lexicon, say, evaluate, repl, serve, mcp, check, docs):
    cli.add_command(module.command)


def main(argv: list[str] | None = None) -> int:
    """Run one command and return its exit code; a usage error exits with 2, as a parser's does."""
    args = sys.argv[1:] if argv is None else list(argv)
    try:
        with cli.make_context("pron", args) as ctx:
            return cli.invoke(ctx)
    except click.exceptions.Exit as done:  # --help
        return done.exit_code
    except click.ClickException as error:
        error.show()
        raise SystemExit(error.exit_code) from None
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
