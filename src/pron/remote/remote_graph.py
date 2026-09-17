"""The Graph of a running server, read over the socket (spec 11 §8, 12 §5)."""

from __future__ import annotations

from pron.remote.remote import _Remote


class RemoteGraph(_Remote):
    """The Graph methods of spec 12 §5 (`edges_from(node_id=...)`, `targets(node_id=..., relation=...)`, ...), keyword arguments only."""

    op = "graph"
