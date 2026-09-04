---
id: atom-logicalsystem-as-aggregate-root
title: LogicalSystem as Aggregate Root
five_wh_one_plus: what
tags:
- domain:knowledge_representation
- domain:graph_architecture
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# LogicalSystem as Aggregate Root

## Answer

Top-level coordinator that registers and links all entities: names, symbols, things, relations, LiSpaces, WiGames, Contexts, RoutingProjections. When a fact is added through the system, symbol support is updated automatically. Exposes local search, cross-search (via projections), and route-search (multi-hop across projection paths). The single entry point for the operational model.
