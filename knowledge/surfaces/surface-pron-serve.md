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

Serve a world: one process keeps the world, its caches and its sessions open behind a
Unix socket, and every local caller (the CLI, the REPL, kinesis) says its sentences
through it instead of opening the world again (spec 11 §8).

## How It Works

One request per connection, one JSON object per line. Requests are handled one at a
time: a world has one writer, and a turn is short. The server speaks as whoever the
client says it is; identity is the application's (spec 11 §6). The socket lives at
<world>/.pron/serve.sock; a client that finds no listener there opens the world itself.
The client side is pron.client, stdlib only.

## Commands

Server
