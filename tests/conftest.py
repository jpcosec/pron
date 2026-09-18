from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
for path in (ROOT / "src", ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from worlds import restaurant  # noqa: E402


@pytest.fixture
def world():
    return restaurant.world()


@pytest.fixture
def theorems():
    return restaurant.theorems()
