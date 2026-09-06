# Legacy Extraction from hum-ecosystem

## Estado
Draft

## Propósito
Documentar qué partes de `/home/jp/proyectos/hum-ecosystem` siguen siendo conceptualmente valiosas para la nueva arquitectura de knowledge management que estamos definiendo.

Este documento no trata `hum-ecosystem` como archivo muerto.
Lo trata como una fuente histórica de:

- ideas arquitectónicas
- modelos intermedios
- intuiciones sobre estructura del conocimiento
- separación entre superficie documental, semántica operable y persistencia en grafo

La meta es distinguir:

- qué rescatar
- qué reinterpretar
- qué no copiar literalmente
- qué puede guiar una primera implementación compatible con el futuro sistema

---

## 1. Tesis principal

`/home/jp/proyectos/hum-ecosystem` todavía conserva una parte importante del esqueleto teórico de la arquitectura que ahora estamos reformulando de forma más concreta, multi-source y provenance-first.

Lo más valioso que queda ahí no es una implementación única lista para reusar, sino un conjunto de líneas convergentes sobre:

1. **pipeline superficie -> estructura operable -> grafo persistido**
2. **determinización del conocimiento**
3. **queryabilidad y materialización**
4. **semántica relacional más rica que un sistema plano de tags**

---

## 2. Fuentes principales revisadas

### Documentación general
- `/home/jp/proyectos/hum-ecosystem/docs/README.md`

### Conceptos
- `/home/jp/proyectos/hum-ecosystem/docs/concepts/KG_TREES.md`
- `/home/jp/proyectos/hum-ecosystem/docs/concepts/KNOWLEDGE_STRUCTURE_CHALLENGE.md`

### Arquitectura
- `/home/jp/proyectos/hum-ecosystem/docs/architecture/nl_sl_kg_pipeline.md`
- `/home/jp/proyectos/hum-ecosystem/docs/architecture/universal_knowledge_loop.md`
- `/home/jp/proyectos/hum-ecosystem/docs/architecture/graphlang/README.md`
- `/home/jp/proyectos/hum-ecosystem/docs/architecture/HUM_KNOWLEDGE_PACKAGE_MAP.md`
- `/home/jp/proyectos/hum-ecosystem/docs/architecture/HUM_MIGRATION_MAP.md`

### Órgano de conocimiento
- `/home/jp/proyectos/hum-ecosystem/core/knowledge/README.md`

### Ancestro de sistema hum
- `/home/jp/proyectos/hum-ecosystem/hum-core/README.md`

---

## 3. Lo más importante: KG-Trees como antecedente de la IR

Fuente:
- `/home/jp/proyectos/hum-ecosystem/docs/concepts/KG_TREES.md`

El documento define los KG-Trees como:

> "AST-like intermediate structures between structured surface input and persistent graph knowledge"

Y también dice:

> "an intermediate representation between document structure and graph memory"

## Qué recuperamos de ahí

Esta es probablemente una de las herencias más fuertes para la nueva arquitectura.

El principio que vale rescatar es:

- no conviene saltar directamente de documento a grafo persistido
- conviene tener una **representación intermedia operable**
- esa representación intermedia debe poder:
  - validarse
  - transformarse
  - reescribirse
  - aceptarse o rechazarse antes de persistir

## Relectura en la arquitectura nueva

Hoy eso se puede reinterpretar como una familia de IRs o estructuras intermedias, por ejemplo:

- proyecciones de fuente
- bundles de anchors
- samples validados
- colocaciones conceptuales de átomos
- relaciones graph-ready para provenance, concepto y estructura

## Conclusión

La idea de KG-Tree no debe copiarse literalmente sin revisión, pero sí debe recuperarse como patrón estructural:

> entre la superficie documental y el grafo persistido debe existir una forma intermedia operable.

---

## 4. La challenge de estructura del conocimiento: más que extraer átomos

Fuente:
- `/home/jp/proyectos/hum-ecosystem/docs/concepts/KNOWLEDGE_STRUCTURE_CHALLENGE.md`

El documento afirma explícitamente:

> "Knowledge ingestion is not just about extracting labels (atoms). It is about the reconstruction of a complex system where the relationships—both internal and external—generate emergent properties."

También resume implicaciones como:

1. `Ingestion is Systems Engineering`
2. `Context is Multi-dimensional`
3. `Emergence cannot be hardcoded`

## Qué recuperamos de ahí

Esto conecta de forma directa con el problema actual de los tags y de la taxonomía de átomos.

La lección fuerte es:

- no basta con extraer unidades atómicas aisladas
- importa reconstruir relaciones internas y externas
- importa reconocer dimensiones múltiples
- importa modelar emergencia sistémica, no solo listas de labels

## Relectura en la arquitectura nueva

Esto sostiene la necesidad de distinguir al menos:

- grafo de provenance
- grafo conceptual de átomos
- grafo estructural proyectado

Y sostiene también la crítica a usar tags como portador semántico principal.

## Conclusión

Este documento es un antecedente fuerte de la tesis actual:

> la KB no debe quedar reducida a un conjunto de átomos etiquetados; debe poder reconstruir sistemas relacionales.

---

## 5. NL -> SL -> KG como antecedente del pipeline document-first

Fuente:
- `/home/jp/proyectos/hum-ecosystem/docs/architecture/nl_sl_kg_pipeline.md`

Este documento formaliza el pipeline:

- `NL`: natural language crudo
- `SL`: structured surface language, gestionado por `sldb`
- `KG`: persistent graph knowledge, gestionado por `kgdb`

Y sitúa explícitamente un paso intermedio:

- `SL -> KG-Tree -> KG`

Además afirma:

> "The pipeline transforms knowledge from raw signals into world-facts."

Y asigna roles concretos a:

- `sldb`
- `truth_machine`
- `kgdb`
- `hum`
- `repopackage`

## Qué recuperamos de ahí

El patrón más valioso es este:

1. **surface/document layer**
2. **intermediate logical/operable structure**
3. **persistent graph layer**

En la relectura actual, esa IR no necesita ser una sola estructura canónica.
Puede aparecer como una cadena de representaciones cada vez menos azucaradas,
por ejemplo:

- texto natural
- átomos u otros documentos estructurados
- grafos locales
- grafo indexado agregado

## Relectura en la arquitectura nueva

La arquitectura actual puede leerse como una evolución/refinamiento de ese patrón:

- fuentes heterogéneas multi-source
- proyecciones estructurales (texto, AST, layout, DOM, etc.)
- anchor bundles
- samples verificables
- átomos pequeños con provenance
- composiciones
- grafos de provenance / concepto / estructura

## Conclusión

No conviene copiar literalmente el pipeline NL/SL/KG como estaba, pero sí conservar el patrón general:

> superficie estructurada -> IR operable -> persistencia relacional.

---

## 6. Universal Knowledge Loop como antecedente de materialización y retorno

Fuente:
- `/home/jp/proyectos/hum-ecosystem/docs/architecture/universal_knowledge_loop.md`

Este documento presenta un loop `S -> M -> G -> S`, con pasos de:

- ingest
- semantic mapping
- validation
- consolidation
- pruning
- deconversion / refined output

## Qué recuperamos de ahí

La gran lección aquí es que:

- el grafo no es solo un depósito final
- el sistema debe poder volver a materializar conocimiento en superficies humanas o derivadas

## Relectura en la arquitectura nueva

Esto se conecta con:

- compositions
- reports
- dashboards
- concept maps
- lineage views
- derived docs

## Conclusión

La nueva app debería mantener viva esta intuición:

> la persistencia en grafo debe servir también para producir nuevas superficies de lectura, inspección y acción.

---

## 7. `core/knowledge` como antecedente directo del órgano de conocimiento

Fuente:
- `/home/jp/proyectos/hum-ecosystem/core/knowledge/README.md`

Este archivo define `core/knowledge` como:

> `formal, queryable, and materializable knowledge substrate`

Además organiza el órgano en zonas:

- `selfdocs`
- `protocols`
- `rituals`
- `contracts`
- `procedures`
- `query`
- `materialization`

Y formula principios como:

1. `Separation of Hum/Knowledge`
2. `Determinization`
3. `Queryability`

Particularmente importante es la expectativa explícita de que:

> `Relationships between knowledge atoms must be explicitly defined in the edges field.`

## Qué recuperamos de ahí

Esto es probablemente el precursor más cercano de la arquitectura que ahora estamos buscando.

Recuperamos de aquí:

- separación entre actor/orquestación y conocimiento
- conocimiento como órgano estructurado
- importancia de queryabilidad por identificador estable
- idea de materialización
- necesidad de relaciones explícitas entre unidades de conocimiento

Si `core/knowledge` sigue siendo localizable y útil, conviene releerlo como
antecedente fuerte. Si no, basta con conservar la intuición arquitectónica sin
forzarle un rol más central del que hoy puede sostener documentalmente.

## Relectura en la arquitectura nueva

Hoy esa intuición puede fortalecerse así:

- no solo `edges` entre atoms
- también relaciones entre:
  - Source
  - Sample
  - Atom
  - Composition
  - Concept
  - TaxonomyNode
  - StructureNode

## Conclusión

`core/knowledge` no es todavía la arquitectura final que queremos, pero sí contiene un antecedente muy claro de:

> una KB estructurada, consultable, determinizable y con relaciones explícitas.

---

## 8. `hum-core` como ancestro del seed repo / sistema autopoietico

Fuente:
- `/home/jp/proyectos/hum-ecosystem/hum-core/README.md`

Este README presenta a Hum como:

> "An LLM-Driven Wiki Ecosystem"

Y como:

> "a self-contained Seed Repository and Development Operating System"

Además introduce el modelo de 4 zonas:

- `raw/`
- `wiki/`
- `desk/`
- `drawers/`

Y la idea de compilar conocimiento hacia un Knowledge Graph.

## Qué recuperamos de ahí

Más que detalles exactos de implementación, aquí importa rescatar:

- la intuición de un ecosistema de superficies distintas
- la diferencia entre crudo, verdad estructurada y trabajo operativo
- la idea de compilación de conocimiento

## Qué no conviene copiar literalmente

No conviene heredar sin revisión:

- la dependencia en `wiki/` como centro único
- la mezcla entre loop autopoietico, operación y KB como si fueran el mismo contenedor
- supuestos demasiado centrados en raw NL como fuente principal

## Conclusión

`hum-core` sirve más como antecedente histórico y organizacional que como blueprint técnico directo.

---

## 9. `docs/README.md` y la doctrina de documentación canónica

Fuente:
- `/home/jp/proyectos/hum-ecosystem/docs/README.md`

Este archivo presenta la documentación como una **documentation grid** y formula la regla:

> `one idea, one canonical home, many references`

## Qué recuperamos de ahí

Esto es metodológicamente muy valioso para el nuevo proyecto de KB:

- una idea no debe explicarse por completo en muchos lugares a la vez
- la duplicación difusa degrada claridad y mantenimiento
- las referencias cruzadas son preferibles a la repetición caótica

## Conclusión

Este principio debería mantenerse también en la nueva KB y su documentación arquitectónica.

---

## 10. `graphlang` y la línea de semántica formal

Fuente principal revisada:
- `/home/jp/proyectos/hum-ecosystem/docs/architecture/graphlang/README.md`

Además, la estructura visible del directorio sugiere una línea formal activa en:

- `CURRENT_STATE.md`
- `SYSTEM_SPEC.md`
- `database_query_formalization.md`
- `semantic_operations_spec.md`
- `tractarian_core_formalization.md`
- otros mapas y formalizaciones

## Qué recuperamos de ahí

Aunque no se haya leído todo en esta pasada, la estructura deja ver una preocupación consistente por:

- operaciones semánticas
- formalización computacional
- formalización de consultas
- mapeo entre formalización y código

## Relectura en la arquitectura nueva

Esto puede informar especialmente:

- el diseño del concept graph
- la formalización de relaciones
- la semántica de queries sobre provenance/concept/structure
- futuras capas de reasoning o validación semántica

## Conclusión

`graphlang` no debe copiarse a ciegas, pero sí debe considerarse una reserva importante de trabajo formal sobre semántica relacional.

---

## 11. Qué rescatar exactamente

## 11.1 A nivel de patrones

### Patrón A
**Surface -> IR -> Graph**

Fuentes:
- `docs/concepts/KG_TREES.md`
- `docs/architecture/nl_sl_kg_pipeline.md`

### Patrón B
**Knowledge is relational, not just atomic**

Fuentes:
- `docs/concepts/KNOWLEDGE_STRUCTURE_CHALLENGE.md`
- `core/knowledge/README.md`

### Patrón C
**Determinization before persistence**

Fuentes:
- `core/knowledge/README.md`
- `docs/architecture/nl_sl_kg_pipeline.md`

### Patrón D
**Materialization / deconversion back to surfaces**

Fuentes:
- `docs/architecture/universal_knowledge_loop.md`
- `core/knowledge/README.md`

### Patrón E
**Separation of orchestration from knowledge substrate**

Fuentes:
- `core/knowledge/README.md`
- `hum-core/README.md`

---

## 11.2 A nivel de conceptos

### Recuperar
- KG-Trees como antecedente de IR
- queryability
- explicit edges
- materialization
- knowledge organ
- semantic operations / formal graph work

### Reinterpretar
- NL -> SL -> KG hacia un modelo multi-source
- determinization hacia niveles de representación más que una única forma canónica
- wiki-centric organization hacia source/sample/atom/composition
- atom extraction hacia reconstrucción relacional más rica

### No copiar literalmente
- dependencia en raw text como entrada principal única
- mezcla excesiva entre loop autopoietico y KB central
- semánticas demasiado acopladas a un shell específico
- separaciones históricas de orquestación/sustrato que hoy ya no podamos explicar con precisión

---

## 12. Cómo conecta con la arquitectura actual

Este legado converge muy bien con los documentos ya definidos en `/home/jp/Upla/source/spec/`, en especial:

- `MULTI_SOURCE_ANCHORING.md`
- `GRAPH_ARCHITECTURE.md`
- `ATOM_CONCEPT_GRAPH.md`
- `SYNTHESIZED_ARCHITECTURE.md`

## Convergencias claras

### KG-Trees <-> IR entre estructura documental y grafo
Conecta con:
- samples como objetos verificables
- anchor bundles
- proyecciones estructurales

### Knowledge structure challenge <-> concept graph + system relations
Conecta con:
- crítica al abuso de tags
- necesidad de grafo conceptual explícito

### NL/SL/KG pipeline <-> document-first + graph spine
Conecta con:
- source subsystem
- structure subsystem
- anchoring subsystem
- graph subsystem

### core/knowledge <-> KB queryable y materializable
Conecta con:
- ids estables
- edges explícitos
- retrieval
- materialization

---

## 13. Recomendación práctica para el futuro inmediato

Al construir la primera iteración de la KB sobre los átomos actuales de Deskops, conviene preservar compatibilidad con este legado útil.

## Eso implica:

1. no tratar los átomos solo como notas planas
2. preparar desde ya relaciones explícitas
3. no cerrar el diseño a un único tipo de fuente
4. dejar espacio para IR intermedia entre documento y grafo
5. separar facets ligeras de semántica conceptual fuerte
6. mantener queryabilidad por ids estables
7. mantener posibilidad de materialización futura

---

## 14. Síntesis final

La parte más valiosa que queda de `/home/jp/proyectos/hum-ecosystem` puede resumirse así:

- el conocimiento debe estructurarse antes de persistirse
- el grafo no debe reemplazar la superficie documental, sino consolidarla relacionalmente
- la queryabilidad y la materialización son requisitos de primer nivel
- las relaciones entre unidades de conocimiento importan tanto como las unidades mismas
- hace falta una capa intermedia operable entre documento y grafo

En una frase:

> `hum-ecosystem` todavía conserva un antecedente fuerte de una KB document-first, determinizable, queryable y relacional, cuya intuición central debe rescatarse y reescribirse ahora en clave multi-source, provenance-first y concept-graph-aware.

---

## 15. Próximo paso sugerido

El siguiente trabajo lógico es definir una estrategia de construcción incremental usando el `deskops` actual, de manera que:

- los átomos presentes sirvan como punto de arranque
- lo que construyamos ahora no quede descartado después
- la primera KB ya nazca compatible con:
  - provenance futura
  - concept graph futuro
  - structural graph futuro
  - multi-source anchoring futuro
