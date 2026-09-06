---
id: atom-knar-proposal-executor
title: NodeExecutor concentra la ejecución individual en el diseño propuesto
five_wh_one_plus: how
tags:
- system:knar
- topic:execution
- domain:system_architecture
- kind:software
- impl:pending
provenance: Derivado de docs/knowledge-native-runtime/technical/README.md y del modelo
  técnico asociado. Propuesta del asistente; no decisión aprobada del spec.
---

# NodeExecutor concentra la ejecución individual en el diseño propuesto

## Answer

La propuesta técnica separa el orquestador de planes de un NodeExecutor encargado de ejecutar y verificar un nodo. El orquestador llama execute y el nodo delega a run, sin volver a invocar execute recursivamente sobre el mismo nodo.
