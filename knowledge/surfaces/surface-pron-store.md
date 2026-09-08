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
store's hash chain, so reading them here costs nothing and is never stale.

## Commands

StoreError
Store
