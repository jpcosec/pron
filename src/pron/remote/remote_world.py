"""The World of a running server, read over the socket (spec 11 §8, 12 §5, §7)."""

from __future__ import annotations

from pron.remote.remote import _Remote


class RemoteWorld(_Remote):
    """`model_names()`, `family_of(name=...)`, `relation_types()`, `projection(name=...)`, `hash_mundo()`, `model_hashes()`, `graph_is_fresh()`."""

    op = "world"
