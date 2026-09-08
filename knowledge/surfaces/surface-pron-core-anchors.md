---
id: surface-pron-core-anchors
system: pron
surface: pron.core.anchors
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/core/anchors.py
---

# pron.core.anchors

## Purpose

Anchor registry: symbol -> {kind, ref, motive} from tracked AnchorDocs

## How It Works

atom-the-anchor-table-is-declared-as-sldb-documents-not-code: Anchors live as tracked SLDB documents (AnchorDoc), not as code, so each app declares its own grammar by registering anchors. knowledge adapts to each use case without code changes, the grammar is queryable and versioned with provenance, and the app becomes self-aware of its own command language: --help and the living grammar derive from the same documents.

atom-unanchored-symbols-fail-with-an-explicit-semantic-error: A symbol without an anchor must not be guessed, fuzzy-matched into an operation, or silently ignored. The evaluator fails with an explicit semantic error stating that the symbol has no known motive. Growing the grammar means declaring a new anchor document, never patching the parser.

## Commands

Anchor: symbol: str; kind: str; ref: str; motive: str
AnchorRegistry
AnchorRegistry.lookup(self, symbol: str) -> Anchor | SemanticError | The anchor for a symbol, or an explicit semantic error.
AnchorRegistry.all(self) -> list[Anchor] | The living grammar, for `knowledge anchors` and derived help.
AnchorRegistry.by_kind(self, kind: str) -> list[Anchor] | Anchors of one kind (used by the desugarer to classify tokens).
