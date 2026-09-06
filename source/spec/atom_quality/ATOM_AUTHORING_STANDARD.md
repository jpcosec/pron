# Atom Authoring Standard

## Estado

Borrador operativo.

## Propósito

Definir el estándar base de qué es un átomo, qué debe contener y qué no debe contener.

---

## 1. Definición práctica de átomo

Un átomo es una **unidad pequeña, estable y reusable de conocimiento** que responde una sola pregunta 5WH1+ sobre una afirmación claramente delimitada.

Un átomo no es:

- una nota de brainstorming
- una mini-sección de documento pegada sin destilar
- una lista de ideas vagamente relacionadas
- un resumen largo de un capítulo
- una task camuflada como conocimiento

---

## 2. Invariantes del estándar

Todo átomo debe respetar estos invariantes.

### 2.1 Una pregunta principal

El `five_wh_one_plus` define la pregunta dominante del átomo.

Ejemplo:

- `what` para definición o caracterización principal
- `why` para justificación o razón estructural
- `how` para mecanismo o criterio operativo
- `how_not` para constraint o anti-patrón

No conviene mezclar en un mismo answer:

- qué es una cosa
- por qué importa
- cómo implementarla

a menos que una de esas funciones sea claramente subordinada a la principal.

### 2.2 Una afirmación principal

Cada átomo debe tener una sola tesis nuclear.

Sí puede:

- introducir una distinción necesaria
- aclarar una consecuencia directa
- precisar una frontera con conceptos vecinos

No debe:

- apilar varias tesis independientes
- mezclar definición con workflow entero
- comprimir una taxonomía completa en un solo atom

### 2.3 Respuesta durable

El answer debe poder seguir siendo útil aunque cambien:

- herramientas concretas
- carpetas transitorias
- orden de implementación
- nombre de tareas actuales

La formulación puede mencionar superficies actuales, pero no debe depender enteramente de ellas.

### 2.4 Reuse por recomposición

Un átomo bueno debe poder reutilizarse luego en:

- composiciones
- revisiones
- decisiones de modelado
- criterios de migración
- explicaciones arquitectónicas

---

## 3. Estructura estándar

Formato recomendado:

```md
---
id: atom-...
title: ...
five_wh_one_plus: what|why|how|how_not|when|where|for_whom
tags:
  - ...
provenance: Derived from `...`.
---

# Título del átomo

## Answer

Respuesta compacta, clara y sustantiva.
```

---

## 4. Estándar del answer

### 4.1 Longitud orientativa

No hay longitud rígida, pero en general un buen answer suele requerir:

- más que una reformulación del título
- menos que un mini-ensayo largo

Rango orientativo:

- 2 a 4 frases compactas en la mayoría de los casos

### 4.2 Estructura sugerida del answer

Un patrón útil es:

1. afirmación principal
2. distinción relevante
3. implicación o utilidad

### 4.3 Lo que el answer debe evitar

- tautologías
- frases puramente decorativas
- justificaciones tan genéricas que servirían para cualquier átomo
- referencias implícitas a “lo hablado antes”
- lenguaje excesivamente provisional si la idea ya está suficientemente clara

---

## 5. Estándar de tags

Los tags del átomo sirven como **facetas ligeras de recuperación semántica**.
No deben cargarse con toda la semántica profunda ni con metadata de gobernanza sobre el átomo.

La metadata sobre el átomo vive ahora en un espacio separado, ver `source/spec/ATOM_METADATA_DOC.md`.

### 5.1 Mínimo recomendado

Cada átomo debería tener al menos:

- `system:...`
- `topic:...`

### 5.2 Tags frecuentes según el tipo de átomo

Según el caso, también pueden aparecer:

- `layer:*`
- `entity:*`
- `graph:*`
- `domain:*`
- `cross:*`

### 5.3 Regla de humildad semántica

Si una distinción es estructuralmente importante, no debe vivir solo como tag.
Debe vivir también en:

- el título
- el answer
- o eventualmente relaciones/nodos explícitos futuros

---

## 6. Estándar de procedencia

Por compatibilidad con el modelo actual, el átomo sigue declarando procedencia explícita en el frontmatter `provenance`.
La metadata de gobernanza asociada a esa procedencia ya no debe cargarse en tags del átomo; debe vivir en el espacio de metadata, ver `source/spec/ATOM_METADATA_DOC.md`.

### 6.1 Procedencia mínima aceptable

Nombrar el spec, doc o fuente concreta de donde se deriva la afirmación.

### 6.2 Procedencia de síntesis

Si el átomo combina varias fuentes, debe decirlo claramente.

Ejemplo:

```yaml
provenance: Derived from `source/spec/GRAPH_ARCHITECTURE.md` and `source/spec/ATOM_CONCEPT_GRAPH.md`.
```

### 6.3 Honestidad epistemológica

La procedencia no debe exagerar el grounding.
No es lo mismo:

- inferido desde specs
- sostenido por sample explícito
- validado contra fuente versionada

---

## 7. Clasificación de gobernanza recomendada

Conviene que cada átomo pueda clasificarse por rol principal para revisión y
gobernanza, pero esa clasificación pertenece al metadata registry, no al
núcleo semántico del tagset del átomo.

Ejemplos frecuentes:

- `role:definition`
- `role:constraint`
- `role:governance_rule`
- `role:relation`
- `role:workflow_rule`
- `role:migration_rule`
- `role:retrieval_rule`
- `role:modeling_rule`

---

## 8. Anti-patrones

No crear átomos que sean principalmente:

- placeholders sin curación
- duplicados casi idénticos
- resúmenes demasiado grandes
- reglas demasiado contextuales a una task puntual
- títulos precisos con answers genéricos
- opiniones vagas sin procedencia
- taxonomías enteras colapsadas en una sola pieza

---

## 9. Criterio final

Un átomo cumple el estándar cuando:

- su afirmación principal es clara
- su answer agrega sustancia real
- su procedencia es explícita
- sus tags permiten encontrarlo
- su formulación es reusable y razonablemente estable
