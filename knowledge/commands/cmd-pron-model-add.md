---
id: cmd-pron-model-add
system: pron
command_path: pron model add
synopsis: Register a StructuredNLDoc model contract in the local store.
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/cli/main.py:_cmd_model_add
---

# pron model add

## Synopsis

Register a StructuredNLDoc model contract in the local store.

## Purpose

Register a StructuredNLDoc model contract in the local store.

## How It Works

Delegates to `sldb models add` against the local .sldb store, given a
module:Class reference, so the evaluator and write ops can resolve and
validate documents of that model.

## Arguments

<module:Class> | required | The model reference to register, e.g. pron.bridges.write_models:FactDoc.
--kb <root> | optional | KB root; defaults to the current working directory.

## Usage

pron model add pron.bridges.write_models:FactDoc
