---
id: atom-knar-compatibilidad-antes-de-ejecutar
title: La compatibilidad de puertos se valida antes de ejecutar
five_wh_one_plus: when
tags:
- system:knar
- topic:type_compatibility
- domain:code_craft
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 5, 18, 23. Declaración del spec;
  no prueba de implementación.
---

# La compatibilidad de puertos se valida antes de ejecutar

## Answer

El orquestador comprueba que una salida sea compatible con la entrada a la que se conecta antes de ejecutar el pipeline. Esa validación permite detectar conexiones inválidas sin depender de lo que ocurra durante una invocación.
