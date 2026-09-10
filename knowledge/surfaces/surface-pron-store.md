---
id: surface-pron-store
system: pron
surface: store
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/store.py
---

# store

## Purpose

The only door to sldb: read by address (spec 02), write by address (spec 04), never open Markdown.

## How It Works

Every method is a call into sldb's library. sldb caches the runtime documents by the
store's hash chain, so reading them here costs nothing and is never stale. A world's store
may link other stores (spec 01 §Un mundo en varios stores); every method that names a
document takes the store it lives in, `None` or "local" for the local one, and the
`*_of(export_id)` forms take the id `store:Model:doc` that carries it.

Model editing (`model_catalog`, `model_detail`, `model_template_edit`, `model_fields_add`,
`model_fields_remove`, `model_validate_draft`, `model_promote`) is the same door for a
model's own contract instead of a document's payload (spec 12 §4, spec 10 §3): a draft
lives in the `.py.temp` sibling sldb keeps next to the compiled model module until
`model_promote` installs it, reindexes, and bumps the version.

## Commands

StoreError
Store
