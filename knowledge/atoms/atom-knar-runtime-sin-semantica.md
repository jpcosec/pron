---
id: atom-knar-runtime-sin-semantica
title: El runtime no define la semántica del agente
five_wh_one_plus: how_not
tags:
- system:knar
- topic:runtime_contract
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 2, 20, 23. Declaración del spec;
  no prueba de implementación.
---

# El runtime no define la semántica del agente

## Answer

El backend no debe convertirse en el lugar donde se define la responsabilidad o el significado del agente. Esas definiciones pertenecen al grafo y al spec del nodo; el runtime las materializa bajo el contrato recibido.
