"""Malformed composition declarations fail before calling write mechanisms."""

from unittest.mock import Mock

import pytest

from pron.kernel.word import Word
from pron.session import Session
from pron.world.store_error import StoreError
from pron.kernel.part import Part


@pytest.mark.parametrize("phase", ["validate", "execute"])
@pytest.mark.parametrize("operation", ["assert", "change"])
def test_created_reference_requires_a_preceding_create(phase, operation):
    step = {
        "do": operation,
        "source": "$created",
        "target": "$created",
        "relation": "belongs_to",
        "field": "status",
        "value": "confirmed",
    }
    part = Part(
        "compose",
        verb=Word(
            "broken", "alias", "compose", "test", "test", payload={"steps": [step]}
        ),
    )
    session = Mock(spec=Session)
    session.write_store = None
    session.kernel = Mock()
    session.verbs = Mock()
    plan = {"steps": [{}]}

    with pytest.raises(StoreError, match=r"references \$created before create"):
        if phase == "validate":
            Session._dry_parts(session, [part], [plan], {})
        else:
            Session._compose(session, part, plan, [], {"writes": []})

    assert session.kernel.mock_calls == []
    assert session.verbs.mock_calls == []
