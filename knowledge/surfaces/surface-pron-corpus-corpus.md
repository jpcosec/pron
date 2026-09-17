---
id: surface-pron-corpus-corpus
system: pron
surface: corpus.corpus
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/corpus/corpus.py
---

# corpus.corpus

## Purpose

The indexed corpus of a world (spec 12 §5b): which documents a consumer can retrieve
by similarity, kept fresh against the store.

## How It Works

A runtime that retrieves documents by meaning needs the same six things every time: pick
the documents, get the text that represents each one, know the content hash so a reindex
embeds only what changed, persist the vectors outside git, rank a query, and audit that
the index matches the store. All of that is general and lives here. What is not general
is which models enter and what text represents a document: that is the consumer's policy,
declared once as an `IndexProjection` and passed in.

Identity is always the export id (`Model:doc`, `store:Model:doc`), never the bare name:
two stores of a federated world may hold the same document name.

## Commands

Corpus
