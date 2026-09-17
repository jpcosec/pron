---
id: surface-pron-session
system: pron
surface: session
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/session.py
---

# session

## Purpose

A session: one world, one projection, one speaker, and the turn loop (spec 06, 07, 11).

## How It Works

turn(sentence): read hash_mundo → interpret → resolve → verify → decide → execute →
refresh if written → write the MoveDoc → answer. Everything the turn did is in the
trace; every trace line is a real call.

The session owns what outlives a turn — the world, the projection and what `_load` builds
from it, the dialogue, the ledger, the last hash_mundo it saw. Each phase of a turn is one
class in `pron.sexpr` that works over the session: a `Move` brackets the turn, an
`Evaluator` compiles, plans (`Planner`), pre-validates (`Prevalidator`) and executes
(`Executor`) the forms, and the dialogue side replies to pending questions (`Replier`) or
corrects the last missing turn (`Corrector`). The underscore methods below are the seams
those phases meet at, and the ones the surface's renderer asks.

## Commands

Session
