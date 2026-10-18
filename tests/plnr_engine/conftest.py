from __future__ import annotations

import sys
from pathlib import Path

import pytest

# The engine's own test world lives next to its tests, under a name that cannot be taken for
# pron's tests/worlds (also on sys.path, with its own restaurant).
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from engine_worlds import restaurant  # noqa: E402


@pytest.fixture
def world():
    return restaurant.world()


@pytest.fixture
def theorems():
    return restaurant.theorems()
