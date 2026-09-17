"""A graph refresh deferred until after the response (spec 11 §8): the session answered
first, and the graph catches up when the server settles or the next graph read arrives.
"""

from __future__ import annotations

from typing import Any, Callable


class PendingRefresh:
    """The accumulated deferral: the union of the stores, light only if every one was."""

    def __init__(self) -> None:
        self._pending: tuple[set[str] | None, bool] | None = None  # (stores, light)

    def defer(self, stores: list[str] | None, light: bool) -> None:
        wanted = None if stores is None else set(stores)  # None: every store, as in refresh
        if self._pending is None:
            self._pending = (wanted, light)
        else:
            pending_stores, pending_light = self._pending
            union = None if pending_stores is None or wanted is None else pending_stores | wanted
            self._pending = (union, pending_light and light)

    @property
    def is_pending(self) -> bool:
        return self._pending is not None

    def clear(self) -> None:
        self._pending = None

    def settle(self, refresh: Callable[..., Any]) -> bool:
        """Run `refresh(stores=..., light=...)` for the pending deferral, if there is one, and
        say whether it ran. It stops being pending while it runs (refresh reads the graph
        itself); a refresh that raises leaves it pending again, so it is retried."""
        if self._pending is None:
            return False
        stores, light = self._pending
        self._pending = None
        try:
            refresh(stores=None if stores is None else sorted(stores), light=light)
            return True
        except Exception:
            self._pending = (stores, light)
            raise
