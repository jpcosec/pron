---
id: surface-pron-serve
system: pron
surface: serve
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/serve.py
---

# serve

## Purpose

Serve worlds: one process keeps one or more worlds, their caches and their sessions open
behind a Unix socket, and every local caller (the CLI, the REPL, an agent runtime) says its
sentences through it instead of opening a world again (spec 11 §8, 12 §7).

## How It Works

One request per connection, one JSON object per line. Requests are handled one at a
time: a world has one writer, and a turn is short. Each request names the world it
speaks to and the caller's own world, `home`; a caller whose home is another world may
open only the projections that world exposes, its interface lexicon, and nothing else
(spec 12 §6): talking to another world is semantic, never access to its store. The
server speaks as whoever the client says it is; identity is the application's (11 §6).
Every mounted world gets `<world>/.pron/serve.sock` pointing at the daemon's socket, so a
client that only knows the world finds the daemon. The client side is pron.client.

## Commands

Server
