"""How an answer names what it found, and how a question numbers what it offers (spec 06).

A nominal answer ("the tables") and a relation read ("what Ana booked") say the same thing
the same way: nothing, one name, or how many and then all of them. A pending question and
the reminder that it is still pending number their candidates the same way too.
"""

from __future__ import annotations


def listing(display, addresses: list[str]) -> str:
    """Nothing, the one name, or how many there are and then all of them."""
    if not addresses:
        return "None."
    names = display.names(addresses)
    if len(names) == 1:
        return names[0] + "."
    return f"{len(names)}: " + "; ".join(names) + "."


def numbered(labels: list[str]) -> str:
    """The candidates of a pending question, numbered the way the answer may name them."""
    return " · ".join(f"({i + 1}) {label}" for i, label in enumerate(labels))
