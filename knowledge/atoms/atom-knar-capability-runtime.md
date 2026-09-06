---
id: atom-knar-capability-runtime
title: La capacidad y el runtime son dimensiones distintas
five_wh_one_plus: why
tags:
- system:knar
- topic:runtime
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 7, 8. Declaración del spec; no prueba
  de implementación.
---

# La capacidad y el runtime son dimensiones distintas

## Answer

La capacidad identifica la transformación prometida y el runtime identifica el mecanismo que la ejecuta. Separarlas permite describir resumir_documento independientemente del proveedor LLM, o execute_query independientemente de la definición semántica del nodo.
