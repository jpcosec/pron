# SPEC — Knowledge-Native Agent Runtime

## 1. Objetivo

Construir una arquitectura donde **agentes, tools, runtimes, APIs, bases de datos y proyectores sean componentes componibles bajo un contrato común**.

La fuente de verdad no es el workflow ni el prompt: es un **grafo de conocimiento tipado**, persistido principalmente como Markdown estructurado y proyectable hacia modelos Pydantic/otros tipos.

El sistema debe permitir construir aplicaciones complejas como composición de nodos pequeños, especializados, testeables y semánticamente descritos.

---

## 2. Principio central

```text
Knowledge Graph
     │
     ▼
 Agent/Node Spec
     │
     ▼
Executable Nodes
     │
     ├── LLM
     ├── Tool
     ├── SQL
     ├── API
     ├── Projector
     ├── Workflow
     └── External Runtime
```

El **grafo define qué existe y qué significa**.

El runtime solamente materializa y ejecuta esa definición.

Por tanto:

> **El grafo es semántico. El workflow es derivado.**

Esto lo diferencia de sistemas como n8n, donde el grafo representa principalmente flujo de ejecución.

---

# 3. Unidad fundamental: `ExecutableNode`

Todo elemento ejecutable implementa el mismo contrato abstracto.

```clojure
(defprotocol ExecutableNode

  ;; identidad semántica
  (self-doc [node])

  ;; contrato
  (input-ports [node])
  (output-ports [node])

  ;; conocimiento al que tiene acceso
  (knowledge-projection [node])

  ;; capacidades declaradas
  (capabilities [node])

  ;; comportamiento temporal
  (state-machine [node])

  ;; backend que materializa la ejecución
  (runtime [node])

  ;; condiciones que prueban que terminó correctamente
  (completion-tests [node])

  ;; ejecución
  (execute [node context input]))
```

Conceptualmente:

```text
ExecutableNode
├── Self
├── Inputs
├── Outputs
├── Knowledge
├── Capabilities
├── State Machine
├── Runtime
├── Completion Tests
└── Implementation
```

La clase base debe mantenerse deliberadamente pequeña.

---

# 4. `SelfDoc`

Cada nodo posee un documento que explica su identidad operacional.

No es una personalidad.

Es una declaración formal de responsabilidad.

```yaml
id: source.scraper.wikipedia

name: Wikipedia Scraper

purpose:
  Extract structured information from Wikipedia pages.

responsibilities:
  - fetch_source
  - normalize_content
  - emit_source_document

does_not:
  - interpret findings
  - modify knowledge atoms
  - publish output

knowledge_scope:
  read:
    - source_configs
  write:
    - raw_sources
```

Esto permite que otro agente u orquestador pueda descubrir qué nodo utilizar sin inspeccionar su código.

---

# 5. Puertos tipados

Los nodos no deberían comunicarse principalmente mediante texto libre.

Cada nodo expone:

```text
InputPort<T>
OutputPort<T>
```

Ejemplo:

```clojure
{:inputs
 [{:name :source
   :type SourceReference}]

 :outputs
 [{:name :document
   :type SourceDocument}]}
```

El orquestador puede entonces comprobar:

```text
Output<A> ──compatible──> Input<A>
```

antes de ejecutar el pipeline.

Esto convierte la arquitectura en una especie de **Lego semántico**.

---

# 6. Knowledge Projection

Un agente no recibe necesariamente toda la base.

Recibe una **proyección del grafo** apropiada para su tarea.

```text
Knowledge Graph
      │
      ├── Agent A Projection
      ├── Agent B Projection
      ├── SQL Projection
      └── UI Projection
```

Ejemplo:

```clojure
{:knowledge
 {:roots [:customers :orders]
  :relations [:belongs-to :references]
  :depth 2
  :permissions [:read]}}
```

El CLI actual de la base de conocimiento puede inicialmente implementar esta capa.

Más adelante debería existir una API estable:

```text
knowledge.query()
knowledge.resolve()
knowledge.project()
knowledge.write()
knowledge.validate()
```

El agente no debería estar haciendo parsing arbitrario de Markdown.

---

# 7. Capabilities

Una capability describe **qué puede garantizar el nodo**.

```yaml
capabilities:

  - id: extract.website
    input: WebSource
    output: SourceDocument

  - id: normalize.article
    input: RawArticle
    output: NormalizedArticle
```

Capabilities y runtime son conceptos distintos.

Por ejemplo:

```text
Capability:
    summarize_document

Runtime:
    DeepSeek
```

o:

```text
Capability:
    execute_query

Runtime:
    PostgreSQL
```

---

# 8. Runtime

El runtime es el backend de ejecución.

```text
ExecutableNode
        │
        ▼
 Runtime Adapter
```

Posibles runtimes:

```text
LLMRuntime
SQLRuntime
HTTPRuntime
ShellRuntime
ClojureRuntime
JSRuntime
WASMRuntime
AstroRuntime
DeepSeekHarnessRuntime
HumanRuntime
```

Interfaz mínima:

```clojure
(defprotocol Runtime
  (prepare [runtime node context])
  (invoke [runtime request])
  (observe [runtime execution])
  (cancel [runtime execution]))
```

Esto permite cambiar DeepSeek Harness por otro sistema sin alterar el modelo semántico.

---

# 9. State Machine

Cada nodo puede tener una máquina de estados explícita.

Ejemplo:

```text
IDLE
 │
 ▼
PREPARING
 │
 ▼
RUNNING
 │
 ├──> RETRYING
 │
 ▼
VALIDATING
 │
 ├──> FAILED
 │
 ▼
COMPLETED
```

Pero el nodo puede extenderla.

Por ejemplo, un scraper:

```text
RESOLVE_SOURCE
      ↓
FETCH
      ↓
PARSE
      ↓
NORMALIZE
      ↓
VALIDATE
      ↓
STORE
```

La máquina de estados también debería ser parte del grafo/spec.

---

# 10. Completion Tests

Cada nodo define qué significa **haber terminado correctamente**.

Esto es distinto de un unit test tradicional.

Ejemplo:

```yaml
completion_tests:

  - name: source_exists
    assert:
      output.document != null

  - name: valid_schema
    schema:
      output.document: SourceDocument

  - name: stored
    assert:
      knowledge.exists(output.document.id)

  - name: no_missing_required_fields
    validator:
      SourceDocument.required_fields
```

Hay por tanto al menos tres niveles:

```text
Unit tests
    ↓
Contract tests
    ↓
Completion tests
```

### Unit test

¿Funciona la implementación?

### Contract test

¿Respeta inputs/outputs?

### Completion test

¿Cumplió realmente el objetivo prometido?

---

# 11. Tipos concretos de nodo

No necesariamente deben ser clases diferentes.

Preferiblemente son especializaciones configuradas de `ExecutableNode`.

```text
ExecutableNode
│
├── AgentNode
├── ToolNode
├── ProjectorNode
├── AdapterNode
├── WorkflowNode
└── CompositeNode
```

Pero conceptualmente podrían ser simplemente:

```clojure
{:kind :node
 :runtime :llm
 ...}
```

vs.

```clojure
{:kind :node
 :runtime :postgres
 ...}
```

Esto evita una jerarquía de clases innecesaria.

---

# 12. LLM como nodo

```text
Input
  │
  ▼
Knowledge Projection
  │
  ▼
LLM Runtime
  │
  ▼
Typed Output
```

Ejemplo:

```yaml
id: research.interpreter

runtime:
  type: llm
  provider: deepseek

inputs:
  - SourceDocument

outputs:
  - KnowledgeAtom[]

knowledge:
  read:
    - ontology
    - source_notes

capabilities:
  - extract_claims
  - relate_concepts
```

El prompt debería ser una **proyección derivada del SelfDoc + conocimiento + contrato**, no la fuente primaria de comportamiento.

---

# 13. SQL como nodo

```yaml
id: customer_database

runtime:
  type: postgres

inputs:
  - CustomerQuery

outputs:
  - CustomerRecordSet

knowledge:
  read:
    - database_schema

capabilities:
  - query_customer
  - aggregate_orders
```

El orquestador no necesita saber SQL.

Solo:

```text
CustomerQuery
      ↓
customer_database
      ↓
CustomerRecordSet
```

---

# 14. API como nodo

```yaml
id: weather_api

runtime:
  type: http

inputs:
  - WeatherRequest

outputs:
  - WeatherObservation

capabilities:
  - current_weather

auth:
  strategy: secret_ref
  secret: WEATHER_API_KEY
```

El detalle HTTP queda encapsulado.

---

# 15. Proyectores

Los proyectores convierten conocimiento en representaciones.

```text
Knowledge
   │
   ├──> Markdown
   ├──> HTML
   ├──> JSON
   ├──> Diagram
   ├──> Audio
   └──> Wiki
```

Ejemplo:

```yaml
id: projection.article

runtime:
  type: clojurescript

inputs:
  - ArticleKnowledge

outputs:
  - ArticleViewModel
```

Después:

```text
ArticleViewModel
       ↓
AstroRenderer
       ↓
HTML
```

---

# 16. Página compleja

Una página grande no debería ser un único nodo.

```text
Knowledge Graph
      │
      ├── HeaderProjector
      ├── ArticleProjector
      ├── RelationGraphProjector
      ├── SourcesProjector
      └── NavigationProjector
               │
               ▼
          PageComposer
               │
               ▼
          AstroRenderer
               │
               ▼
             HTML
```

Esto permite testear cada pieza separadamente.

---

# 17. Composite Nodes

Una aplicación completa puede comportarse como un nodo.

Internamente:

```text
CompositeNode
│
├── Node A
├── Node B
├── Node C
└── Node D
```

Externamente:

```text
Input<X>
   ↓
CompositeNode
   ↓
Output<Y>
```

Esto permite composición recursiva.

Un workflow entero puede convertirse en una pieza de otro workflow.

---

# 18. Orquestador

El orquestador debería ser pequeño.

Responsabilidades:

```text
1. recibir objetivo
2. resolver capacidades necesarias
3. encontrar nodos compatibles
4. verificar tipos
5. construir execution graph
6. ejecutar
7. observar estados
8. verificar completion tests
9. persistir resultados
```

No debería contener conocimiento específico de aplicaciones.

Pseudocódigo:

```clojure
(defn satisfy [goal context]

  (let [capability (resolve-capability goal)
        node       (find-node capability)
        input      (resolve-inputs node context)]

    (assert-compatible input node)

    (let [result (execute node context input)]

      (run-completion-tests node result)

      result)))
```

---

# 19. Flujo de conocimiento

El patrón fundamental queda:

```text
       ┌────────────────────┐
       │   Knowledge Graph  │
       └─────────┬──────────┘
                 │ project
                 ▼
       ┌────────────────────┐
       │   Executable Node  │
       └─────────┬──────────┘
                 │ execute
                 ▼
       ┌────────────────────┐
       │      Runtime       │
       └─────────┬──────────┘
                 │ output
                 ▼
       ┌────────────────────┐
       │   Typed Artifact   │
       └─────────┬──────────┘
                 │ validate
                 ▼
       ┌────────────────────┐
       │   Knowledge Graph  │
       └────────────────────┘
```

El sistema completo es un loop de transformación del conocimiento.

---

# 20. Integración con DeepSeek Harness

DeepSeek Harness no debería convertirse en la arquitectura principal.

Debe ser un runtime:

```text
Knowledge System
      │
      ▼
AgentSpec
      │
      ▼
DeepSeekHarnessAdapter
      │
      ▼
DeepSeek Harness
```

El adapter traduce:

```text
SelfDoc             → system/context
KnowledgeProjection → context
Capabilities        → tools
StateMachine        → execution rules
CompletionTests     → verification
```

Así puedes posteriormente tener:

```text
DeepSeekHarnessRuntime
ClaudeRuntime
LocalLLMRuntime
DeterministicRuntime
```

sin cambiar los agentes.

---

# 21. Lenguaje

Recomendación inicial:

```text
Semantic model / orchestration:
    Clojure

Browser / UI projections:
    ClojureScript

Existing knowledge models:
    Python / Pydantic

Web rendering:
    Astro

LLM runtime:
    adapter

External systems:
    adapters
```

No intentaría migrar inmediatamente Pydantic.

Primero:

```text
Markdown
   ↕
Pydantic knowledge layer
   ↕
AgentSpec
   ↕
Clojure runtime
```

Después puedes decidir si el modelo semántico termina moviéndose completamente a EDN/Clojure.

---

# 22. Representación declarativa

Idealmente un nodo debería poder ser casi enteramente data:

```clojure
{:id :research/source-scraper

 :self
 {:purpose "Acquire source documents"}

 :inputs
 [{:name :source
   :type :source/reference}]

 :outputs
 [{:name :document
   :type :source/document}]

 :knowledge
 {:read [:source-config]
  :write [:source-document]}

 :capabilities
 [:source/fetch
  :source/normalize]

 :runtime
 {:type :http-scraper}

 :state-machine
 [:idle
  :fetching
  :parsing
  :validating
  :completed]

 :completion-tests
 [:document-valid
  :document-persisted]}
```

El código implementa principalmente runtimes y primitives.

**Los agentes deberían ser mayoritariamente datos.**

---

# 23. Invariantes

La primera versión debería imponer estas reglas:

1. Todo nodo tiene `SelfDoc`.
2. Todo input/output tiene tipo.
3. Todo nodo declara explícitamente qué conocimiento lee/escribe.
4. Ningún runtime define semántica del agente.
5. Todo nodo ejecutable posee al menos un completion test.
6. Un nodo no puede escribir fuera de su scope.
7. La compatibilidad de puertos se valida antes de ejecutar.
8. Todo resultado persistido debe poder rastrearse hacia la ejecución que lo produjo.
9. Workflows y aplicaciones pueden encapsularse nuevamente como nodos.
10. El grafo de conocimiento sigue siendo la fuente de verdad.

---

## 24. La arquitectura reducida

Al final, el sistema tiene cinco conceptos fundamentales:

```text
KNOWLEDGE
    conocimiento semántico persistido

NODE
    componente que promete una transformación

PORT
    contrato tipado entre componentes

RUNTIME
    mecanismo que materializa la transformación

PROJECTION
    representación particular del conocimiento
```

Y alrededor de ellos:

```text
State Machines
Capabilities
Completion Tests
Permissions
Provenance
Orchestration
```

Eso permite que un scraper, un LLM, PostgreSQL, una API, un generador Astro o incluso otro sistema multiagente **sean piezas del mismo sistema sin fingir que internamente hacen lo mismo**.

