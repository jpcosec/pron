---
id: atom-knar-proposal-configured-node
title: Un ConfiguredNode genérico es una implementación propuesta
five_wh_one_plus: how
tags:
- system:knar
- topic:node_spec
- domain:system_architecture
- kind:software
- impl:pending
provenance: Derivado de docs/knowledge-native-runtime/technical/README.md y del modelo
  técnico asociado. Propuesta del asistente; no decisión aprobada del spec.
---

# Un ConfiguredNode genérico es una implementación propuesta

## Answer

Los diagramas técnicos proponen que ConfiguredNode implemente ExecutableNode usando NodeSpec como datos. Los accessors se derivan del spec y execute delega a NodeExecutor; esta clase concreta es una propuesta de implementación, no una exigencia del spec.
