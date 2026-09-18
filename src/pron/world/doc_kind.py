"""What pron does with the documents of a model, declared once per model (spec 05, 07, 10,
12 §5b): whether they are nodes of the graph, words of the lexicon, a source of values to
suggest, entries of the corpus, and whether the model is the ledger.

pron has no code per model of a world: a world's models all get the default kind, and the
only kinds declared here are pron's and sldb's own relation bookkeeping. The registry
answers by model NAME and imports no model class, so asking it costs nothing (`import pron`
stays free of pydantic).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocKind:
    """The policy of one model. The default — every flag but `is_ledger` on — is a model of
    the world; `type_tag` is the semantic tag sldb's edge index is told to leave out when
    the model stays out of the graph."""

    model: str
    in_graph: bool = True
    in_lexicon: bool = True
    suggests_values: bool = True
    in_corpus: bool = True
    is_ledger: bool = False
    type_tag: str | None = None


# sldb's relation bookkeeping (RelationTypeDoc, RelationDoc — spec 03) and pron's projections
# and anchors are never words of the lexicon nor a source of values; the ledger is a word
# (one asks about moves), but its values are this very conversation's past sentences, and it
# stays out of the graph.
_DECLARED: dict[str, DocKind] = {
    k.model: k
    for k in (
        DocKind("RelationTypeDoc", in_lexicon=False, suggests_values=False),
        DocKind("RelationDoc", in_lexicon=False, suggests_values=False),
        DocKind("ProjectionDoc", in_lexicon=False, suggests_values=False),
        DocKind("AnchorDoc", in_lexicon=False, suggests_values=False),
        DocKind(
            "MoveDoc",
            in_graph=False,
            suggests_values=False,
            is_ledger=True,
            type_tag="type.pron.move",
        ),
    )
}


def kind_of(model: str) -> DocKind:
    """The declared kind of a bookkeeping model; the default kind for a model of the world."""
    return _DECLARED.get(model) or DocKind(model)


def declared() -> tuple[DocKind, ...]:
    """The kinds pron declares: its own bookkeeping models and sldb's relation ones."""
    return tuple(_DECLARED.values())


def models_without(policy: str) -> frozenset[str]:
    """The declared models whose `policy` flag is off, e.g. `models_without("in_lexicon")`."""
    return frozenset(k.model for k in declared() if not getattr(k, policy))


def ledger_model() -> str:
    """The one model that is the ledger."""
    (ledger,) = (k.model for k in declared() if k.is_ledger)
    return ledger


def tags_outside_graph() -> tuple[str, ...]:
    """The semantic tags sldb's edge index leaves out: those of the models not in the graph."""
    return tuple(k.type_tag for k in declared() if not k.in_graph and k.type_tag)
