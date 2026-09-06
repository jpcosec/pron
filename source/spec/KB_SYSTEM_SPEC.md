# KB System Spec

## Estado
Draft 0.1

## Objetivo
Definir un sistema de base de conocimiento sobre **SLDB** que:

- preserve trazabilidad fuerte hacia fuentes originales
- permita trabajar con conocimiento atómico
- separe evidencia, anotación y destilación
- mantenga `deskops` solo como capa operativa

## Capas

### 1. Capa operativa
Usa `deskops` para:

- board
- tasks
- rituales
- coordinación de trabajo

No es la capa principal de conocimiento.

### 2. Capa de fuentes
Contiene artefactos originales, inmutables.

Ejemplos:

```text
sources/
  apos-book.pdf
```

Regla:
- las fuentes no se editan
- se referencian por ruta + hash

### 3. Capa de biopsias / samples
Una **biopsia** es un corte trazable de una fuente.

Sirve para:
- apuntar a un fragmento exacto de la fuente
- declarar el método de anclaje usado
- fijar evidencia local verificable
- permitir anotación inline posterior

La biopsia es el puente entre la fuente y el átomo.

### 4. Capa de átomos
Los átomos contienen conocimiento destilado y estable.

No dependen directamente del PDF.
Dependen de una o más biopsias.

## Estructura propuesta

```text
project/
  sources/
  knowledge/
    samples/
    atoms/
  knowledge_models/
  .sldb/
  desk/
```

## Principio central

### Fuente → Biopsia → Átomo

- **fuente**: artefacto original
- **biopsia**: fragmento localizado y verificable
- **átomo**: conocimiento abstraído y reusable

## Requisitos de trazabilidad

Cada biopsia debe permitir responder:

- ¿de qué archivo salió?
- ¿de qué versión exacta del archivo salió?
- ¿qué método de anchor se usó?
- ¿qué fragmento exacto se cortó?
- ¿cómo volver al lugar original?

## Modelo 1: `SourceSampleDoc`

Documento SLDB para biopsias.

### Campos mínimos

- `id`
- `title`
- `source_path`
- `source_title`
- `source_hash_sha256`
- `anchor_method`
- `chapter`
- `section`
- `page_start`
- `page_end`
- `anchor_text`
- `exact_quote`
- `prefix`
- `suffix`
- `sample_text_hash_sha256`
- `tags`

### Semántica

- el frontmatter guarda la localización y verificabilidad
- el cuerpo contiene el fragmento textual editable/anotable
- el cuerpo puede usar marcado inline estilo `marcado`

## Modelo 2: `KnowledgeAtomDoc`

Documento SLDB para conocimiento destilado.

### Campos mínimos

- `id`
- `title`
- `question`
- `answer`
- `provenance`
- `tags`

### `provenance`

Debe apuntar a biopsias, no directamente al PDF, por ejemplo:

```yaml
provenance:
  - sample_id: sample-apos-ch4-span-definition
    relation: distilled_from
```

## Metodología de anchor

No inventar metodologías nuevas si ya existen.

`anchor_method` debe declarar métodos usados, por ejemplo:

- `w3c:text-quote-selector`
- `w3c:text-position-selector`
- `pdf-fragment:page`
- `pdf:anchor-text`
- `hypothesis:fuzzy-quote-anchor`

Puede ser una lista.

## Estrategia de anchor recomendada

Usar anchor híbrido:

- hash del archivo fuente
- página
- capítulo/sección si existen
- `anchor_text`
- `exact_quote`
- `prefix`
- `suffix`

Esto permite:
- navegación humana
- reanclaje
- validación

## Hashes

### Hash obligatorio de fuente

`source_hash_sha256`

Sirve para probar que la biopsia fue tomada del mismo PDF original.

### Hash opcional del corte

`sample_text_hash_sha256`

Sirve para detectar alteraciones del texto del sample.

## Relación con `marcado`

`marcado` no se aplica al PDF.

`marcado` se aplica al **sample**.

### Regla

- PDF: fuente inmutable
- sample: superficie de anotación
- atom: superficie de conocimiento estable

## Ejemplo de sample

```md
---
id: sample-apos-ch4-span-definition
title: Construcción de span desde combinaciones lineales
source_path: sources/apos-book.pdf
source_title: APOS Theory
source_hash_sha256: "..."
anchor_method:
  - w3c:text-quote-selector
  - pdf-fragment:page
  - pdf:anchor-text
chapter: "4"
section: "4.2.3"
page_start: 36
page_end: 37
anchor_text: "Given a vector space V with a specific scalar field K"
exact_quote: "Given a vector space V with a specific scalar field K, students perform Actions..."
prefix: "Mental Constructions"
suffix: "The reversal of this Process"
sample_text_hash_sha256: "..."
tags:
  - system:apos
  - topic:spanning-set-and-span
  - layer:source
---
```

Cuerpo:

```md
<!-- sem:concept.spanning_set -->
Given a vector space V with a specific scalar field K, students perform Actions...
<!-- /sem:concept.spanning_set -->
```

## Ejemplo de átomo

```md
---
id: atom-span-construction-starts-from-actions-on-linear-combinations
title: La construcción de span comienza con acciones sobre combinaciones lineales
question: how
provenance:
  - sample_id: sample-apos-ch4-span-definition
    relation: distilled_from
tags:
  - system:apos
  - topic:spanning-set-and-span
  - layer:applications
---
```

## Invariantes

### Fuente
- no se edita
- se identifica por ruta + hash

### Biopsia
- debe ser reversible hacia la fuente
- debe declarar método de anchor
- debe guardar evidencia textual suficiente
- no necesita un tamaño uniforme; necesita direccionabilidad y verificación

### Átomo
- debe ser pequeño
- debe responder una sola pregunta 5WH1+
- debe poder rastrearse a una o más biopsias
- debe ganar profundidad por composición, no por inflación

## Flujo recomendado

Este flujo es una disciplina operativa recomendada, no una máquina rígida de
fases del sistema.

1. registrar fuente
2. calcular hash
3. crear biopsia
4. anotar biopsia inline con `marcado`
5. destilar átomo
6. enlazar átomo a sample vía provenance
7. indexar con SLDB

## Beneficios

- mejor provenance
- desacople entre fuente y conocimiento
- uso real de `marcado`
- modelos SLDB más limpios
- deduplicación más fácil
- auditoría más fuerte

## Próximos pasos

1. implementar `SourceSampleDoc`
2. ajustar `KnowledgeAtomDoc` para provenance por `sample_id`
3. crear primer sample real desde el PDF APOS
4. definir convención de hashes
5. decidir si habrá capa derivada `derived/` para texto/layout del PDF
