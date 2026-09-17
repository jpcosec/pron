---
id: surface-pron-world-matching-document_index
system: pron
surface: world.matching.document_index
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/world/matching/document_index.py
---

# world.matching.document_index

## Purpose

Documents of a world ranked by similarity to a query (spec 05 §Calce aproximado, 11 §2).
The vectors live in one derived file outside git, keyed by the document's content hash, so a
re-index embeds only what changed. pron never decides what to do with a rank; it offers it.

## How It Works

Documents of a world ranked by similarity to a query (spec 05 §Calce aproximado, 11 §2).
The vectors live in one derived file outside git, keyed by the document's content hash, so a
re-index embeds only what changed. pron never decides what to do with a rank; it offers it.

## Commands

DocumentIndex
