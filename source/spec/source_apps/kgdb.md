# kgdb

## Qué es
Substrato de persistencia y consulta de grafos para el ecosistema HUM.
Ingiere payloads/versioned exports y responde queries deterministas sobre nodos y edges.

## Por qué importa para la nueva app
Si la nueva app necesita relaciones explícitas entre fuentes, samples, atoms, composiciones, tareas y artefactos, KGDB es una referencia clave para la capa grafo.

## Qué deberíamos recuperar

### 1. Separación documento vs grafo
- SLDB/documentos producen semántica
- KGDB persiste y recorre relaciones
- no reinterpretar arbitrariamente la semántica aguas abajo

### 2. Contratos de ingestión
- snapshots validados
- nodos/edges tipados
- validación robusta de payloads

### 3. Query determinista
- get nodes
- traverse edges
- query by semantics and scope
- trace surfaces entre artefactos

### 4. Trazabilidad relacional
Especialmente útil para:
- qué atoms derivan de qué samples
- qué samples vienen de qué fuentes
- qué documentos usan qué atoms
- qué composiciones dependen de qué piezas

### 5. Filosofía importante
El grafo debe almacenar y recorrer hechos, no improvisar interpretación documental.

## Qué no deberíamos heredar sin revisión
- complejidad de contratos si la nueva app requiere un modelo más simple al inicio
- fronteras innecesarias si documento y grafo viven más integrados

## Preguntas de extracción
- ¿Cuál es el contrato mínimo de snapshot útil?
- ¿Qué tipos de nodo/edge se necesitan para una KB source/sample/atom?
- ¿Cómo diseñar consultas de trazabilidad verdaderamente útiles?