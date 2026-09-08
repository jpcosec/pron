# Arquitectura de pron

La arquitectura objetivo de pron, proyección gráfica de source/spec. Sustantivos por dirección en sldb, verbos transitivos como modelos de relación de kgdb almacenados en sldb y ensamblados por su ingest, verbos de acción como escrituras de sldb. La v1 está en la rama v1-code-and-kb.

## Objetivo · componentes

Pron pide por dirección, recorre aristas y escribe documentos. No resuelve, no filtra, no declara verbos. Los sustantivos son st.{Modelo+}.doc.campo más un predicado; los verbos transitivos son los modelos de relación de kgdb (RelationTypeDoc, RelationDoc), que sldb almacena como documentos y el ingest de kgdb ensambla; los verbos de acción son docs create, fields update y refrescar.

- El léxico sale de los modelos: nombre, campos con descripción, tags, familias ({Modelo+}). Los RelationTypeDoc dan los verbos transitivos con sus tipos válidos. Los AnchorDoc son alias, no la fuente.
- Un sustantivo es una dirección más un predicado, y eso lo responde sldb (ls, get, glob, find, --where). Pron no tiene cascada de resolución propia.
- Los modelos de relación son de kgdb: RelationTypeDoc declara el verbo con sus tipos válidos y su eje, RelationDoc es una arista autorada. Pron los registra en su store al declarar el mundo; sldb los guarda como documentos; el ingest de kgdb los vuelve aristas. kgdb sigue siendo derivado y de solo lectura.
- El editor (sldb serve + graph_ui) escribe por la misma save_payload que pron. pron detecta lo que no hizo comparando hash_mundo y hash_d, recarga léxico y registra un movimiento externo.
- Las condiciones viven en el RelationTypeDoc (para todas sus aristas) o en un RelationDoc (que reemplaza la del tipo), y las evalúa sldb sobre el sujeto con find --where; pron solo las pasa.
- Una transición no se dispara en kgdb. Es una escritura en sldb, arista más campo de estado, seguida de un refresh que reensambla el grafo.
- El kernel son los verbos de acción y cada uno es una operación de sldb que ya existe: docs create, fields update y append, docs untrack, stores update.
- La declaración del mundo es store_index.yaml: modelos registrados, stores enlazados, predicados. La proyección es la parte de eso que una sesión puede nombrar.
- El por qué se lee de las aristas del eje WHY, HOW y PROVENANCE que los predicados del store le dan a cada verbo, más el ledger.
- Los sustantivos del mundo de pron son sus propios modelos: átomo, comando, superficie, anchor. Hoy los átomos están tipados con el AtomDoc de deskops y hay trece modelos de deskops registrados sin documentos; los dos salen, deskops es otra instancia sobre el núcleo, no la fuente de los modelos de pron.
- El kgdb ingest unificado (nodos, nodos relation_type, aristas desde RelationDoc y links, ledger excluido, hash_mundo, integridad como error) es el prerrequisito de source/spec/08; hoy sus dos mitades existen por separado.

```mermaid
graph TD
    subgraph afuera ["Fuera de pron"]
        hablante["Quien habla · persona, LLM u otro producto"]
        editor["Editor · sldb serve (/schema, /graph, POST /save) + graph_ui · formularios desde el esquema, relaciones como RelationDoc"]
    end
    subgraph pron ["pron · el SHRDLU"]
        superficie["Superficie · oración → (alcance, predicado) para sustantivos · (verbo, sujeto, objeto) para verbos · respuesta en natural"]
        proyeccion["Proyección · ProjectionDoc · stores, modelos, relaciones con modo leer / afirmar, acciones, alias, naming, display, key"]
        dialogo["Diálogo · pendiente (¿cuál?) y referentes (ese, la anterior)"]
        kernel["Kernel · verbos de acción · crear · cambiar · agregar · limpiar · quitar · olvidar · refrescar · lee antes de escribir · reevalúa condiciones"]
        embeddings["Embeddings · palabra sin calce → cercanos por descripciones de modelos y campos"]
        ledger["Ledger · MoveDoc por turno · interpretación, consultas, escritura, hash_mundo antes y después · movimientos externos detectados"]
        proyector["Proyector · stores update · semantic-export · kgdb ingest"]
    end
    subgraph mundo ["Mundo · sldb · los sustantivos · almacena todo documento, incluidas las relaciones de kgdb"]
        store_index["store_index.yaml · la declaración del mundo · modelos registrados (los de contenido y los de relación de kgdb) · stores enlazados · predicados"]
        modelos["Modelos de contenido · SUSTANTIVOS · nombre, campos con descripción, tags, familia"]
        anchors["AnchorDoc · alias y motivos · solo lo que no coincide con un modelo, campo o tag"]
        docs["Documentos · los objetos del mundo · markdown reversible"]
    end
    subgraph superficies ["Superficies de sldb · lo que pron usa, no reimplementa"]
        addr["Direcciones · st.{Modelo+}.doc.campo.sub · se.tag · gse.tag · --where · ls, get, glob, find"]
        writes["Escrituras · docs create / untrack · fields update, append, clean · re-renderiza, valida roundtrip, cascada de hashes"]
        export["semantic-export · modelos, documentos, secciones, tags, DAG"]
    end
    subgraph grafo ["kgdb · dueño de los verbos transitivos · el grafo es derivado y de solo lectura"]
        reltypes["RelationTypeDoc · VERBOS TRANSITIVOS · modelo de kgdb · name, source_types, target_types, cardinality, condition, eje del predicado"]
        relinst["RelationDoc · una arista autorada · modelo de kgdb, guardada como documento en sldb · source_id, target_id, relation_type, condition"]
        ingest["kgdb ingest · nodos desde semantic-export · nodos relation_type · aristas desde los RelationDoc y los links con predicado · excluye el ledger · hash_mundo · integridad como error"]
        snapshot["GraphSnapshot · nodos = documentos · aristas = tags, contención y relaciones autoradas"]
        traversal["edges_from · edges_to · ¿existe la arista? · cada arista trae origin y condition"]
    end
    hablante -->|"una oración"| superficie
    editor -->|"POST /save · misma save_payload"| writes
    superficie -->|"movimiento externo si hash_mundo cambió sin pron"| ledger
    superficie -->|"referentes"| dialogo
    superficie -->|"cada palabra está en la proyección"| proyeccion
    proyeccion -->|"qué mundo"| store_index
    proyeccion -->|"léxico de sustantivos · nombres, campos, tags, familias"| modelos
    store_index -->|"models add kgdb…:RelationTypeDoc, RelationDoc · el mundo declara qué verbos existen"| reltypes
    proyeccion -->|"léxico de verbos transitivos"| reltypes
    proyeccion -->|"alias"| anchors
    superficie -->|"palabra sin calce → cercanos"| embeddings
    superficie -->|"sustantivo = st.{Modelo+} + where · un campo = .campo.sub"| addr
    addr -->|"reads"| docs
    superficie -->|"¿el verbo aplica al sujeto y al objeto? · source_types, target_types"| reltypes
    superficie -->|"verbo transitivo leído · ¿quién implementa X? · ¿existe pasa_a desde el estado actual?"| traversal
    superficie -->|"condición de la arista evaluada por sldb sobre el sujeto · find … --where"| addr
    superficie -->|"verbo de acción"| kernel
    kernel -->|"crear doc · cambiar campo · escribir RelationDoc"| writes
    writes -->|"re-renderiza y valida"| docs
    writes -->|"una arista nueva es un documento más del store"| relinst
    kernel -->|"refrescar tras escribir"| proyector
    proyector -->|"runs"| export
    proyector -->|"runs"| ingest
    export -->|"nodos"| ingest
    relinst -->|"una arista por RelationDoc"| ingest
    ingest -->|"builds"| snapshot
    traversal -->|"reads"| snapshot
    superficie -->|"el movimiento entero"| ledger
    ledger -->|"¿por qué? · aristas del eje WHY / HOW"| traversal
    superficie -->|"resultado · ¿cuál? · no existe, cercanos"| hablante
```

## Objetivo · una conversación

Cinco turnos de source/spec/09 sobre el mundo del restaurante (09a): crear con payload, un verbo transitivo que crea su sujeto con dos predicados cruzados, una ambigüedad y su respuesta, una transición guardada por pasa_a y una condición evaluada por sldb, y el por qué.

- Cada mensaje es la llamada real de sldb o kgdb; correrlas en la shell da el mismo resultado que el turno.
- Dos restricciones son dos consultas y una intersección de direcciones; también cuando una lista viene de kgdb (edges_to) y otra de sldb (find).
- Verificar que el verbo aplica es leer source_types y target_types del RelationTypeDoc de kgdb, por dirección en sldb. Verificar que la arista existe es kgdb. Verificar la condición es sldb, con find --where sobre el sujeto.
- Afirmar un verbo transitivo es docs create de un RelationDoc; si el sujeto no existe, se crea en el mismo movimiento. kgdb nunca recibe una orden: su ingest reensambla.
- Una transición es cambiar el campo estado, permitida porque existe pasa_a desde el estado actual y su condición se cumple. No crea aristas.
- Una pendiente de elección se contesta con una designación contra los candidatos ya mostrados; un conjunto de exactamente uno vale como antecedente singular.
- El MoveDoc se escribe después del refresh y no lo desfasa: el ledger queda fuera de hash_mundo y del grafo.
- El mundo del restaurante está declarado entero en source/spec/09a: modelos, tipos de relación con su condición, transiciones, ProjectionDoc y alias.

```mermaid
sequenceDiagram
    actor hablante
    participant superficie
    participant dialogo
    participant lexico
    participant sldb_addr
    participant sldb_write
    participant kgdb
    participant kernel
    participant proyector
    participant ledger
    hablante->>superficie: crea un cliente que se llame Ana Rojas, teléfono 9 5555 1234
    superficie->>lexico: crea → acción crear · cliente → Cliente · se llame → nombre · teléfono → telefono · literales
    superficie->>sldb_addr: fields show models/Cliente · obligatorios nombre, telefono
    superficie->>kernel: crear Cliente {nombre, telefono}
    kernel->>sldb_write: docs create --model Cliente --name cliente-ana-rojas (naming del ProjectionDoc)
    sldb_write->>kernel: tracked · hashes
    kernel->>proyector: refrescar
    proyector->>kgdb: stores update · semantic-export · kgdb ingest
    superficie->>ledger: MoveDoc · payload · dirección creada · hash_mundo antes y después
    superficie->>hablante: Creado el cliente Ana Rojas.
    hablante->>superficie: reservale una mesa en la terraza para 6 personas el viernes a las 21
    superficie->>lexico: reservale → relación de + crea_sujeto Reserva · le → referente · terraza → zona · para 6 → personas y capacidad #gt;= 6
    superficie->>dialogo: le → último singular de clase Cliente · cliente-ana-rojas
    superficie->>sldb_addr: find st.{Mesa} --where 'zona = "terraza"' → 12, 14, 20
    superficie->>sldb_addr: find st.{Mesa} --where 'capacidad #gt;= 6' → 12, 14
    superficie->>superficie: ∩ → mesa-12, mesa-14 · determinante una → mesa-12
    superficie->>sldb_addr: get st.{RelationTypeDoc}.de y .asignada_a · tipos y condición capacidad #gt;= {personas}
    superficie->>sldb_addr: find st.{Mesa} --where 'capacidad #gt;= 6' contiene mesa-12 · condición ok
    superficie->>kernel: crear Reserva · afirmar de → Ana · afirmar asignada_a → mesa-12
    kernel->>sldb_write: docs create Reserva · docs create RelationDoc de · docs create RelationDoc asignada_a
    kernel->>proyector: refrescar (una vez)
    proyector->>kgdb: kgdb ingest · nodos + aristas desde los RelationDoc
    superficie->>ledger: MoveDoc · dos consultas y su intersección · alternativa mesa-14 · tres documentos
    superficie->>hablante: Reserva para Ana Rojas el viernes 11 a las 21:00, 6 personas, mesa 12, pendiente. También servía la 14.
    hablante->>superficie: ¿qué reservas tiene Ana para el viernes?
    superficie->>sldb_addr: find st.{Cliente} --where 'nombre ~ "Ana"' → ana-perez, ana-rojas
    superficie->>dialogo: [ambiguo] pendiente de elección · dos candidatos
    superficie->>ledger: [ambiguo] MoveDoc · libre → pendiente
    superficie->>hablante: [ambiguo] ¿Cuál? (1) Ana Pérez · (2) Ana Rojas
    hablante->>superficie: Rojas
    superficie->>dialogo: designación contra los candidatos · calce único → ana-rojas
    superficie->>kgdb: edges_to(Cliente:cliente-ana-rojas, de) → reserva-2026-09-11-ana-rojas
    superficie->>sldb_addr: find st.{Reserva} --where 'fecha = "2026-09-11"' → ana-rojas, luis-soto
    superficie->>superficie: ∩ → una dirección · conjunto de uno = antecedente singular
    superficie->>ledger: MoveDoc · pendiente → libre
    superficie->>hablante: Una · el viernes 11 a las 21:00, 6 personas, mesa 12, pendiente.
    hablante->>superficie: confirmala
    superficie->>lexico: confirmala → alias action cambiar estado=confirmada · la → referente Reserva
    superficie->>sldb_addr: get st.{Reserva}.reserva-….estado → pendiente
    superficie->>kgdb: edges_from(Estado:pendiente, pasa_a) → confirmada (condition personas #lt;= 8), cancelada
    superficie->>sldb_addr: find st.{Reserva} --where 'personas #lt;= 8' contiene la reserva · transición legal
    superficie->>kernel: cambiar estado
    kernel->>sldb_write: fields update docs/reserva-…/estado '"confirmada"'
    kernel->>proyector: refrescar
    superficie->>ledger: MoveDoc · estado anterior y nuevo · arista y condición evaluada
    superficie->>hablante: Confirmada.
    hablante->>superficie: ¿por qué?
    superficie->>ledger: último MoveDoc con escritura sobre la reserva
    ledger->>superficie: oración · arista pasa_a · condición personas #lt;= 8 · quién · cuándo
    superficie->>kgdb: edges_from(reserva, eje WHY / PROVENANCE)
    superficie->>hablante: Porque lo pediste y la transición pendiente → confirmada era legal · 6 personas, límite 8.
```

## Objetivo · el diálogo

El único estado propio de pron por sesión — si hay o no una pregunta pendiente — y sus cuatro salidas.

- Es la conversación estilo SHRDLU. Una ambigüedad abre una pregunta; la siguiente oración la contesta, no la contesta, o la descarta.
- Todos los movimientos se registran, incluidos los que no cambian de estado.

```mermaid
stateDiagram-v2
    state "Libre · sin pendiente" as libre
    state "Pendiente · candidatos guardados, Meaning con hueco" as pendiente
    [*] --> libre
    libre --> libre : único o missing
    libre --> pendiente : ambiguo
    pendiente --> libre : calza un candidato
    pendiente --> pendiente : no calza
    pendiente --> libre : orden nueva
```
