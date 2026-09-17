---
id: surface-pron-world-matching-matcher
system: pron
surface: world.matching.matcher
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/world/matching/matcher.py
---

# world.matching.matcher

## Purpose

Ranking candidates for a query (spec 11 §2): with an Embedder when the application gave
one, difflib otherwise. `cosine` is the similarity over two vectors. Neither ever executes
anything: they only rank neighbors to offer.

## How It Works

Ranking candidates for a query (spec 11 §2): with an Embedder when the application gave
one, difflib otherwise. `cosine` is the similarity over two vectors. Neither ever executes
anything: they only rank neighbors to offer.

## Commands

cosine
Matcher
