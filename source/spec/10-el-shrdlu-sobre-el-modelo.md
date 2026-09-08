# 10 · El SHRDLU sobre el modelo

Los documentos anteriores dicen qué es un sustantivo, un verbo y un movimiento. Este dice cómo se monta la gramática sobre un modelo concreto sin escribir código por modelo: cómo los campos se vuelven propiedades de las que se puede hablar, cómo una relación llega a kgdb en bytes, y cómo conviven pron y el editor sobre el mismo mundo.

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
- **Un alias puede nombrar un predicado**: `large → predicate:capacity >= 6`. Así "the large tables" es un adjetivo del mundo sin código. El alias declara sobre qué modelo vale.
- **Comparar dos objetos** es una condición con interpolación (03): "does the reservation fit at table 12?" es el alias `fits → predicate:capacity >= {party_size}` evaluado sobre la mesa con los valores de la reserva.
- **Contar** es el tamaño del conjunto de direcciones: "how many tables are on the terrace?" es `find … --where` y contar. Sumar, promediar y ordenar sobre un campo son lecturas del campo en cada dirección del conjunto: `get` por dirección, N veces; pron no lee payloads enteros para eso.
- **El nombre natural de un objeto** lo declara el mundo en el `ProjectionDoc`, campo `display`, una plantilla por modelo: `Table: "table {number}"`, `Reservation: "{date} {time}, {party_size} people"`. Sin plantilla, se usa `title` si existe y el nombre del documento si no.
- **Nombrar un objeto por un campo** es un predicado de igualdad: "table 12" es `number = 12` porque `number` es el campo `key` que el `ProjectionDoc` declara para `Table`. Sin `key`, "la mesa 12" se busca como nombre propio (`doc ~ "12"`).
- **Una escritura respeta el tipo**: "change it to nine" en un `int` se convierte; "change it to many" es missing con el tipo como pista. Un `Literal` solo acepta sus valores y ofrece la lista.

Todo esto se deriva del esquema en el momento de cargar el léxico. Registrar un modelo nuevo en el mundo alcanza para que sus campos se puedan preguntar, usar como adjetivo y escribir; los alias y las plantillas de `display` son lo único que alguien escribe a mano, y son documentos.

## 2. Cómo una relación llega a kgdb

La relación es un documento de sldb desde que se afirma hasta que se lee como arista. El camino en bytes:

### 2.1 El tipo, una vez por mundo

Un `RelationTypeDoc` de kgdb, trackeado en el store del mundo, por ejemplo `relations/types/assigned_to.md`:

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

Los ids son `Modelo:nombre`, el id de exportación de sldb, y son los mismos que kgdb usa dentro de `sldb://document/Modelo:nombre`. Cuando el mundo tiene stores enlazados, el id completo es `store:Modelo:nombre` con el nombre del store tal como está en `store_index.stores`, y `local:` se omite: `Modelo:nombre` siempre es del store propio. Dos documentos con el mismo modelo y nombre en stores distintos son dos objetos distintos, y pron los distingue en referentes, intersecciones y aristas por ese prefijo; en la respuesta en natural, cuando hay choque, agrega el store ("table 12 del store *north-branch*"). Un `RelationDoc` puede apuntar a otro store con el prefijo; su ingest lo resuelve contra el snapshot de ese store. El nombre del documento es `<tipo>--<origen>--<destino>`, así una arista se puede buscar por dirección (`find 'st.{RelationDoc}' --where 'source_id = "…"'`) sin pasar por kgdb, y dos afirmaciones iguales chocan en el nombre en vez de duplicarse.

### 2.3 Del store al grafo

El refresh (04) corre tres cosas:

1. `sldb stores update`: índices semánticos y de secciones al día.
2. `sldb stores semantic-export`: cada documento trackeado, incluidos los `RelationDoc` y `RelationTypeDoc`, sale como entrada con id, modelo, tags y hashes.
3. `kgdb ingest`: **un solo comando** que construye el snapshot con:
   - un nodo `sldb://document/Modelo:nombre` por documento de contenido, con `node_type` = el modelo, sus tags y sus secciones, como hoy;
   - un nodo `sldb://relation_type/<name>` por `RelationTypeDoc`, con `source_types`, `target_types`, cardinalidad y eje, y **aristas `applies_to_source` y `applies_to_target`** desde ese nodo a cada `sldb://model/<M>` que nombra: así los verbos de una clase son sus aristas entrantes;
   - un nodo `sldb://field/<M>.<f>` por campo de cada modelo, con tipo y descripción, y una arista `has_field` desde el modelo; una arista `extends` de cada modelo a sus `base_models`;
   - un nodo `sldb://anchor/<symbol>` por `AnchorDoc` y una arista `names` a lo que su `ref` nombra (modelo, campo, tipo de relación; un `compose`, una por paso). Con esto el grafo contesta "¿qué puedo hacer con una reserva?" con `edges_to(sldb://model/Reservation)` filtrado por `applies_to_*` y `names`, más las aristas de sus ancestros por `extends`, sin que nadie registre verbos por sustantivo;
   - **una arista por `RelationDoc`**, colgada del nodo origen: `relation_type`, y en `metadata` el id del `RelationDoc`, la condición y `origin: relation_doc`. El `RelationDoc` no es nodo;
   - una arista por link con predicado en prosa, con `origin: link`, documento y sección de donde salió;
   - los documentos con tag `type.pron.move` excluidos;
   - integridad referencial: una arista cuyo origen o destino no existe es error del ingest, y el lint de pron lo convierte en fallo de build.

El snapshot guarda en `metadata` el `hash_mundo` con que se construyó. Hoy kgdb tiene las dos mitades por separado, `ingest-sldb` y `assemble_authored_graph`, y ninguna en el mismo comando; unirlas es el prerrequisito de 08.

### 2.4 Cómo pron lo lee

Solo con tres preguntas al grafo: `edges_from(nodo, tipo)`, `edges_to(nodo, tipo)`, y "is there an edge from A to B of type T?". Cada arista devuelta trae su `origin` y su condición, y con eso pron sabe si se puede negar por oración (solo `relation_doc`) y si hay que evaluar algo antes de aceptarla como legal. Cualquier consulta más rica ("todo lo relacionado con X a dos saltos") es `scope` de kgdb y entra al léxico solo si un alias la nombra.

### 2.5 Estados

Un campo `Literal` se vuelve una máquina cuando el mundo tiene un modelo `State` con documentos que declaran `machine: Modelo.campo` y `name: <valor>`, y aristas `transitions_to` entre ellos. La convención que une campo y documento es el par `(machine, name)`: el valor `confirmed` de `Reservation.status` es el documento de `State` con `machine = "Reservation.status"` y `name = "confirmed"`, que se encuentra con dos predicados y una intersección (02). Así dos modelos pueden tener estados con el mismo nombre y transiciones distintas: `Order.status` y `Reservation.status` tienen cada uno su `confirmed`. pron no necesita declarar nada más: al ver un campo `Literal` para el que existen documentos `State` con esa `machine`, cambiar ese campo pasa a ser una transición (03). Un `Literal` sin documentos `State` es un campo común.

## 3. El editor y pron sobre el mismo mundo

El mundo tiene dos superficies de escritura además de pron: el CLI de sldb, y el editor. El editor es `sldb serve` con sus tres rutas, `/schema` (los modelos con sus campos, tipos y enums), `/graph` (los documentos con payload y tags) y `POST /save` (un payload nuevo para un documento), y sobre eso graph_ui, el editor visual de grafos de kgdb, que lee `/schema` para dibujar formularios y escribe por `/save`. Un `RelationDoc` se crea en el editor como cualquier documento: un formulario con `source_id`, `target_id` y `relation_type` como enum.

Reglas de convivencia:

- **Las tres superficies escriben por sldb.** `/save` y `fields update` terminan en la misma función, `save_payload`: re-render, roundtrip, hashes, índice semántico. No hay una escritura que pron no pueda ver.
- **pron detecta lo que no hizo.** Antes de cada turno compara `hash_mundo`; si cambió y no fue por su último movimiento, recarga léxico y proyección, marca el grafo como viejo hasta el próximo refresh, y el ledger recibe un movimiento `externo` con la lista de documentos cuyo `hash_d` cambió. "why is it at 9 people?" puede responder "it changed outside pron between 21:03 and 21:10".
- **pron lee antes de escribir.** Un `fields update` va precedido por un `get` del campo; el valor anterior va al `MoveDoc`. Si el editor y pron escriben el mismo campo en la misma ventana, gana el último y el ledger lo muestra; no hay bloqueo de documento, solo el `store_lock` de sldb sobre los índices.
- **El refresh es de quien escribe.** El editor que crea un `RelationDoc` corre el refresh o deja el grafo viejo; pron lo dirá al leer. La política es la misma que para el agente expansor (01).
- **El editor no tiene vocabulario propio.** Sus formularios salen de `/schema`, sus enums son los `Literal`, sus relaciones son los `RelationTypeDoc`. Los dos operan sobre los mismos objetos, campos y tipos de relación porque leen el mismo esquema. No es una equivalencia exacta: el editor ve el mundo entero y pron ve una proyección, así que en una sesión pron puede decir menos de lo que el editor puede escribir; y pron agrega lo que el editor no tiene, las condiciones evaluadas antes de escribir, el ledger y el diálogo. Un `RelationDoc` creado en el editor no pasa por la verificación de `source_types` ni por la condición; el ingest de kgdb lo rechaza si los extremos no existen, y pron lo reporta como arista con condición incumplida cuando la lee.

## 4. Lo que hay que construir, en orden

Esto se agrega al orden de 08, dentro de los pasos 2, 5 y 6:

- **Paso 2, léxico**: la tabla de tipos de arriba, los alias de campo, los alias de predicado, `display` y `key` en el `ProjectionDoc`.
- **Paso 5, verbos de acción**: la conversión de literal a tipo, la reevaluación de condiciones, la detección de escrituras externas por `hash_mundo` y `hash_d`.
- **Paso 6, verbos transitivos**: el `kgdb ingest` unificado (en kgdb), el nombre canónico de los `RelationDoc`, la lectura de `origin` y `condition` en las aristas, la convención `State`.

Ninguna de estas piezas es código por modelo. Si al implementar aparece un `if modelo == "Table"`, la pieza está mal ubicada: va al esquema, a un alias o al `ProjectionDoc`.
