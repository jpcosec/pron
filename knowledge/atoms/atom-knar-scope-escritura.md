---
id: atom-knar-scope-escritura
title: Un nodo no puede escribir fuera de su scope
five_wh_one_plus: how_not
tags:
- system:knar
- topic:permissions
- domain:governance
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 23. Declaración del spec; no prueba
  de implementación.
---

# Un nodo no puede escribir fuera de su scope

## Answer

Las escrituras de un nodo deben quedar dentro del scope autorizado en su definición. Declarar ese límite tiene una consecuencia de ejecución: el sistema debe impedir escrituras que lo excedan.
