---
id: atom-knar-puertos-tipados
title: Los puertos definen entradas y salidas tipadas
five_wh_one_plus: what
tags:
- system:knar
- topic:ports
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 5, 23, 24. Declaración del spec;
  no prueba de implementación.
---

# Los puertos definen entradas y salidas tipadas

## Answer

Cada nodo expone `InputPort<T>` y `OutputPort<T>`, identificando el tipo de los datos que recibe y entrega. El contrato tipado organiza la comunicación entre componentes y permite componer transformaciones mediante artefactos estructurados.
