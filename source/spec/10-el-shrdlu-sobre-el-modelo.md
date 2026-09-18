# 10 · El SHRDLU sobre el modelo

Los documentos anteriores dicen qué es un sustantivo, un verbo y un movimiento. Este dice cómo se monta la gramática sobre un modelo concreto sin escribir código por modelo: cómo los campos se vuelven propiedades de las que se puede hablar, cómo una relación llega al índice de aristas de sldb en bytes, y cómo conviven el SHRDLU y `graph_ui`, dos superficies sobre las mismas formas.

## 1. Los campos son las propiedades del objeto

Un modelo es una clase y sus campos son atributos. El SHRDLU convierte cada campo en un conjunto de oraciones admitidas, y qué oraciones admite lo decide **el tipo del campo**, leído del esquema (`fields show models/M`). No hay una tabla por modelo: hay una tabla por tipo.

| tipo del campo | preguntar | usar como adjetivo | escribir | llamada |
|---|---|---|---|---|
| `str` | "what notes does X have?" | "saying *pizza*" → `notes ~ "pizza"` | "add a note *birthday*", "saying…" | `get …campo` / `fields update` |
| `int`, `float` | "how many people does X have?", "what is the capacity?" | "for 6" → `capacity >= 6`; "more than 4" → `>`; "of 6" → `= 6` | "change it to 9" | idem |
| `Literal`, `Enum` | "which zone is X in?", "what status is it in?" | "on the terrace" → `zone = "terrace"`; "pending ones" → `status = "pending"` | "set it to confirmed" (transición si el modelo tiene `State`, 03) | idem; valores en el léxico (05) |
| `bool` | "is X active?" | "active ones" → `active = true` | "activate it" | idem |
| `list[str]` | "what tags does it have?" | "with the tag T" → `"T" in tags` | "add T", "remove T", "no duplicates" | `fields append / remove / clean` |
| `list[Modelo]`, tabla | "what arguments does it have?", "the second one?" | — | "add an argument…" con payload | `…campo.i.sub`, `fields append` |
| `dict` | "what is in metadata?", "the author?" | "by author A" → sobre `metadata.author` | "set the author to A" | `…campo.sub` |
| campo opcional vacío | "does it have provenance?" | "with provenance" → `has(provenance)` | "remove its provenance" | `has()` / `fields remove` |

Reglas que completan la tabla:

- **Cada campo tiene un alias** (05) que da su nombre y sus preposiciones: `capacity ← "for N"`, `zone ← "on the Z"`, `name ← "named"`. Sin alias, el campo se nombra por su identificador.
- **Un alias puede nombrar un predicado**: `large → (where Table "capacity >= 6")`. Así "the large tables" es un adjetivo del mundo sin código. El alias declara sobre qué modelo vale.
- **Comparar dos objetos** es una condición con interpolación (03): "does the reservation fit at table 12?" es el alias `fits → (where Table "capacity >= {party_size}")` evaluado sobre la mesa con los valores de la reserva.
- **Contar** es el tamaño del conjunto de direcciones: "how many tables are on the terrace?" es `find … --where` y contar. Sumar, promediar y ordenar sobre un campo son lecturas del campo en cada dirección del conjunto: `get` por dirección, N veces; pron no lee payloads enteros para eso.
- **El nombre natural de un objeto** lo declara el mundo en el `ProjectionDoc`, campo `display`, una plantilla por modelo: `Table: "table {number}"`, `Reservation: "{date} {time}, {party_size} people"`. Sin plantilla, se usa `title` si existe y el nombre del documento si no.
- **Nombrar un objeto por un campo** es un predicado de igualdad: "table 12" es `number = 12` porque `number` es el campo `key` que el `ProjectionDoc` declara para `Table`. Sin `key`, "la mesa 12" se busca como nombre propio (`doc ~ "12"`).
- **Una escritura respeta el tipo**: "change it to nine" en un `int` se convierte; "change it to many" es missing con el tipo como pista. Un `Literal` solo acepta sus valores y ofrece la lista.

Todo esto se deriva del esquema en el momento de cargar el léxico. Registrar un modelo nuevo en el mundo alcanza para que sus campos se puedan preguntar, usar como adjetivo y escribir; los alias y las plantillas de `display` son lo único que alguien escribe a mano, y son documentos.

## 2. Cómo una relación llega al índice de aristas

La relación es un documento de sldb desde que se afirma hasta que se lee como arista. El camino en bytes:

### 2.1 El tipo, una vez por mundo

Un `RelationTypeDoc` de sldb, trackeado en el store del mundo, por ejemplo `relations/types/assigned_to.md`:

```yaml
name: assigned_to
direction: directed
cardinality: many_to_one
source_types: [Reservation]
target_types: [Table]
condition: "capacity >= {party_size}"
```

y en el cuerpo la descripción, que entra al léxico como motivo del verbo. La `condition` del tipo vale para todas sus aristas; una instancia puede traer la suya y reemplazarla. El mismo nombre se registra como predicado del store con su eje, `sldb predicates add assigned_to --axis WHERE`, para que los links en prosa `[assigned_to:: [[table-12]]]` compartan vocabulario con las aristas autoradas.

### 2.2 La instancia, una por arista

Un `RelationDoc`, por ejemplo `relations/assigned_to--reservation-2026-09-11-ana-rojas--table-12.md`:

```yaml
source_id: Reservation:reservation-2026-09-11-ana-rojas
target_id: Table:table-12
relation_type: assigned_to
condition: ""
```

`condition` vacía: hereda la del tipo. Se llena solo cuando esta arista tiene una regla distinta.

Los ids son `Modelo:nombre`, el id de exportación de sldb, y son los mismos que el índice de aristas usa dentro de `sldb://document/Modelo:nombre`. Cuando el mundo tiene stores enlazados, el id completo es `store:Modelo:nombre` con el nombre del store tal como está en `store_index.stores`, y `local:` se omite: `Modelo:nombre` siempre es del store propio. Dos documentos con el mismo modelo y nombre en stores distintos son dos objetos distintos, y pron los distingue en referentes, intersecciones y aristas por ese prefijo; en la respuesta en natural, cuando hay choque, agrega el store ("table 12 del store *north-branch*"). Un `RelationDoc` puede apuntar a otro store con el prefijo; el índice lo resuelve contra los stores enlazados, calificando el id del extremo. El nombre del documento es `<tipo>--<origen>--<destino>`, así una arista se puede buscar por dirección (`find 'st.{RelationDoc}' --where 'source_id = "…"'`) sin pasar por el índice, y dos afirmaciones iguales chocan en el nombre en vez de duplicarse.

### 2.3 Del store al índice de aristas

El índice de aristas no es un snapshot aparte: es un índice del store, como el semántico o el de secciones (03). Cada escritura de sldb sobre un documento (`create`, `save payload`, `untrack`) deja al día, en la misma operación, el shard de aristas de ese documento — no hay un comando que "correr" para que una arista aparezca (04). `sldb.api.rebuild_edges` solo tiene trabajo cuando algo tocó el store por fuera de sldb. Lo que ese índice compone:

- un nodo `sldb://document/Modelo:nombre` por documento de contenido, con `node_type` = el modelo, sus tags y sus secciones;
- un nodo `sldb://relation_type/<name>` por `RelationTypeDoc`, con `source_types`, `target_types`, cardinalidad y eje, y **aristas `applies_to_source` y `applies_to_target`** desde ese nodo a cada `sldb://model/<M>` que nombra: así los verbos de una clase son sus aristas entrantes;
- un nodo `sldb://field/<M>.<f>` por campo de cada modelo, con tipo y descripción, y una arista `has_field` desde el modelo; una arista `extends` de cada modelo a sus `base_models`;
- un nodo `sldb://anchor/<symbol>` por `AnchorDoc` y una arista `names` a lo que la forma de su `ref` nombra (modelo, campo, tipo de relación; en un `(move …)`, una por paso). Con esto el índice contesta "¿qué puedo hacer con una reserva?" con `edges_to(sldb://model/Reservation)` filtrado por `applies_to_*` y `names`, más las aristas de sus ancestros por `extends`, sin que nadie registre verbos por sustantivo;
- **una arista por `RelationDoc`**, colgada del nodo origen: `relation_type`, y en `metadata` el id del `RelationDoc`, la condición y `origin: relation_doc`. El `RelationDoc` no es nodo;
- una arista por link con predicado en prosa, con `origin: link`, documento y sección de donde salió;
- los documentos con tag `type.pron.move` excluidos de lo que pron lee como grafo (`doc_kind.tags_outside_graph()`, 07) — el índice los tiene, es la lectura la que filtra;
- integridad referencial: una arista cuyo origen o destino no existe se reporta (`check_edges`), nunca revienta la lectura — el índice siempre se puede componer.

Cada uno de esos aportes vive en el shard de quien lo produce (el documento, el modelo o el store), así que editar un documento reescribe solo su propio shard, nunca el índice entero (03).

### 2.4 Cómo pron lo lee

Solo con tres preguntas al índice de aristas: `edges_from(nodo, tipo)`, `edges_to(nodo, tipo)`, y "is there an edge from A to B of type T?". Cada arista devuelta trae su `origin` y su condición, y con eso pron sabe si se puede negar por oración (solo `relation_doc`) y si hay que evaluar algo antes de aceptarla como legal. Cualquier consulta más rica ("todo lo relacionado con X a dos saltos") existe como método de `Graph` (`descendants`, `neighbors_via`, 12) pero no entra al léxico salvo que un alias la nombre.

### 2.5 Estados

Un campo `Literal` se vuelve una máquina cuando el mundo tiene un modelo `State` con documentos que declaran `machine: Modelo.campo` y `name: <valor>`, y aristas `transitions_to` entre ellos. La convención que une campo y documento es el par `(machine, name)`: el valor `confirmed` de `Reservation.status` es el documento de `State` con `machine = "Reservation.status"` y `name = "confirmed"`, que se encuentra con dos predicados y una intersección (02). Así dos modelos pueden tener estados con el mismo nombre y transiciones distintas: `Order.status` y `Reservation.status` tienen cada uno su `confirmed`. pron no necesita declarar nada más: al ver un campo `Literal` para el que existen documentos `State` con esa `machine`, cambiar ese campo pasa a ser una transición (03). Un `Literal` sin documentos `State` es un campo común.

## 3. Dos superficies sobre el mismo mundo

El SHRDLU no es la única superficie del mundo. `graph_ui`, el editor visual del grafo tipado de sldb, es otra al mismo nivel: el SHRDLU convierte oraciones en formas (06) y proyecta lenguaje; `graph_ui` convierte gestos en formas y proyecta visualizaciones. Ninguna pasa por la otra; las dos terminan en la misma evaluación (13), con los mismos permisos, verificaciones, `MoveDoc` y `undo`. Cada una tiene su propio vocabulario sobre los mismos nombres del mundo: el SHRDLU, el léxico (05), que dice cómo se dice cada forma; `graph_ui`, su vocabulario visual, que dice cómo se dibuja y con qué gesto se escribe. Por debajo de las dos queda el CLI de sldb, que no es una superficie de pron sino el sustrato.

Hoy `graph_ui` todavía escribe por debajo de las formas: habla a sldb por `pron.Store` (12 §4), lee `schema()`/`docs()` para dibujar formularios y aristas, escribe por `create`/`replace`/`untrack`, y edita modelos con `model_template_edit`/`model_fields_add`/`model_fields_remove`/`model_validate_draft`/`model_promote`. Un `RelationDoc` se crea como cualquier documento, con `source_id`, `target_id` y `relation_type` como enum. Las escrituras de datos pasan a formas; la edición de esquema no tiene forma y sigue por `pron.Store`.

Reglas de convivencia:

- **Toda escritura termina en sldb.** Las formas, `world.store.replace`/`update_field` y `fields update` terminan en la misma función, `save_payload`: re-render, roundtrip, hashes, índice semántico. No hay una escritura que pron no pueda ver.
- **pron detecta lo que no hizo.** Antes de cada turno compara `hash_mundo`; si cambió y no fue por su último movimiento, recarga léxico y proyección, marca el grafo como viejo hasta el próximo refresh, y el ledger recibe un movimiento `externo` con la lista de documentos cuyo `hash_d` cambió. "why is it at 9 people?" puede responder "it changed outside pron between 21:03 and 21:10". Una superficie que escribe por formas no es externa: su movimiento está en el ledger.
- **pron lee antes de escribir.** Un `fields update` va precedido por un `get` del campo; el valor anterior va al `MoveDoc`. Si dos superficies escriben el mismo campo en la misma ventana, gana el último y el ledger lo muestra; no hay bloqueo de documento, solo el `store_lock` de sldb sobre los índices.
- **El refresh es de quien escribe.** Una forma refresca como cualquier movimiento; quien escribe por `pron.Store` corre el refresh o deja el grafo viejo, y pron lo dirá al leer. La política es la misma que para el agente expansor (01).
- **Ninguna superficie tiene mundo propio.** Los formularios de `graph_ui` salen de `/schema`, sus enums son los `Literal`, sus relaciones son los `RelationTypeDoc`; el léxico del SHRDLU sale de lo mismo. Lo que una superficie agrega (palabras, alias, formas de decir; símbolos, trazos, gestos) no agrega capacidades: nombra formas. Una escritura por `pron.Store` no pasa por la verificación de `source_types` ni por la condición; el índice de sldb la reporta como arista sin extremos válidos si no existen (`check_edges`, un reporte, no un rechazo — el índice siempre se puede leer), y pron la reporta como arista con condición incumplida cuando la lee.

## 4. Lo que hay que construir, en orden

Esto se agrega al orden de 08, dentro de los pasos 2, 5 y 6:

- **Paso 2, léxico**: la tabla de tipos de arriba, los alias de campo, los alias de predicado, `display` y `key` en el `ProjectionDoc`.
- **Paso 5, verbos de acción**: la conversión de literal a tipo, la reevaluación de condiciones, la detección de escrituras externas por `hash_mundo` y `hash_d`.
- **Paso 6, verbos transitivos**: el `kgdb ingest` unificado (en kgdb), el nombre canónico de los `RelationDoc`, la lectura de `origin` y `condition` en las aristas, la convención `State`.

Ninguna de estas piezas es código por modelo. Si al implementar aparece un `if modelo == "Table"`, la pieza está mal ubicada: va al esquema, a un alias o al `ProjectionDoc`.
