"""The constructions by the name patterns.yaml gives them (spec 06, 11 §1): the interpreter
tries them in that file's order, and a name without a class here is skipped.
"""

from __future__ import annotations

from pron.surface.constructions.action_alias_construction import ActionAliasConstruction
from pron.surface.constructions.assert_relation_construction import (
    AssertRelationConstruction,
)
from pron.surface.constructions.change_to_construction import ChangeToConstruction
from pron.surface.constructions.compose_construction import ComposeConstruction
from pron.surface.constructions.construction import Construction
from pron.surface.constructions.create_construction import CreateConstruction
from pron.surface.constructions.forget_construction import ForgetConstruction
from pron.surface.constructions.list_op_construction import ListOpConstruction
from pron.surface.constructions.lone_verb_construction import LoneVerbConstruction
from pron.surface.constructions.nominal_construction import NominalConstruction
from pron.surface.constructions.read_relation_construction import (
    ReadRelationConstruction,
)
from pron.surface.constructions.set_field_construction import SetFieldConstruction
from pron.surface.constructions.why_construction import WhyConstruction

CONSTRUCTIONS: dict[str, Construction] = {
    c.name: c
    for c in (
        LoneVerbConstruction("undo"),
        LoneVerbConstruction("refresh"),
        WhyConstruction(),
        ComposeConstruction(),
        ActionAliasConstruction(),
        CreateConstruction(),
        ChangeToConstruction(),
        SetFieldConstruction(),
        ListOpConstruction(),
        ForgetConstruction(),
        AssertRelationConstruction(),
        ReadRelationConstruction(),
        NominalConstruction(),
    )
}
