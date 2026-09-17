---
id: surface-pron-sexpr-dialogue-replier
system: pron
surface: sexpr.dialogue.replier
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/dialogue/replier.py
---

# sexpr.dialogue.replier

## Purpose

A sentence said while a question is pending (spec 06): an answer, or not.

## How It Works

It may be a new order, and then the question is dropped and the order runs; it may call the
whole thing off; or it answers — the value of the field a create was missing, or which of
the candidates was meant. An answer fills the hole in the part that asked, and that part is
said again as forms and evaluated like any other move. An answer that picks none, or more
than one, leaves the question pending and asks it again.

## Commands

Replier
