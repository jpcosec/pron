"""What the lexicon holds that is written in code (spec 05): pron's function words, the
models that are pron's and sldb's own relation bookkeeping, and how a word writes what it
names as a form (spec 13).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from pron.kernel.sexp.read_write import Sym, write

FUNCTION_WORDS = yaml.safe_load(
    (Path(__file__).parent.parent.parent / "surface" / "function_words.yaml").read_text(
        encoding="utf-8"
    )
)
INTERNAL_MODELS = {"RelationTypeDoc", "RelationDoc", "ProjectionDoc", "AnchorDoc"}
# never a source of values to offer or promote: pron's and sldb's own relation bookkeeping,
# and the ledger, whose values are this very conversation's past sentences
UNSUGGESTED_MODELS = INTERNAL_MODELS | {"MoveDoc"}


def word_ref(head: str, *names: str) -> str:
    """`(head name …)`: what a model, field, relation or action word names, as a form."""
    return write([Sym(head), *[Sym(n) for n in names]])
