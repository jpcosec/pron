"""The indexed corpus of a world (spec 12 §5b), now sldb's: pron only adapts its `World`
to the store-based corpus of sldb. What is not general — which models enter and what
text represents a document — is the consumer's policy, declared once as an
`IndexProjection`.
"""

from __future__ import annotations

from typing import Any

from sldb.api.corpus.corpus import Corpus as SldbCorpus

from pron.world.world import World


class Corpus(SldbCorpus):
    """The documents of a world that can be retrieved by similarity, and their index."""

    def __init__(
        self,
        world: World,
        projection: Any | None = None,
        embedder: Any | None = None,
        matcher: Any | None = None,
    ) -> None:
        super().__init__(
            world.store.sp,
            world.store.pythonpath,
            world.derived_dir,
            projection,
            embedder,
            matcher,
        )
