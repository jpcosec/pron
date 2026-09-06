---
id: atom-knar-estados-especializados
title: Un nodo puede especializar su máquina de estados
five_wh_one_plus: how
tags:
- system:knar
- topic:state_machine
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 9. Declaración del spec; no prueba
  de implementación.
---

# Un nodo puede especializar su máquina de estados

## Answer

La máquina de un nodo puede extender el ciclo general con etapas propias de su trabajo. El scraper ejemplifica RESOLVE_SOURCE → FETCH → PARSE → NORMALIZE → VALIDATE → STORE como pasos operacionales explícitos.
