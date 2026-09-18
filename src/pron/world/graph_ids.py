"""Node ids of sldb's edge index, as pron names them (spec 03, 10): re-exported from
`sldb.api`, whose id builders already coincide with these, plus the id parsing pron's own
navigation needs.
"""

from __future__ import annotations

from sldb.api import (
    doc_node_id,
    field_node_id,
    model_node_id,
    relation_type_node_id,
    tag_node_id,
)

doc_id = doc_node_id
model_id = model_node_id
relation_type_id = relation_type_node_id
field_id = field_node_id
tag_id = tag_node_id


def kind(node_id: str) -> str | None:
    """The `<kind>` of an `sldb://<kind>/...` id (document, model, semantic_tag, section, field, ...)."""
    if node_id.startswith("sldb://"):
        rest = node_id[len("sldb://") :]
        return rest.split("/", 1)[0] if "/" in rest else None
    return None


def bare(node_id: str) -> str:
    """The id without its `sldb://<kind>/` prefix; an id without one passes through."""
    if node_id.startswith("sldb://"):
        rest = node_id[len("sldb://") :]
        return rest.split("/", 1)[1] if "/" in rest else rest
    return node_id
