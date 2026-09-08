---
id: surface-pron-core-resolution
system: pron
surface: pron.core.resolution
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/core/resolution.py
---

# pron.core.resolution

## Purpose

Noun resolver: (model, selector) -> Resolved | Ambiguous | Missing

## How It Works

atom-symbol-resolution-is-stateful-and-treats-ambiguity-as-dialogue: Noun resolution against the store has three outcomes, SHRDLU-style: a unique referent proceeds; an ambiguous one returns a question plus candidates and leaves the evaluator awaiting clarification, so the next input resolves the pending expression; a missing one fails with the symbol's motive so the error explains what was being looked for. The resolution cascade reuses sldb's own search layers: exact name, exact title, name prefix, semantic tag (namespaced selectors match tagged docs), then substring over name and title; fuzzy matching only populates nearest suggestions. Ambiguity produces dialogue, never a silent failure or a bare exception.

## Commands

resolve_noun(bridge: SldbBridge, model_name: str, selector: str, motive: str) -> Resolved | Ambiguous | Missing | Resolve a selector against the tracked documents of a model.
