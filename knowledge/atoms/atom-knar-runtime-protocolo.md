---
id: atom-knar-runtime-protocolo
title: El protocolo Runtime cubre preparación, invocación, observación y cancelación
five_wh_one_plus: how
tags:
- system:knar
- topic:runtime_contract
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 8. Declaración del spec; no prueba
  de implementación.
---

# El protocolo Runtime cubre preparación, invocación, observación y cancelación

## Answer

La interfaz mínima declara prepare(runtime, node, context), invoke(runtime, request), observe(runtime, execution) y cancel(runtime, execution). Estas operaciones separan la preparación de una petición del seguimiento y control de su ejecución.
