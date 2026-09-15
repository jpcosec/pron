# 05 · Léxico y proyección

## De dónde salen las palabras

El léxico no es una tabla de pron. Se deriva del mundo, en este orden:

| palabra | fuente | ejemplo |
|---|---|---|
| nombre común | nombre del modelo y su docstring | `CliCommandDoc` → "command" |
| hiperónimo | `base_models` y `family` | `PrimitiveDoc` → "primitive" |
| atributo | nombre y `description` de cada campo | `synopsis` → "synopsis" |
| categoría | tags y el DAG semántico | `type.knowledge.anchor` → "anchor" |
| verbo transitivo | `RelationTypeDoc.name` y su descripción | `implements` → "implements" |
| verbo de acción | la tabla del kernel (04) | "change", "create", "forget" |
| alias | `AnchorDoc` | "repl" → `st.{CliCommandDoc}.cmd-pron-repl` |

Las descripciones obligatorias de los campos son el motivo de cada palabra: lo que se le muestra al humano cuando pregunta "what is synopsis?" y lo que se embebe para el calce aproximado.

Los **valores** también son léxico cuando el campo los acota: los miembros de un `Literal` o `Enum`, y los valores ya usados de campos como `system` y de `tags`. Por eso "de pron" en "los átomos de pron" es un predicado `system = "pron"` y no un nombre propio (02). Los valores libres de texto no entran al léxico.

## De dónde se lee el léxico

Las fuentes de arriba son documentos y esquemas de sldb, y el ingest de kgdb las materializa como aristas: `has_field`, `extends`, `applies_to_source`, `applies_to_target`, `names` (10 §2.3). Con el grafo fresco, el léxico de una clase es una sola consulta, sus aristas entrantes y las de sus ancestros; sin grafo o con grafo viejo, pron lo deriva desde sldb con las consultas de la tabla, y la traza lo dice. Nunca se registra un verbo por sustantivo: la pregunta "¿qué puedo hacer con X?" se contesta recorriendo, no leyendo una lista.

## Anchors: la forma en lengua natural

Toda palabra del léxico nombra una **forma** (13): un modelo es `(model M)`, un campo `(field M f)`, un valor `(value M f v)`, un tipo de relación `(relation R)`, un verbo del kernel `(action verbo)`. Eso es lo que muestra `pron lexicon` en la columna `ref`, y lo que la superficie arma cuando reconoce la palabra. Un `AnchorDoc` es un alias: una palabra más, con la forma que nombra escrita por quien declara el mundo. Su contrato:

| campo | contenido |
|---|---|
| `symbol` | la palabra canónica |
| `forms` | todas las formas que la superficie reconoce, listadas: `reservation, reservations`; `confirma, confirmá, confirm it` (11 §1) |
| `ref` | la forma que nombra, en uno de los casos de abajo |
| `motive` | lo que se muestra al preguntar qué significa |

Los casos de `ref`:

| forma | ejemplo | qué es |
|---|---|---|
| `(model M)` | `client → (model Client)` | un sustantivo |
| `(field M f)` | `named → (field Client name)` | un atributo, con sus preposiciones en `forms` |
| `(where M "<predicado>")` | `large → (where Table "capacity >= 6")` | un adjetivo; el predicado puede usar `{campo}` del sujeto y las ranuras `N`, `X`, `Z` de sus `forms` |
| `(relation R)` | `asignale → (relation assigned_to)` | un verbo transitivo; `forms` puede marcar la lectura inversa (`has ← (relation booked_by)`) |
| `(change (it "it" M) f "v")` | `confirm → (change (it "it" Reservation) status "confirmed")` | un verbo de acción con campo y valor fijos; `(it …)` es el hueco que llena el sustantivo de la oración |
| `(doc "M:nombre")` | `el proyector → (doc "SurfaceDoc:surface-pron-infra-projector")` | un nombre propio fijo para un objeto |
| `(move (create M) (assert R (created) SUST) …)` | `book`, abajo | una oración compuesta |

**Oraciones compuestas.** Un alias compuesto es un `(move …)` con huecos que la oración llena. "book her a table for 6 on Friday at 9pm":

```yaml
symbol: book
forms: [book her, book him, book them, make a reservation for]
ref: (move (create Reservation) (assert booked_by (created) (it "her" Client)) (assert assigned_to (created) (a Table)))
motive: create a reservation for someone and put it at a table
```

Los huecos son tres y fijos: `(created)`, el documento que dejó el `(create …)` del mismo movimiento, que recibe los literales de la oración asignados a sus campos por sus alias; `(it "…" M)`, el referente de la oración con esa clase ("her"); `(a M)`, la frase nominal de la oración con esa clase ("a table on the terrace for 6"). Un paso puede ser `create`, `assert` o `change`. Al decir la oración, el alias se escribe como `(say book (slot "$referent:Client" SUST) (slot "$object:Table" SUST) (campo valor) …)` y se evalúa: cada paso pasa por las mismas verificaciones y permisos que si fuera una forma sola; si un hueco no se puede resolver, el movimiento entero es ambiguo o missing antes de ejecutar nada; los pasos se ejecutan en orden con un solo refresh. No hay condicionales ni repeticiones: lo que no cabe en una secuencia fija de tres tipos de paso no es un alias, es un patrón general de pron o no existe.

Un alias sí aporta significado a una expresión: "large" significa algo porque alguien decidió que es capacidad mayor o igual a seis. Lo que no hace es agregar capacidades: todo `ref` es una forma que el mundo ya puede evaluar sin el alias (13). Por eso no es la fuente del léxico, sino su forma en lengua natural, y por eso se puede listar, revisar y borrar sin que nada deje de ser posible.

Un alias puede nombrar también un **verbo de acción con campo y valor fijos**: `confirm → (change (it "it" Reservation) status "confirmed")`. Es la única forma en que un mundo agrega verbos sin código, y sigue siendo un alias: el verbo real es `change` y pasa por las mismas verificaciones, incluida la transición (03).

Son la única fuente de la forma hablada. El identificador `CliCommandDoc` no se convierte en "command" por ninguna regla: alguien escribe el alias `command → (model CliCommandDoc)`, con su plural en `forms`. Un término sin alias se nombra y se reconoce por su identificador tal cual y, además, partido en palabras (`cli command doc`, `party size`): esa forma la deriva el léxico del identificador, no es un `AnchorDoc`, y sirve de calce hasta que un alias diga algo mejor.

Un alias entra a una sesión solo si todo lo que su forma nombra está en la proyección: los modelos, las relaciones y los verbos del kernel de cada paso. Un alias hacia un modelo fuera de `models` no existe para esa sesión, aunque la lista `aliases` lo nombre.

**La sintaxis anterior.** Los `ref` escritos como texto (`model:M`, `field:M.f`, `predicate:M:<where>`, `relation:R`, `action:<verbo> M.f=v`, `doc:M:nombre`, y `compose` con una lista `steps`) se siguen leyendo, y el léxico los convierte en la forma equivalente; un lint rechaza un `ref` que no es ninguna de las dos.

## Proyección

La proyección (01) recorta el léxico: solo entran las palabras cuyas fuentes están en la proyección de la sesión. Verificar que una palabra "está en la proyección" es buscarla en ese léxico recortado, no en el mundo entero.

## Calce aproximado

Cuando una palabra no calza exactamente con el léxico, la superficie busca cercanos por similitud entre la palabra y los motivos del léxico: descripciones de campos, docstrings de modelos, descripciones de `RelationTypeDoc`, motivos de anchors. Los embeddings se calculan offline sobre el léxico, no sobre los documentos, y se recalculan cuando cambia `hash_mundo` (07).

El resultado del calce aproximado sobre el mundo nunca se ejecuta solo. Se ofrece: "I don't have *bridge*, did you mean *bridges*?". La única excepción es contestar una pendiente de elección (06): ahí el conjunto de candidatos es cerrado y ya se mostró, y un calce único contra esos candidatos sí rellena el hueco.

Un valor libre de texto que no calza también se ofrece, nunca se vuelve léxico. Cuando un predicado de igualdad sobre un campo `string` no enumerado no encuentra nada, o la palabra del turno no tiene cercano de vocabulario, la superficie rankea contra los valores distintos que ese campo ya tiene en los documentos del modelo (familia incluida, stores de la proyección) y ofrece la oración corregida — "the fact about *evento_adverso*" — lista para decirse tal cual. Por encima de `matching.max_values` distintos no se sugiere, y la traza lo dice. Estos valores libres no entran a `lex.words`: sólo los de un `Literal`/`Enum` y los ya usados de `system` y `tags` lo hacen (arriba). Con el mismo criterio, el léxico puede armar unos pocos ejemplos reales de la proyección — un modelo, su plural, un campo con un valor si lo hay — para que "what can I say?" muestre algo que el mundo puede resolver, no un ejemplo genérico de otro mundo.

## Invariantes

- Todo lo que el léxico sabe de un mundo se puede reconstruir desde su store: ninguna palabra de un mundo vive en código. Las palabras generales (determinantes, interrogativos, los verbos del kernel, las construcciones por tipo de campo) sí son de pron y valen para todo mundo.
- Un cambio de `hash_mundo` invalida el léxico y sus embeddings; escribir en el ledger no.
- El léxico se puede listar: "what can I say?" imprime las palabras de la proyección con su motivo.
