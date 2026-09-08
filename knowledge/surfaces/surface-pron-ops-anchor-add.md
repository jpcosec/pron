---
id: surface-pron-ops-anchor-add
system: pron
surface: pron.ops.anchor_add
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/ops/anchor_add.py
---

# pron.ops.anchor_add

## Purpose

anchor add: declare a new grammar symbol as a tracked AnchorDoc

## How It Works

atom-the-anchor-table-is-declared-as-sldb-documents-not-code: Anchors live as tracked SLDB documents (AnchorDoc), not as code, so each app declares its own grammar by registering anchors. knowledge adapts to each use case without code changes, the grammar is queryable and versioned with provenance, and the app becomes self-aware of its own command language: --help and the living grammar derive from the same documents.

atom-anchor-ref-is-a-typed-string-with-a-scheme-per-kind: AnchorDoc.ref is a single string with a kind-specific scheme validated by regex: model:<Name>, doc:<name>, edge:<relation_type>[:direction], op:<function>, and fields:<f1,f2> or view:<name> for projections. A typed string instead of a dict keeps frontmatter legible and validation simple; complex resolution lives in the evaluator, not in the anchor.

## Commands

AnchorAddError
validate_ref(kind: str, ref: str) -> None | The ref must match the scheme declared for its kind.
anchor_add(root: Path, symbol: str, kind: str, ref: str, motive: str) -> tuple[bool, str] | Write the AnchorDoc, track it in sldb, and rebuild the graph.
