"""The only door to sldb: read by address (spec 02), write by address (spec 04), never open Markdown.

Every method is a call into sldb's library. sldb caches the runtime documents by the
store's hash chain, so reading them here costs nothing and is never stale. A world's store
may link other stores (spec 01 §Un mundo en varios stores), so a document is named by a
`DocId` — store, model, name — and every operation on one document has one form that takes
it (`doc_at`, `payload_at`, `hash_at`, `path_at`, `create_at`, `track_at`, `untrack_at`,
`replace_at`, `update_field_at`, `remove_field_at`, `append_at`, `clean_at`, `matches_at`).
The older forms delegate to it: `(model, name, store)`, with `None` or "local" for the
local store, and `*_of(export_id)`, which take the id `store:Model:doc`.

Model editing (`model_catalog`, `model_detail`, `model_template_edit`, `model_fields_add`,
`model_fields_remove`, `model_validate_draft`, `model_promote`) is the same door for a
model's own contract instead of a document's payload (spec 12 §4, spec 10 §3): a draft
lives in the `.py.temp` sibling sldb keeps next to the compiled model module until
`model_promote` installs it, reindexes, and bumps the version.

`Store` is the one name callers hold; each responsibility behind it is its own layer in
pron.world.storage: the linked stores, the model registry, document reads, structural
queries, tracking, payload writes, and model editing.
"""

from __future__ import annotations

from pron.world.storage.document_tracker import DocumentTracker
from pron.world.storage.model_editor import ModelEditor
from pron.world.storage.payload_editor import PayloadEditor
from pron.world.storage.structural_query import StructuralQuery


class Store(StructuralQuery, DocumentTracker, PayloadEditor, ModelEditor):
    """Read/write access to one world's .sldb store, and the stores it links, through sldb's library."""
