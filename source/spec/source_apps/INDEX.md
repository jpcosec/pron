# Source Apps Index

## Propósito
Este índice resume las aplicaciones/herramientas revisadas en:

- `/home/jp/proyectos/hum-ecosystem/tools`

y organiza qué clase de valor pueden aportar a una nueva aplicación comprehensiva de knowledge management.

Los documentos detallados viven en este mismo directorio.

---

## Vista rápida por rol

### Núcleo de conocimiento
Estas son las fuentes más importantes para el core de la nueva app.

- [`sldb.md`](./sldb.md)
  - contratos documentales
  - tracking
  - store
  - indexación
  - búsqueda estructurada

- [`marcado.md`](./marcado.md)
  - marcado semántico inline
  - anchors
  - rangos
  - validación
  - anotación sobre samples

- [`kgdb.md`](./kgdb.md)
  - persistencia de grafo
  - relaciones tipadas
  - queries deterministas
  - trazabilidad entre entidades

### Capa operativa / experiencia CLI
Estas fuentes importan para la UX, la disciplina de trabajo y la experiencia de uso.

- [`deskops.md`](./deskops.md)
  - CLI humana
  - atoms
  - tasks / board / rituals
  - acoplamiento entre trabajo y conocimiento

### Modelado semántico / ontológico
Estas fuentes ayudan a pensar el nivel de formalización del conocimiento.

- [`ontomap.md`](./ontomap.md)
  - ontologías RDF/OWL
  - dimensiones semánticas
  - proyecciones

- [`tractatusIR.md`](./tractatusIR.md)
  - ideas experimentales de semántica y representación de grafos
  - vocabulario conceptual y patrones de razonamiento potencialmente recuperables

### UI / visualización / surfaces de operador
Estas fuentes son relevantes para cómo ver, editar y navegar el conocimiento.

- [`sldb-ui.md`](./sldb-ui.md)
  - UI para documentos marcados
  - source vs rendered
  - marker inspection
  - edición asistida

- [`graph_ui.md`](./graph_ui.md)
  - edición/inspección visual de grafos
  - arquitectura reusable de graph editor

- [`spec2viz.md`](./spec2viz.md)
  - materialización de conocimiento estructurado en diagramas y charts

### Ingesta / adquisición
Fuentes relevantes si la nueva app tendrá pipelines para capturar conocimiento desde fuera.

- [`hum-scrapper.md`](./hum-scrapper.md)
  - automatización
  - memoria semántica entre runs
  - adquisición estructurada

### Infraestructura adyacente
No es KM directo, pero puede aportar ideas transferibles.

- [`repopackage.md`](./repopackage.md)
  - contratos tipados
  - composición federada
  - trazabilidad entre componentes

---

## Lectura recomendada por prioridad

### Prioridad 1: entender el core de la KB
1. [`sldb.md`](./sldb.md)
2. [`marcado.md`](./marcado.md)
3. [`kgdb.md`](./kgdb.md)
4. [`deskops.md`](./deskops.md)

Razón:
- aquí está la mayor parte de la infraestructura y UX que ya resuelve problemas centrales de knowledge management

### Prioridad 2: entender modelado y surfaces
5. [`ontomap.md`](./ontomap.md)
6. [`sldb-ui.md`](./sldb-ui.md)
7. [`graph_ui.md`](./graph_ui.md)
8. [`spec2viz.md`](./spec2viz.md)

Razón:
- ayudan a decidir ontología, interfaces y vistas derivadas

### Prioridad 3: entender expansión futura
9. [`hum-scrapper.md`](./hum-scrapper.md)
10. [`tractatusIR.md`](./tractatusIR.md)
11. [`repopackage.md`](./repopackage.md)

Razón:
- aportan ideas para ingestión avanzada, semántica experimental o federación futura

---

## Qué extraer de cada una, en una línea

- **deskops** → disciplina atómica + UX CLI + workflow de producción de conocimiento
- **sldb** → contratos documentales + store + tracking + indexación
- **marcado** → anotación inline + anchors + validación de markup/rangos
- **kgdb** → capa grafo para relaciones y trazabilidad
- **ontomap** → ontología explícita y dimensiones semánticas
- **sldb-ui** → operator surface para documentos marcados
- **graph_ui** → operator surface para grafos y lineage visual
- **spec2viz** → proyecciones visuales de conocimiento estructurado
- **hum-scrapper** → pipelines de adquisición con memoria semántica
- **tractatusIR** → ideas experimentales de semántica relacional
- **repopackage** → contratos/federación/composición entre espacios independientes

---

## Cómo usar este índice

Si la meta es diseñar una app nueva, este índice sugiere una estrategia:

1. estudiar primero el núcleo funcional ya probado
2. separar lo metodológico de lo accidental en cada herramienta
3. preservar disciplina y UX valiosas
4. evitar copiar límites históricos de implementación
5. sintetizar luego un diseño unificado

En particular:

- no copiar `desk/` como contenedor por defecto solo porque hoy existe
- no perder la disciplina 5WH1+ y la composabilidad de los átomos
- no perder el store y tracking estructurado de SLDB
- no perder el valor de anchors/anotación que aporta Marcado
- no perder la trazabilidad relacional que sugiere KGDB

---

## Siguiente paso sugerido

Luego de este índice, conviene producir uno de estos dos artefactos:

1. **mapa de capacidades**
   - capability → source app → keep / adapt / discard

2. **arquitectura sintetizada**
   - qué componentes tendrá la nueva app
   - de qué herramienta viene cada idea
   - qué decisiones unifican todo en un sistema coherente
