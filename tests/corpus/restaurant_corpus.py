"""A corpus over the restaurant world, read as its documents' own fields."""

from __future__ import annotations

from pron.corpus import Corpus, IndexProjection
from pron.world.world import World


def fields_of(payload: dict) -> str:
    """The restaurant has no summaries: a document reads as its own fields."""
    return " ".join(f"{k} {v}" for k, v in payload.items() if isinstance(v, (str, int)))


def corpus_of(world: World, **kw) -> Corpus:
    kw.setdefault("text", fields_of)
    kw.setdefault("text_id", "fields")
    return Corpus(world, IndexProjection.of(**kw))
