---
id: atom-knar-runtime-intercambiable
title: Cambiar el runtime debe conservar la definición semántica del agente
five_wh_one_plus: why
tags:
- system:knar
- topic:runtime
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 8, 20. Declaración del spec; no
  prueba de implementación.
---

# Cambiar el runtime debe conservar la definición semántica del agente

## Answer

La separación mediante adapters permite sustituir DeepSeek Harness por Claude, un LLM local o un runtime determinista sin cambiar el modelo semántico del agente. La identidad y el contrato se conservan aunque cambie su mecanismo de materialización.
