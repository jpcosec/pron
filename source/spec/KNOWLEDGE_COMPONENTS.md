# KNOWLEDGE COMPONENTS — Descomposición del sistema

## Estado
Capa 3 (después de core y usability). Define componentes, contratos y
dependencias. Sin ambigüedad aquí, el código es mecánico.

## Mapa

```
┌─────────────────────────── knowledge CLI ────────────────────────────┐
│  surface_parser → desugarer → session → evaluator → renderer         │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
   anchor_registry        noun_resolver          op_dispatcher
   (AnchorDoc en sldb)    (sldb docs)            (check/next/assert/…)
        │                      │                      │
        └──────────┬───────────┴──────────┬───────────┘
              sldb bridge            kgdb bridge
              (store, docs,          (snapshot, traversal,
               fields, models)        edges, trace)
```

## Componentes

### 1. surface_parser
- **In**: argv / línea de texto.
- **Out**: lista de tokens clasificados posicionalmente.
- **Contrato**: no interpreta; solo tokeniza y detecta orden noun-first/verb-first.
- **Depende de**: nada.

### 2. desugarer
- **In**: tokens clasificados + anchor kinds (solo para distinguir noun/verb).
- **Out**: s-expression (Meaning). Determinista y reversible.
- **Contrato**: mismo input ⇒ misma s-expr; toda s-expr producida es
  serializable de vuelta a un surface canónico.
- **Depende de**: anchor_registry (lookup de kind, no de ref).

### 3. anchor_registry
- **In**: símbolo.
- **Out**: AnchorDoc {kind, ref, motive} o miss explícito.
- **Contrato**: lee AnchorDocs tracked del store local + federados; cache por
  invocación; nunca inventa anchors.
- **Modelo**: `AnchorDoc` (StructuredNLDoc, vive en sldb junto a
  CliCommandDoc/SurfaceDoc). Campos: symbol, kind, ref, motive, tags, provenance.
- **Depende de**: sldb bridge.

### 4. noun_resolver
- **In**: (modelo, selector) — p.ej. (UserDoc, "juanito").
- **Out**: exactamente uno de:
  - `Resolved(doc)`
  - `Ambiguous(candidates, question)`
  - `Missing(motive, nearest)`
- **Contrato**: los tres resultados son valores, no excepciones. Match por id
  exacto → título exacto → prefijo; fuzzy solo para poblar `nearest`.
- **Depende de**: sldb bridge.

### 5. session
- **In/Out**: expresión pendiente + candidatos.
- **Contrato**: persiste en `.knowledge-session.json` (local al cwd);
  la clarificación matchea contra candidatos pendientes antes de tratar la
  entrada como comando nuevo; TTL corto (una sesión de trabajo).
- **Depende de**: nada (archivo local).

### 6. op_dispatcher
- **In**: s-expression con todos los símbolos resueltos.
- **Out**: OperationResult {status, payload, refs, provenance}.
- **Contrato**: despacha por anchor kind=operation. Operaciones de lectura
  (check, next, return) no mutan; escrituras (assert, create, ingest) van vía
  sldb y registran la s-expr evaluada como provenance.
- **Depende de**: sldb bridge, kgdb bridge.

### 7. sldb bridge
- **Contrato**: única puerta a sldb. Usa la capa de librería real
  (`sldb.store.query.load_runtime_documents`, `resolve_model_ref`,
  docs/fields ops) — nunca reimplementa búsqueda ni shellea al CLI de sldb.
- **Incluye**: resolución multi-store (local + federados, cada store con su
  propio pythonpath — el fix ya aplicado en `sldb.store.query`).

### 8. kgdb bridge
- **Contrato**: única puerta al grafo. Carga snapshot
  (`.sldb/runtime/knowledge_graph.kg.json`), valida contra
  `kgdb.contracts.io.GraphSnapshot`, expone: neighbors(node), edges(node,
  role), trace(node), nodes_by_relation(rel, target).
- **Regla**: snapshot desactualizado ⇒ warning con instrucción de `project`,
  nunca resultado silenciosamente stale.

### 9. projector (infra layer)
- **In**: modelos declarados + docs tracked.
- **Out**: registro en store + snapshot kgdb refrescado.
- **Contrato**: `knowledge model add <ref>` registra; `knowledge project`
  materializa grafo. Es la capa que da mundo al evaluador.

### 10. renderer
- **In**: OperationResult | Ambiguous | Missing | SemanticError.
- **Out**: JSON (default) o texto. Siempre incluye refs.

## Reglas transversales

- Cada componente es una función/clase con un solo motivo (los componentes se
  documentan a sí mismos como atoms `kind:software` cuando se implementen).
- Errores entre componentes son valores tipados (Resolved/Ambiguous/Missing/
  SemanticError), no excepciones de control de flujo.
- Ningún componente fuera de los bridges importa sldb/kgdb directamente.
- Los bridges no conocen la gramática; el evaluador no conoce el storage.

## Decisiones cerradas (ex-ambigüedades)

### D1. Serialización de la s-expression

Formato canónico (subset de EDN/lisp, parseable con el kernel propio):

```
expr      := (op arg*)
op        := símbolo anclado kind=operation
arg       := expr | ref | literal | option
ref       := (docs <model-symbol>)               ; todos los docs del modelo
           | (doc <model-symbol> <selector>)     ; un doc por selector
           | (rel <relation-symbol> <expr>)      ; traversal desde expr
literal   := "string" | número | :keyword
option    := :project <projection-symbol>        ; siempre par keyword+símbolo
selector  := "string" (siempre entre comillas dobles; comillas internas se
             escapan con \"; nunca se interpola sin quoting)
```

Reglas:
- Los símbolos van sin comillas; los selectores SIEMPRE con comillas dobles.
- Las options van al final de la expresión, como pares `:keyword símbolo`.
- Serialización de vuelta (Meaning→Surface) usa el orden noun-first canónico.
- Toda s-expr válida roundtripea: parse(serialize(e)) == e.

### D2. Sesión: ubicación, TTL e invalidación

- Archivo: `.knowledge/session.json` bajo el cwd (dir `.knowledge/` es runtime
  local, gitignored).
- Contenido: {pending_sexpr, candidates, created_at, cwd, store_hash}.
- TTL: 15 minutos desde created_at; expirado ⇒ se ignora y se borra.
- Invalidación adicional: si `store_hash` (hash_a del store) cambió, la sesión
  se descarta — los candidatos podrían ya no existir.
- Solo existe una expresión pendiente a la vez; un comando nuevo la reemplaza.

### D3. Contrato de AnchorDoc.ref por kind

`ref` es un string con esquema por kind (validado por el modelo):

| kind       | formato de ref                  | ejemplo                          |
|------------|--------------------------------|----------------------------------|
| model      | `model:<ModelName>`            | `model:UserDoc`                  |
| doc        | `doc:<doc-name>`               | `doc:atom-searchvector`          |
| relation   | `edge:<relation_type>`         | `edge:declares_preference`       |
| operation  | `op:<función>`                 | `op:check`                       |
| projection | `fields:<f1,f2,...>` \| `view:<name>` | `fields:id,title` / `view:summary` |

- Un solo string tipado (no dict): legible en frontmatter, validable con regex
  por kind, y suficiente — la resolución compleja vive en el evaluador, no en
  el anchor.
- `relation` puede sufijar dirección: `edge:declares_preference:in` (default
  `out`).

## Orden de implementación (cuando toque)

1. AnchorDoc (modelo, en sldb) + anchor_registry.
2. s-expr parser + desugarer.
3. noun_resolver + session.
4. bridges (sldb primero, kgdb después).
5. op_dispatcher: check → next → return → assert/create/ingest.
6. renderer + surface CLI.
