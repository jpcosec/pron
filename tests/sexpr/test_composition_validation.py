"""Malformed composition declarations fail before calling write mechanisms."""

from unittest.mock import Mock

import pytest

from pron.kernel.parts.word import Word
from pron.sexpr.execution.compose_executor import ComposeExecutor
from pron.sexpr.execution.relation_write import EdgeWriter
from pron.sexpr.prevalidation.dry_runner import DryRunner
from pron.sexpr.turn.move_context import MoveContext
from pron.world.store_error import StoreError
from pron.kernel.parts.part import Part


def _untouchable() -> Mock:
    """Anything besides the kernel and the verbs: reading it at all is an error."""
    return Mock(spec=[])


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
    kernel = Mock()
    verbs = Mock()
    plan = {"steps": [{}]}

    with pytest.raises(StoreError, match=r"references \$created before create"):
        if phase == "validate":
            DryRunner(kernel, verbs, _untouchable(), None)([part], [plan], {})
        else:
            edges = EdgeWriter(_untouchable(), verbs, None)
            ComposeExecutor(
                kernel, _untouchable(), _untouchable(), _untouchable(), edges
            )(part, plan, MoveContext(record={"writes": []}))

    assert kernel.mock_calls == []
    assert verbs.mock_calls == []
