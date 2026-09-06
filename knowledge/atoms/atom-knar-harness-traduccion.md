---
id: atom-knar-harness-traduccion
title: El adapter traduce las partes del contrato al harness
five_wh_one_plus: how
tags:
- system:knar
- topic:adapter
- domain:system_architecture
- kind:software
- impl:pending
provenance: Derivado de source/spec.md, secciones 20. Declaración del spec; no prueba
  de implementación.
---

# El adapter traduce las partes del contrato al harness

## Answer

DeepSeekHarnessAdapter traduce SelfDoc y KnowledgeProjection a system/context, Capabilities a tools, StateMachine a reglas de ejecución y CompletionTests a verificación. La traducción hace operable el contrato semántico en el backend externo.
