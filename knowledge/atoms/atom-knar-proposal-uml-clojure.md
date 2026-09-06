---
id: atom-knar-proposal-uml-clojure
title: Los diagramas de clases representan protocolos y datos además de clases OO
five_wh_one_plus: how
tags:
- system:knar
- topic:representation
- domain:knowledge_representation
- kind:concept
- impl:pending
provenance: Derivado de docs/knowledge-native-runtime/technical/README.md y del modelo
  técnico asociado. Propuesta del asistente; no decisión aprobada del spec.
---

# Los diagramas de clases representan protocolos y datos además de clases OO

## Answer

La documentación técnica interpreta protocol como defprotocol, record como defrecord o mapa validado, y un colaborador class como un namespace de funciones con dependencias inyectadas cuando se usa Clojure. Esta convención de lectura permite usar UML sin imponer una jerarquía orientada a objetos al runtime.
