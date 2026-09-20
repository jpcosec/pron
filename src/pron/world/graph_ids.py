"""Node ids of sldb's edge index, as pron names them (spec 03, 10): re-exported from
`sldb.api`, whose id builders and `kind`/`bare` parsers already coincide with these.
"""

from __future__ import annotations

from sldb.api import (
    bare,
    doc_node_id,
    field_node_id,
    kind,
    model_node_id,
    relation_type_node_id,
    tag_node_id,
)

doc_id = doc_node_id
model_id = model_node_id
relation_type_id = relation_type_node_id
field_id = field_node_id
tag_id = tag_node_id
