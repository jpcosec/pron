# ontomap

## Qué es
Implementación de un grafo ontológico multidimensional sobre RDF/OWL.
Modela entidades y relaciones con semántica explícita, usando propiedades de aristas en lugar de anidamiento estructural.

## Por qué importa para la nueva app
Aporta ideas para formalizar ontologías, dimensiones semánticas y proyecciones más rigurosas sobre el conocimiento.

## Qué deberíamos recuperar

### 1. Modelado ontológico explícito
- clases
- propiedades
- axiomas
- restricciones
- semántica de relaciones

### 2. Multidimensionalidad
- diferentes dimensiones semánticas sobre el mismo conjunto de entidades
- posibilidad de proyecciones según relación, no solo por carpeta o tag

### 3. Conversión y proyección
- loaders/dumpers
- proyecciones SPARQL
- exportaciones a diagramas

### 4. Valor conceptual
Puede ayudar a decidir si la nueva app necesita:
- solo tags y relaciones simples
- o una ontología formal para ciertos dominios

## Qué no deberíamos heredar sin revisión
- sobreformalización temprana
- dependencia total de RDF/OWL si la KB inicial necesita velocidad y simplicidad

## Preguntas de extracción
- ¿Qué partes del modelado ontológico son útiles ya?
- ¿Qué dimensiones deberían existir en la KB?
- ¿Cuándo conviene pasar de tags a relaciones/ontologías más formales?