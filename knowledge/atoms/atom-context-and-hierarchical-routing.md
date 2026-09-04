---
id: atom-context-and-hierarchical-routing
title: Context and Hierarchical Routing
five_wh_one_plus: what
tags:
- domain:knowledge_representation
- domain:graph_architecture
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Context and Hierarchical Routing

## Answer

A Context is a higher-order routing node (not a WiGame) that routes queries through sub-contexts to WiGame leaves. It can point to other Contexts or to WiGames, making the hierarchy recursive. RoutingProjection matrices implement the concrete projections between WiGame spaces. ContextRoute defines directed routing edges with relation_ids.
