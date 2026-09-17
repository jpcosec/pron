---
id: surface-pron-sexpr-dialogue-corrector
system: pron
surface: sexpr.dialogue.corrector
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/dialogue/corrector.py
---

# sexpr.dialogue.corrector

## Purpose

Spec 06 §Corrección: a fragment that fills the hole the last missing turn left.

## How It Works

"book a table on the patio" → there is no patio; "on the terrace" → that is a verbless
fragment, and it fits the hole of the last turn (a value of `zone`), so the previous
sentence is said again whole, with the hole filled. It is not a pending question: that turn
ended and was recorded; this is a new move that says which one it corrects.

## Commands

Corrector
