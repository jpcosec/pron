# sldb

## Qué es
Infraestructura de documentos estructurados en Markdown.
Permite modelar, renderizar, extraer, trackear, indexar y consultar documentos con contratos Pydantic y un store `.sldb`.

## Por qué importa para la nueva app
Es probablemente la pieza más central del stack de conocimiento actual.
Resuelve la capa documental estructurada y el store de modelos/documentos.

## Qué deberíamos recuperar

### 1. Contratos de documento
- modelos `StructuredNLDoc`
- templates reversibles
- mapeo entre frontmatter/cuerpo y campos estructurados
- validación por contrato

### 2. Store e indexación
- tracking de documentos
- registro de modelos
- hashes e integridad
- índices semánticos y físicos
- metadata de secciones

### 3. Operaciones de documento
- create
- track
- update
- recover
- compose
- field-level operations

### 4. Query surface
- búsqueda física
- búsqueda semántica
- navegación por fields/sections/docs/models

### 5. Filosofía importante
- el Markdown es la superficie fuente
- el store es la capa indexada y consultable
- no duplicar verdad semántica innecesariamente

## Qué no deberíamos heredar sin revisión
- cualquier complejidad accidental del CLI actual
- límites del modelo si la app nueva necesita workflows más nativos para samples, atoms y evidence

## Preguntas de extracción
- ¿Qué partes de SLDB son indispensables como núcleo?
- ¿Cómo representa tracking, hashes, sections y semantic indexes?
- ¿Qué patrones conviene elevar a primitivas nativas en la nueva app?
- ¿Cómo soportar mejor sample → atom sin perder compatibilidad conceptual?