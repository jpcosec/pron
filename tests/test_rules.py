"""The two rules of the repo, as tests so they cannot be skipped: files have a size, and
the engine knows no name of any world.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from check_file_length import LIMIT, source_files, too_long  # noqa: E402


def test_no_source_file_is_longer_than_the_limit():
    offenders = [f"{p}: {n}" for p in source_files([]) if (n := too_long(p))]
    assert not offenders, "too long:\n" + "\n".join(offenders)


def test_the_limit_is_actually_a_limit():
    assert LIMIT > 0
    assert any(p.name == "goals.py" for p in source_files([]))


def test_the_engine_mentions_no_name_of_the_world():
    """src/plnr is the layer under every world: Table, status, assigned_to and the rest are
    the world's words, and a word of a world in the engine is the hardcoding this package
    exists to avoid."""
    world_words = {
        "Table",
        "Reservation",
        "Client",
        "State",
        "Guard",
        "status",
        "assigned_to",
        "booked_by",
        "transitions_to",
        "party_size",
        "capacity",
        "terrace",
        "free",
        "fits",
        "book",
    }
    found: dict[str, list[str]] = {}
    for path in sorted((ROOT / "src" / "plnr").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        # only the code, not the prose that explains the language
        code = re.sub(r'"""[\s\S]*?"""', "", text)
        for word in world_words:
            if re.search(rf"\b{word}\b", code):
                found.setdefault(path.name, []).append(word)
    assert not found, f"the engine knows world words: {found}"
