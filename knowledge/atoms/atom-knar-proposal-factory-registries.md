---
id: atom-knar-proposal-factory-registries
title: Factory y registros son colaboradores propuestos para materializar nodos
five_wh_one_plus: how
tags:
- system:knar
- topic:materialization
- domain:system_architecture
- kind:software
- impl:pending
provenance: Derivado de docs/knowledge-native-runtime/technical/README.md y del modelo
  técnico asociado. Propuesta del asistente; no decisión aprobada del spec.
---

# Factory y registros son colaboradores propuestos para materializar nodos

## Answer

El diseño técnico propone NodeRegistry para resolver definiciones, RuntimeRegistry para seleccionar backends y NodeFactory para construir nodos configurados. Esa distribución de responsabilidades es una posible implementación de la resolución y materialización exigidas por el spec.
