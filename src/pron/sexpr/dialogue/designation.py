"""A designation of one of a pending choice's candidates (spec 06): a number, an ordinal, or a
name matched against the candidates' labels."""

from __future__ import annotations

from pron.world.lexicon import FUNCTION_WORDS


def within(i: int, n: int) -> list[int]:
    return [i] if 0 <= i < n else []


def ordinal(t: str) -> int | None:
    """The index an ordinal says — "second", "the second", "the second one" — negative from
    the end; None when it is not one."""
    ordinals = FUNCTION_WORDS["designation"]["ordinal"]
    return next(
        (
            idx
            for word, idx in ordinals.items()
            if t in (word, f"the {word}", f"the {word} one")
        ),
        None,
    )


def by_label(t: str, labels: list[str], matcher) -> list[int]:
    """The candidates whose labels a name matches best, when it matches well enough."""
    if t.startswith("the ") and t.endswith(" one"):
        t = t[4:-4]
    ranked = matcher.rank(
        t,
        [(str(i), label) for i, label in enumerate(labels)],
        k=len(labels),
        threshold=0.0,
    )
    if not ranked:
        return []
    best = ranked[0][1]
    winners = [int(k) for k, s in ranked if s >= best - 1e-9]
    return winners if best >= 0.5 else []
