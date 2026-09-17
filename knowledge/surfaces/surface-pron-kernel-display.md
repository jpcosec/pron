---
id: surface-pron-kernel-display
system: pron
surface: kernel.display
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/kernel/display.py
---

# kernel.display

## Purpose

How objects are shown (spec 10): the projection's display templates, `{rel.field}` following an edge.

## How It Works

`render_name` is the same substitution used the other way round: a projection's naming rule
turned into the document name a `create` writes.

## Commands

Display
split_address
slugify
render_name
