---
id: cmd-pron-serve
system: pron
command_path: serve
synopsis: Keep a world open and answer sentences over a Unix socket (spec 11 §8).
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:cli_command
provenance: src/pron/cli/main.py:_cmd_serve
---

# serve

## Synopsis

Keep a world open and answer sentences over a Unix socket (spec 11 §8).

## Purpose

Keep a world open and answer sentences over a Unix socket (spec 11 §8).

## How It Works

Imports, caches and sessions are paid once; `say`, `repl` and kinesis use the socket
at <world>/.pron/serve.sock while it listens. Runs in the foreground until --stop is
sent from another shell or the process is interrupted.

## Arguments

--world | optional | World root (contains .sldb)
--pythonpath | optional | Project path where the world's models import from
--socket | optional | Socket path (default <world>/.pron/serve.sock)
--stop | optional | Stop the server listening at the socket

## Usage

pron serve --world . [--pythonpath .] [--socket PATH]
  pron serve --world . --stop
