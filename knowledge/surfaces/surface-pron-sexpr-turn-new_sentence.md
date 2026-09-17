---
id: surface-pron-sexpr-turn-new_sentence
system: pron
surface: sexpr.turn.new_sentence
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/turn/new_sentence.py
---

# sexpr.turn.new_sentence

## Purpose

A new sentence (spec 13, 05): the surface says it as forms and the forms are evaluated.

## How It Works

The surface only interprets. A sentence made only of words the projection does not have,
or of nouns among them, is answered with what the lexicon has near it; a sentence with any
part nobody could parse is answered with sentences this world does understand. Anything
else is said as forms, and the forms are what gets resolved and run — so a sentence and the
forms it says leave exactly the same move. If the world changes while the move is being
understood, the sentence itself is understood again, not the forms it said the first time.

## Commands

NewSentence
