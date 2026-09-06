---
id: atom-knar-proposal-composite-runtime
title: CompositeRuntime es una forma propuesta de ejecutar composiciones
five_wh_one_plus: how
tags:
- system:knar
- topic:composite_node
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de docs/knowledge-native-runtime/technical/README.md y del modelo
  técnico asociado. Propuesta del asistente; no decisión aprobada del spec.
---

# CompositeRuntime es una forma propuesta de ejecutar composiciones

## Answer

Los diagramas técnicos proponen representar un compuesto mediante ConfiguredNode y CompositeRuntime, que ejecuta un ExecutionPlan con un orquestador. Esta solución preserva el contrato externo, pero el spec permite otras implementaciones de CompositeNode.
