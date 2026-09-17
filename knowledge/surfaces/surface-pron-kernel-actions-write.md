---
id: surface-pron-kernel-actions-write
system: pron
surface: kernel.actions.write
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/kernel/actions/write.py
---

# kernel.actions.write

## Purpose

One write of a move (spec 11 §7): the verb, the address it touched, the field, the value
before and after, whether it was actually done, and whatever extra the verb recorded for the
undo. `record()` is what the MoveDoc keeps.

## How It Works

One write of a move (spec 11 §7): the verb, the address it touched, the field, the value
before and after, whether it was actually done, and whatever extra the verb recorded for the
undo. `record()` is what the MoveDoc keeps.

## Commands

Write
restore_field
