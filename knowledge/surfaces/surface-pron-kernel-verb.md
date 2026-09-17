---
id: surface-pron-kernel-verb
system: pron
surface: kernel.verb
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/kernel/verb.py
---

# kernel.verb

## Purpose

What a plain action verb is (spec 11 §7): one object that knows its own dry-run
simulation, real execution, and undo. Before this, each verb's behavior was reimplemented
independently in `Kernel.dry_run`, `Kernel.undo`, `Session._dry_parts` and
`Session._action`; a Verb is the one place a verb's semantics live, so a new or changed
verb touches one class instead of four call sites. `create` and `assert` stay outside this
protocol: their shapes (no export_id yet; a RelationDoc write) don't fit the same
signature, and `Kernel.undo` already inverts them together.

## How It Works

What a plain action verb is (spec 11 §7): one object that knows its own dry-run
simulation, real execution, and undo. Before this, each verb's behavior was reimplemented
independently in `Kernel.dry_run`, `Kernel.undo`, `Session._dry_parts` and
`Session._action`; a Verb is the one place a verb's semantics live, so a new or changed
verb touches one class instead of four call sites. `create` and `assert` stay outside this
protocol: their shapes (no export_id yet; a RelationDoc write) don't fit the same
signature, and `Kernel.undo` already inverts them together.

## Commands

Verb
