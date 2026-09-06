---
id: atom-knar-resolver-objetivo
title: El orquestador resuelve un objetivo mediante capacidades y nodos compatibles
five_wh_one_plus: how
tags:
- system:knar
- topic:planning
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 18. Declaración del spec; no prueba
  de implementación.
---

# El orquestador resuelve un objetivo mediante capacidades y nodos compatibles

## Answer

Para satisfacer un objetivo, el orquestador resuelve las capacidades necesarias, encuentra nodos adecuados y obtiene sus inputs del contexto. Después verifica tipos y construye el execution graph que coordinará esas piezas.
