---
id: cmd-pron-project
system: pron
command_path: pron project
synopsis: Refresh SLDB indexes and rebuild the KGDB graph.
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/cli/main.py:_cmd_project
---

# pron project

## Synopsis

Refresh SLDB indexes and rebuild the KGDB graph.

## Purpose

Refresh SLDB indexes and rebuild the KGDB graph.

## How It Works

Runs `sldb stores update` to reindex every tracked document (semantic
index, sections), then semantic-exports the store and ingests it into
the KGDB snapshot at .sldb/runtime/knowledge.nx.json.

## Arguments

--kb <root> | optional | KB root; defaults to the current working directory.

## Usage

pron project
