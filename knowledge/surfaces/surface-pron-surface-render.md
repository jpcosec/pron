---
id: surface-pron-surface-render
system: pron
surface: surface.render
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/surface/render.py
---

# surface.render

## Purpose

The other direction of the surface (spec 06, 13): a compiled Part written back as the
forms it says. `said` is what a sentence said, with every noun still a phrase; `resolved` is
what the move did, with every noun replaced by the addresses it resolved to — evaluating that
on the same world in the same state leaves the same writes, without the dialogue.

## How It Works

The other direction of the surface (spec 06, 13): a compiled Part written back as the
forms it says. `said` is what a sentence said, with every noun still a phrase; `resolved` is
what the move did, with every noun replaced by the addresses it resolved to — evaluating that
on the same world in the same state leaves the same writes, without the dialogue.

## Commands

said
said_part
noun_form
resolved
