# KNOWLEDGE CORE — Semantic Anchoring over sldb+kgdb

## Estado
Núcleo. Todo lo demás del sistema knowledge se ordena después de esto.

## Tesis

`knowledge` es un evaluador de s-expressions donde **cada símbolo está anclado a un
motivo semántico** resoluble contra la infraestructura (sldb + kgdb + estado
runtime). El comando no es un string que se parsea a flags: es una expresión
cuyo significado se resuelve contra el mundo antes de ejecutarse.

Inspiración directa: SHRDLU (Winograd). Cada símbolo de la frase se resuelve
contra el mundo; la ambigüedad es un estado del diálogo, no un error.

## Las tres capas (modelo SMG aplicado a comandos)

```
Surface   "user juanito check preferences"     ← azúcar sintáctico, reversible
   │ desugar (determinista)
Meaning   (check (rel preferences (doc user "juanito")))   ← s-expression
   │ eval (cada símbolo → su anchor)
Graph     nodos/edges alcanzados en sldb+kgdb  ← referentes reales
```

- Surface→Meaning es determinista (no NLP libre; gramática posicional).
- Meaning→Graph resuelve cada símbolo por su anchor.
- Un símbolo sin anchor es un error semántico explícito: "no sé qué motivo
  tiene X", nunca un fallo silencioso.

## El anchor: símbolo → motivo semántico

Un anchor liga un símbolo de la gramática a:

1. **kind** — qué clase de referente es:
   - `model` — un StructuredNLDoc registrado (UserDoc, TaskDoc…)
   - `doc` — un documento concreto tracked
   - `relation` — un tipo de edge kgdb (declares_preference, follows…)
   - `operation` — un verbo del runtime (check, next, assert, ingest, create, return)
   - `projection` — una vista/reducción del payload (summary, full…)
2. **ref** — el referente concreto en la infra.
3. **motive** — el motivo semántico en lenguaje natural: qué significa este
   símbolo para un humano. Es lo que hace la gramática legible y auditable.

## Los anchors son documentos SLDB

La tabla de anchors NO es código: es un conjunto de docs tracked (modelo
`AnchorDoc`). Consecuencias:

- Cada app declara su propia gramática registrando sus anchors.
- knowledge se adapta a cada caso de uso sin tocar código.
- La gramática es consultable, versionada, con provenance — es conocimiento.
- La app es autoconsciente también de su lenguaje de comandos: `--help` y la
  gramática viva derivan de los mismos docs.

## Evaluación (estilo SHRDLU)

Para `(check (rel preferences (doc user "juanito")))`:

1. `user` → anchor kind=model → resuelve el modelo UserDoc.
2. `"juanito"` → resolución de sustantivo contra el store:
   - único → sigue
   - ambiguo → retorna pregunta + candidatos ("¿juanito-perez o juanito-soto?")
     y queda en estado de clarificación; la siguiente entrada resuelve.
   - inexistente → error con el motive del símbolo para explicar qué se buscaba.
3. `preferences` → anchor kind=relation → traversal kgdb desde el nodo user.
4. `check` → anchor kind=operation, lectura → proyecta el payload alcanzado.

La resolución de sustantivos es con estado (awaiting_clarification): la
ambigüedad produce diálogo, no excepción.

## Operaciones canónicas (del s-expression runtime ya especificado)

- `(check …)` — evalúa/lee sin mutar.
- `(next …)` — siguiente elemento por estado (orden definido por el modelo).
- `(assert …)` — añade un hecho como verdadero.
- `(create …)` — define entidades (symbol/relation/modelo/doc).
- `(ingest …)` — registra una proposición/documento.
- `(return …)` — consulta hechos almacenados.

Toda escritura (`assert/create/ingest`) va vía sldb (docs/fields) y registra
provenance del comando que la produjo: la Memory de SHRDLU, pero auditable.

## Arquitectura del evaluador

```
surface text ──desugar──► s-expression            (Meaning)
                               │ eval
                     anchor table (docs SLDB)      ← gramática declarable por app
                               │
               ┌───────────────┼────────────────┐
            op layer       noun resolution   relation traversal
         (check/next/      (sldb docs +      (kgdb edges +
          assert/ingest)    disambiguación)   roles)
```

- Parser s-expr: mínimo (~40 líneas).
- Evaluador: resuelve símbolo por anchor; despacha por kind.
- Capa infra (ya entendida): knowledge declara modelos sldb y los proyecta
  (registro en store + materialización kgdb). El evaluador opera sobre esa
  proyección.

## Ejemplos canónicos

```
next task --summary
  ≡ (next (docs task) :project summary)

user juanito check preferences
  ≡ (check (rel preferences (doc user "juanito")))
```

## Qué NO es esto

- No es NLP libre: la surface grammar es posicional y determinista.
- No es un DSL cerrado: la gramática crece declarando anchors, no parcheando
  el parser.
- No es un workflow engine: check/next/assert son operaciones de conocimiento,
  no tasks/boards (eso queda en deskops).

## Orden de dependencia del sistema

1. Este núcleo (anchors + evaluador s-expr).
2. Capa infra (declarar/proyectar modelos) — al servicio del núcleo.
3. Superficies documentales (CliCommandDoc/SurfaceDoc) — derivadas de anchors.
4. Corpus de atoms y dominios — contenido que el núcleo hace consultable.
