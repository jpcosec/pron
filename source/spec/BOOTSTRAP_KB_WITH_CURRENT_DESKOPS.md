# Bootstrap KB with Current Deskops

## Estado
Draft

## Propósito
Definir cómo construir una primera base de conocimiento usando los átomos actuales de `deskops`, de forma que:

- podamos empezar a trabajar ya
- no bloqueemos la arquitectura futura
- lo producido hoy siga siendo útil cuando existan:
  - samples/biopsias verificables
  - provenance fuerte
  - concept graph explícito
  - structural graph derivado de AST/DOM/layout
  - soporte multi-source real

Este documento asume como punto de partida principal el corpus actual de átomos en proyectos como:

- `/home/jp/Upla/tutor_apoe/desk/atoms/`

Y se apoya conceptualmente en:

- `/home/jp/Upla/source/spec/GRAPH_ARCHITECTURE.md`
- `/home/jp/Upla/source/spec/ATOM_CONCEPT_GRAPH.md`
- `/home/jp/Upla/source/spec/MULTI_SOURCE_ANCHORING.md`
- `/home/jp/Upla/source/spec/LEGACY_EXTRACTION_FROM_HUM_ECOSYSTEM.md`
- `/home/jp/Upla/source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md`

---

## 1. Tesis principal

Debemos tratar los átomos actuales de Deskops como:

> una **superficie bootstrap canónica de trabajo** para la KB inicial,
> pero no como el modelo final completo de conocimiento.

Eso implica una posición intermedia muy precisa:

- **sí**: usar los átomos actuales como base operativa real
- **no**: congelar la arquitectura alrededor de las limitaciones actuales de `AtomDoc`

## Fórmula corta

- los átomos actuales son **válidos como knowledge units**
- son **insuficientes como sistema final de provenance y estructura**
- por eso deben integrarse como una **capa bootstrap compatible**, no como punto terminal

---

## 2. Qué estamos bootstrappeando exactamente

En esta fase inicial, lo que se construye no es todavía toda la arquitectura futura.

Se construye una primera KB que ya permita:

1. usar los átomos existentes como corpus real
2. indexarlos y consultarlos con más rigor
3. empezar a derivar grafo conceptual y grafo de provenance mínimo
4. preparar la futura llegada de samples/biopsias
5. evitar retrabajo destructivo cuando migremos a modelos más ricos

## Lo que sí existe ya

- átomos en `desk/atoms/`
- ids estables
- `five_wh_one_plus`
- tags namespaced
- títulos y respuestas curadas
- una taxonomía de carpetas
- en muchos casos, una sección `Procedencia` humana

## Lo que todavía no existe de forma robusta

- sample docs explícitos
- anchor bundles estructurados
- source hash binding fuerte
- provenance por `sample_id`
- concept graph explícito como nodos/edges
- structural graph explícito

---

## 3. Invariante central de compatibilidad futura

Todo lo que hagamos ahora debe respetar este principio:

> ninguna decisión del bootstrap debe impedir que un átomo actual pueda ser re-expresado más adelante como `Atom` con provenance a `Sample`, concept placement explícito y soporte estructural enriquecido.

En práctica, eso significa:

- no destruir ids actuales
- no romper la atomicidad 5WH1+
- no mezclar múltiples ideas en un solo átomo “por conveniencia”
- no usar tags como única semántica profunda
- no inventar un provenance fake para llenar huecos
- no acoplar la KB final a `desk/` como único workspace material

---

## 4. Qué debe permanecer estable desde ya

## 4.1 Identidad del átomo

El `id` actual de los átomos debe tratarse como estable y preservable.

Ejemplo:
- `atom-action-is-a-core-mental-structure-in-apos`

### Regla

El bootstrap debe asumir que estos ids:
- seguirán existiendo
- podrán mapearse luego a modelos más ricos
- no deben regenerarse arbitrariamente

## 4.2 Disciplina 5WH1+

El principio de:
- un átomo responde una sola pregunta 5WH1+

ya es valioso y debe preservarse.

### Regla

No ampliar átomos existentes para meter más contenido solo porque la provenance aún sea pobre.
La profundidad futura debe venir por composición, no por inflación del átomo.

## 4.3 Contenido curado del answer

Las respuestas ya materializadas representan trabajo curatorial real.

### Regla

Deben tratarse como activos de conocimiento válidos, no como simple borrador desechable.

## 4.4 Tags existentes

Los tags actuales deben mantenerse porque ya sirven para:
- retrieval
- agrupación
- continuidad operativa

### Regla

Mantenerlos, pero reinterpretarlos como:
- facets
- no ontología final completa

## 4.5 Ubicación taxonómica existente

La organización por carpetas y la taxonomía documentada son valiosas.

### Regla

No tirarlas.
Deben convertirse en insumo del futuro concept graph.

---

## 5. Qué debemos considerar temporal / transicional

## 5.1 `desk/atoms/` como hogar material principal

Esto sirve hoy, pero no debería dictar la arquitectura final.

### Regla

Usarlo como superficie bootstrap, pero diseñar todo de forma que luego pueda coexistir o migrar a:
- `knowledge/atoms/`
- o a otra superficie más explícitamente KB-first

## 5.2 `AtomDoc` como contrato suficiente

`deskops.models:AtomDoc` es útil para bootstrap, pero insuficiente para el futuro.

### Regla

No asumir que `AtomDoc` agota lo que un átomo deberá expresar más adelante.
Especialmente en:
- provenance
- concept placement
- structural support

## 5.3 `Procedencia` en texto libre

La procedencia humana existente es valiosa, pero no es todavía provenance estructurada fuerte.

### Regla

Tratarla como:
- evidencia transicional
- insumo de migración
- no como validación determinista final

---

## 6. Estrategia general del bootstrap

Este bootstrap no debe gestionarse como un roadmap rígido por fases.
La organización operativa puede vivir en `desk/tasks` y `desk/drawers` sin
congelar aquí una secuencia ceremonial que luego nos estorbe.

## 6.1 Declarar el corpus actual como KB inicial válida

Debemos poder decir sin vergüenza:

- la KB inicial existe
- está en los átomos actuales
- ya produce valor

Pero también:

- su provenance es parcial
- su concept graph es implícito
- su structural graph es inexistente o embrionario

## 6.2 Extraer estructura explícita sin reescribir el corpus

En vez de reescribir todos los átomos ya, conviene derivar capas nuevas a partir de ellos:

1. facet layer
2. taxonomy/concept layer
3. provenance-minimum layer
4. graph materialization layer

## 6.3 Introducir samples hacia adelante, no retroforzar todo de una vez

No hace falta reconstruir toda la KB histórica antes de seguir avanzando.

Conviene permitir que:
- nuevos trabajos ya generen samples explícitos
- átomos viejos puedan seguir existiendo con provenance mínima
- migraciones históricas se hagan progresivamente

---

## 7. Qué construir primero sobre los átomos actuales

## 7.1 Un índice KB explícito de los átomos actuales

Aunque vivan en `desk/atoms/`, debemos empezar a tratarlos como corpus de KB.

Esto implica derivar o registrar al menos:
- `atom_id`
- path
- title
- question type
- tags
- taxonomy path
- provenance text presence/absence

## Compatibilidad futura

Este índice puede luego ampliarse con:
- `sample_ids`
- `concept_ids`
- `supporting_structure_ids`

sin invalidar lo ya hecho.

## 7.2 Un concept graph derivado de taxonomía + tags

Primero no hace falta resolver toda la ontología.
Sí conviene derivar desde ya:

- `ConceptGroup`
- `TaxonomyNode`
- `QuestionType`
- `TagFacet`
- links básicos desde `Atom`

### Insumos claros

- taxonomía de carpetas
- `apos-atom-taxonomy.md`
- tags existentes

## Compatibilidad futura

Luego esto puede refinarse con:
- `Concept` explícitos
- relaciones átomo-átomo curadas
- relaciones concepto-concepto más profundas

## 7.3 Un provenance-minimum model

Sin inventar samples aún, conviene tener un modelo transicional de provenance mínima.

Por ejemplo, por átomo:
- source_path textual
- source_title textual
- chapter/section si aparece
- provenance_status

### Importante

Esto no sustituye `Sample`.
Solo reconoce que algunos átomos tienen mejor o peor grounding textual hoy.

### Estados sugeridos

- `none`
- `textual_only`
- `located_humanly`
- `sample_linked`
- `validated`

## Compatibilidad futura

Cuando existan samples reales, este layer se sustituye o se subordina a provenance por `sample_id`.

## 7.4 Un grafo inicial materializado

Aun con información incompleta, ya podemos materializar un primer grafo con al menos:

- `Atom`
- `TaxonomyNode`
- `ConceptGroup`
- `QuestionType`
- `TagFacet`
- opcionalmente `SourceStub`

### Edges mínimos

- `located_in_taxonomy`
- `grouped_under`
- `child_of`
- `has_question_type`
- `tagged_with`
- `provisionally_grounded_in`

### Importante

Usar `provisionally_grounded_in` o equivalente evita mentir diciendo `distilled_from Sample` cuando aún no hay sample.

---

## 8. Capas de compatibilidad que debemos diseñar ahora

## 8.1 Compatibilidad con futuros Sample docs

Todo átomo actual debe poder recibir más adelante:
- uno o varios `sample_ids`
- relaciones `distilled_from`
- relaciones `supports`

### Regla

No usar un modelo bootstrap que haga imposible múltiples fuentes/sample por átomo.

## 8.2 Compatibilidad con concept graph explícito

Los tags actuales no deben ser la única semántica estructurada.

### Regla

Desde ya separar conceptualmente:
- `TagFacet`
- `TaxonomyNode`
- `QuestionType`
- y luego `Concept`

Aunque al inicio se superpongan parcialmente.

## 8.3 Compatibilidad con structural graph

Hoy quizás no tengamos AST/DOM/layout support explícito para estos átomos.

### Regla

El modelo bootstrap no debe cerrar la puerta a que mañana un átomo quede conectado a:
- `SourceSection`
- `Symbol`
- `ASTNode`
- `LayoutRegion`

## 8.4 Compatibilidad con multi-source

Hoy muchos átomos vienen de un libro PDF.
Mañana vendrán de:
- repos git
- código
- markdown
- webpages
- otras fuentes

### Regla

No diseñar el bootstrap como si todo fuera “chapter + section + page”.
Si se usa provenance mínima, debe ser extensible y typed.

## 8.5 Compatibilidad con nueva superficie documental

Aunque usemos `desk/atoms/`, el diseño lógico debe ser independiente del path físico.

### Regla

Siempre separar:
- identidad lógica del átomo
- ubicación física actual del archivo

---

## 9. Qué NO hacer ahora

## 9.1 No convertir tags en ontología definitiva

Sería el error más grave.

### No hacer
- asumir que `topic:*` ya resuelve toda la estructura conceptual
- congelar taxonomía compleja en strings planos únicamente

## 9.2 No fingir provenance fuerte donde no la hay

### No hacer
- inventar samples retroactivamente sin evidencia
- declarar validación exacta si no existe
- confundir procedencia textual humana con provenance validada

## 9.3 No reescribir masivamente átomos por ansiedad arquitectónica

### No hacer
- migraciones destructivas grandes antes de fijar modelo de transición
- renombrados innecesarios de ids
- reorganizaciones físicas que rompan continuidad sin necesidad

## 9.4 No acoplar el futuro a Deskops como único hogar

### No hacer
- tratar `desk/atoms/` como destino final
- hacer que toda consulta o lógica dependa semánticamente del path `desk/`

---

## 10. Qué sí introducir desde ya

## 10.1 Un vocabulario de estados de grounding

Esto permite distinguir honestamente entre:
- átomo útil pero débilmente fundado
- átomo con localización humana
- átomo ya sampleado
- átomo validado

## 10.2 Un layer explícito de taxonomy extraction

Debe existir una forma de derivar:
- `ConceptGroup`
- `TaxonomyNode`
- path jerárquico

sin depender solo de lectura humana del árbol de carpetas.

## 10.3 Un adapter para leer átomos Deskops como input KB

Más que editarlos todos ya, conviene tener un lector/ingestor que sepa convertir `AtomDoc` actual en una representación interna bootstrap.

### Ese adapter debería extraer
- id
- title
- answer
- five_wh_one_plus
- tags
- folder-derived taxonomy path
- provenance text block si existe

## 10.4 Una noción explícita de “bootstrap source reference”

Mientras no haya samples reales, conviene poder asociar fuentes provisionales de forma typed.

Ejemplo conceptual:
- source ref textual
- source kind guess
- location note
- confidence/provenance status

## 10.5 Una tabla o store de correspondencias futuras

Algo como un mapping que luego pueda crecer:
- `atom_id -> sample_ids[]`
- `atom_id -> concept_ids[]`
- `atom_id -> source_refs[]`
- `atom_id -> structure_refs[]`

Aunque al inicio muchos valores estén vacíos.

---

## 11. Modelo transicional sugerido

## 11.1 Current desk atom (source surface)

Sigue viviendo en:
- `desk/atoms/...`

## 11.2 Bootstrap KB entity

Entidad interna derivada del átomo actual.

Campos sugeridos:
- `atom_id`
- `title`
- `question_type`
- `answer`
- `tag_facets[]`
- `taxonomy_path`
- `concept_group`
- `provenance_status`
- `provisional_source_refs[]`
- `raw_provenance_text`
- `path_current`

## 11.3 Future enriched atom entity

Más adelante podrá agregarse:
- `sample_ids[]`
- `concept_ids[]`
- `structure_support_ids[]`
- `composition_ids[]`

### Importante

Este diseño permite evolución monotónica.
No hace falta desechar la entidad bootstrap para pasar a la enriquecida.
Solo extenderla.

---

## 12. Estrategia de construcción incremental

## Etapa 1 — Declaración y lectura del corpus actual

Objetivo:
- reconocer oficialmente los átomos actuales como corpus KB bootstrap

Entregables:
- inventario de átomos
- parser/adapter de `AtomDoc`
- extracción de tags, taxonomy path y provenance text

## Etapa 2 — Materialización de facet/taxonomy graph

Objetivo:
- volver navegable la semántica ya implícita

Entregables:
- `ConceptGroup`
- `TaxonomyNode`
- `TagFacet`
- `QuestionType`
- relaciones básicas con `Atom`

## Etapa 3 — Provenance minimum registry

Objetivo:
- distinguir grounding real sin fingir sample system completo

Entregables:
- modelo/status de provenance mínima
- source refs provisionales
- queries para detectar átomos huérfanos o débiles

## Etapa 4 — Sample-first future path

Objetivo:
- permitir que nuevo trabajo ya produzca `SourceSampleDoc`

Entregables:
- convención de sample docs
- provenance por `sample_id` para trabajo nuevo
- convivencia entre átomos históricos y átomos enriquecidos

## Etapa 5 — Progressive backfill

Objetivo:
- migrar selectivamente átomos históricos importantes a soporte por samples reales

Entregables:
- pipelines de backfill
- prioridades por valor/confiabilidad/uso

---

## 13. Cómo usar Deskops sin hipotecarnos

Deskops debe usarse ahora como:

- surface operativa
- corpus bootstrap de átomos
- experiencia CLI útil

Pero no como:

- arquitectura final completa de la KB
- único hogar lógico del conocimiento
- modelo suficiente para provenance y concept graph futuros

## Regla estratégica

Usar Deskops como **punto de apoyo**, no como **frontera final**.

---

## 14. Decisión de diseño recomendada

Si hay que resumir todo en una sola decisión:

> construiremos primero una KB bootstrap sobre los átomos actuales de Deskops, agregando capas derivadas de taxonomy, facets y provenance mínima, de forma que cada átomo pueda luego enriquecerse con samples, concept graph explícito y structural support sin perder identidad ni valor curatorial.

---

## 15. Síntesis final

La mejor manera de empezar ahora sin romper el futuro es esta:

1. tratar los átomos actuales como corpus KB real
2. derivar de ellos una capa bootstrap explícita
3. separar desde ya:
   - facets
   - taxonomy
   - provenance mínima
4. no fingir todavía el sistema completo de samples
5. dejar preparados los puntos de extensión para:
   - `sample_ids`
   - `concept_ids`
   - `structure_support_ids`
   - composiciones

En una frase:

> el bootstrap debe respetar la realidad actual de Deskops, pero organizarla desde el primer día como una versión incompleta pero compatible del sistema futuro, no como un callejón sin salida arquitectónico.

---

## 16. Próximo paso sugerido

Después de este documento, conviene definir un artefacto más operativo:

- un **plan de implementación del bootstrap**

concretando al menos:

1. qué archivos y modelos vamos a crear primero
2. qué campos bootstrap tendrá cada átomo derivado
3. cómo materializar el primer concept/taxonomy graph
4. cómo registrar provenance mínima sin mentir
5. cómo convivirán el corpus actual y la futura capa `knowledge/`
