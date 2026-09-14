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

Un `AnchorDoc` es un alias. Su contrato:

| campo | contenido |
|---|---|
| `symbol` | la palabra canónica |
| `forms` | todas las formas que la superficie reconoce, listadas: `reservation, reservations`; `confirma, confirmá, confirm it` (11 §1) |
| `ref` | lo que nombra, en una de las siete formas de abajo |
| `motive` | lo que se muestra al preguntar qué significa |
| `steps` | solo para `ref: compose`: la lista de pasos |

Las formas de `ref`:

| forma | ejemplo | qué es |
|---|---|---|
| `model:M` | `client → model:Client` | un sustantivo |
| `field:M.f` | `named → field:Client.name` | un atributo, con sus preposiciones en `forms` |
| `predicate:M:<where>` | `large → predicate:Table:capacity >= 6` | un adjetivo; `<where>` puede usar `{campo}` del sujeto |
| `relation:R` | `asignale → relation:assigned_to` | un verbo transitivo; `forms` puede marcar la lectura inversa (`has ← relation:booked_by`) |
| `action:<verbo> M.f=v` | `confirm → action:change Reservation.status=confirmed` | un verbo de acción con campo y valor fijos |
| `doc:M:nombre` | `el proyector → doc:SurfaceDoc:surface-pron-infra-projector` | un nombre propio fijo para un objeto |
| `compose` | `book`, abajo | una oración compuesta |

**Oraciones compuestas.** Un alias `compose` declara, en `steps`, una secuencia de pasos con ranuras que la oración llena. "book her a table for 6 on Friday at 9pm":

```yaml
symbol: book
forms: [book her, book him, book them, make a reservation for]
ref: compose
motive: create a reservation for someone and put it at a table
steps:
  - {do: create, model: Reservation, fields: $literals}
  - {do: assert, relation: booked_by,   source: $created, target: $referent:Client}
  - {do: assert, relation: assigned_to, source: $created, target: $object:Table}
```

Las ranuras son cuatro y fijas: `$literals`, los literales de la oración asignados a campos del modelo por sus alias; `$created`, el documento que dejó un paso `create`; `$referent:M`, el referente de la oración con esa clase ("her"); `$object:M`, la frase nominal de la oración con esa clase ("a table on the terrace for 6"). Un paso puede ser `create`, `assert` o `change`. Cada paso pasa por las mismas verificaciones y permisos que si fuera una oración sola; si un paso no se puede resolver, la oración entera es ambigua o missing antes de ejecutar nada; los pasos se ejecutan en orden en un solo movimiento con un solo refresh. No hay condicionales ni repeticiones: lo que no cabe en una secuencia fija de tres tipos de paso no es un alias, es un patrón general de pron o no existe.

Un alias sí aporta significado a una expresión: "large" significa algo porque alguien decidió que es capacidad mayor o igual a seis. Lo que no hace es agregar capacidades: todo `ref` apunta a algo que el mundo ya puede hacer sin el alias, con la dirección o el comando completo. Por eso no es la fuente del léxico, sino su forma en lengua natural, y por eso se puede listar, revisar y borrar sin que nada deje de ser posible.

Un alias puede nombrar también un **verbo de acción con campo y valor fijos**: `confirm → action:change Reservation.status=confirmed`. Es la única forma en que un mundo agrega verbos sin código, y sigue siendo un alias: el verbo real es `change` y pasa por las mismas verificaciones, incluida la transición (03).

Son la única fuente de la forma hablada. El identificador `CliCommandDoc` no se convierte en "command" por ninguna regla: alguien escribe el alias `command → model:CliCommandDoc`, con su plural en `forms`. Un término sin alias se nombra y se reconoce por su identificador tal cual y, además, partido en palabras (`cli command doc`, `party size`): esa forma la deriva el léxico del identificador, no es un `AnchorDoc`, y sirve de calce hasta que un alias diga algo mejor.

Un alias entra a una sesión solo si todo lo que apunta está en la proyección: el modelo de su `ref`, la relación, y en un alias compuesto el modelo y la relación de cada paso. Un alias hacia un modelo fuera de `models` no existe para esa sesión, aunque la lista `aliases` lo nombre.

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
