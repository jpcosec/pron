---
id: atom-knar-proposal-execution-record
title: ExecutionRecord separa estado de invocación y definición del nodo
five_wh_one_plus: how
tags:
- system:knar
- topic:state_machine
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de docs/knowledge-native-runtime/technical/README.md y del modelo
  técnico asociado. Propuesta del asistente; no decisión aprobada del spec.
---

# ExecutionRecord separa estado de invocación y definición del nodo

## Answer

El diseño técnico propone guardar el estado mutable en un ExecutionRecord por invocación y conservar StateMachineSpec como definición. Así varias ejecuciones pueden usar el mismo nodo sin compartir su estado temporal; el spec no exige el nombre de este record.
