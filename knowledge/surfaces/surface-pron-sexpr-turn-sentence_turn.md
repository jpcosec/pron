---
id: surface-pron-sexpr-turn-sentence_turn
system: pron
surface: sexpr.turn.sentence_turn
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/turn/sentence_turn.py
---

# sexpr.turn.sentence_turn

## Purpose

What `Session.turn` does inside its move (spec 06, 13).

## How It Works

A sentence is one of three things. If a question is pending, it is the reply to it. If the
last turn was missing a value and this sentence is a fragment that fits that hole, it is a
correction of that turn, and the corrected sentence runs instead, as a move that says which
one it corrects. Otherwise it is a new sentence. Either way, the hole of the last missing
turn is used up: a correction can only follow the turn it corrects.

## Commands

SentenceTurn
