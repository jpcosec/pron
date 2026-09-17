---
id: surface-pron-kernel-actions-verb_registry
system: pron
surface: kernel.actions.verb_registry
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/kernel/actions/verb_registry.py
---

# kernel.actions.verb_registry

## Purpose

The five plain action verbs by name (spec 11 §7). `create` and `assert` stay outside this
registry: their shapes (no export_id yet; a RelationDoc write) don't fit the same signature,
and `Kernel.undo` already inverts them together.

## How It Works

The five plain action verbs by name (spec 11 §7). `create` and `assert` stay outside this
registry: their shapes (no export_id yet; a RelationDoc write) don't fit the same signature,
and `Kernel.undo` already inverts them together.

## Commands

(none)
