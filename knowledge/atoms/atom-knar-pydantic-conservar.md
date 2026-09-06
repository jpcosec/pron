---
id: atom-knar-pydantic-conservar
title: Los modelos Python y Pydantic se conservan durante la integración inicial
five_wh_one_plus: how_not
tags:
- system:knar
- topic:migration
- domain:system_architecture
- kind:software
- impl:pending
provenance: Derivado de source/spec.md, secciones 21. Declaración del spec; no prueba
  de implementación.
---

# Los modelos Python y Pydantic se conservan durante la integración inicial

## Answer

La incorporación del runtime no requiere migrar inmediatamente los modelos existentes en Python/Pydantic. El spec propone conservar esa capa mientras se conecta con AgentSpec y la ejecución en Clojure.
