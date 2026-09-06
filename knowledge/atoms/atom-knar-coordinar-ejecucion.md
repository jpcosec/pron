---
id: atom-knar-coordinar-ejecucion
title: La orquestación incluye observación, verificación y persistencia
five_wh_one_plus: how
tags:
- system:knar
- topic:orchestration
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 18. Declaración del spec; no prueba
  de implementación.
---

# La orquestación incluye observación, verificación y persistencia

## Answer

Tras construir el execution graph, el orquestador ejecuta los nodos, observa sus estados, verifica completion tests y persiste resultados. El ciclo de coordinación abarca por tanto las condiciones de término y el registro del resultado, además de lanzar invocaciones.
