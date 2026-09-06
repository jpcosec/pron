---
id: atom-knar-sql-nodo
title: Un nodo SQL expone un contrato de consulta tipado
five_wh_one_plus: how
tags:
- system:knar
- topic:sql_node
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 13. Declaración del spec; no prueba
  de implementación.
---

# Un nodo SQL expone un contrato de consulta tipado

## Answer

La base de datos puede exponerse como un nodo que recibe CustomerQuery y devuelve CustomerRecordSet. El runtime PostgreSQL encapsula la ejecución SQL, mientras el orquestador trabaja con tipos y capacidades como consultar clientes o agregar pedidos.
