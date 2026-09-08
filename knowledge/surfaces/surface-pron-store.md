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

Every method is a call into sldb's library. The address engine loads every document
of the store before selecting (an sldb cost, not pron's), so the runtime documents
are cached here and invalidated on every write.

## Commands

StoreError
Store
