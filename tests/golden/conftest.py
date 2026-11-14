"""The golden masters compare documents sldb writes, so they need sldb's wall clock held still.

sldb stamps every write with the time and that stamp is part of the document's source_hash:
the same undo can land on the previous hash_mundo or a new one depending on whether its writes
crossed a second. Freezing the stamp keeps the snapshots pinning hash equality (an undo
restores the hash it left), which is pron behavior, instead of the clock.
"""

from __future__ import annotations

import pytest
from sldb.api.documents import provenance_stamp

PROVENANCE_AT = "2026-09-09T00:00:00Z"


@pytest.fixture(autouse=True)
def frozen_provenance(monkeypatch):
    monkeypatch.setattr(provenance_stamp, "now", lambda: PROVENANCE_AT)
