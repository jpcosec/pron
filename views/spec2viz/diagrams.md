# Arquitectura de pron

Actual: derivado del código. Objetivo: un SHRDLU sobre el mundo que sldb y kgdb ya reparten — sustantivos por dirección en sldb, verbos transitivos como modelos de relación de kgdb almacenados en sldb y ensamblados por su ingest, verbos de acción como escrituras de sldb.

## Arquitectura actual

CLI/REPL sobre un kernel de Meaning (s-expresiones ancladas por gramática viva), operaciones que despachan a los bridges — la única puerta a sldb y kgdb — y un generador de docs que deriva del propio código.

- CLI y REPL comparten el mismo Evaluator; no hay una segunda gramática.
- Session (.pron/session.json) solo persiste la desambiguación del CLI no interactivo; el REPL la mantiene en memoria.
- Los bridges (SldbBridge, KgdbBridge) son la única puerta a las librerías sldb/kgdb, por atom-bridges-are-the-only-doors-to-sldb-and-kgdb.
- El generador de docs (pron docs) deriva CliCommandDoc de los docstrings de los handlers _cmd_* y SurfaceDoc del AST de cada módulo público.

```mermaid
graph TD
    cli["CLI (pron #lt;cmd#gt;)"]
    repl["REPL (pron repl)"]
    surface["Surface grammar"]
    render["Renderer (JSON/text)"]
    sexpr["S-expression parser/serializer"]
    anchors["AnchorRegistry (gramática viva)"]
    evaluator["Evaluator"]
    resolution["Cascada de resolución de nouns"]
    session["Session (.pron/session.json)"]
    read_ops["Read ops (check/next/return)"]
    write_ops["Write ops (create/assert/ingest)"]
    write_models["FactDoc / PropositionDoc"]
    sldb_bridge["SldbBridge"]
    kgdb_bridge["KgdbBridge"]
    docs_gen["Generador de docs (pron docs)"]
    projector["Projector (model add / refresh / project)"]
    sldb_lib["sldb"]
    kgdb_lib["kgdb"]
    store[".sldb store + snapshot KGDB"]
    workspace["knowledge/ (atoms, anchors, commands, surfaces)"]
    cli -->|"tokens → s-expr"| surface
    cli -->|"renders"| render
    cli -->|"eval / cmd_eval"| evaluator
    cli -->|"project / model add"| projector
    cli -->|"docs"| docs_gen
    cli -->|"resultado ambiguo (no interactivo)"| session
    repl -->|"shlex.split"| surface
    repl -->|"evaluates"| evaluator
    repl -->|"renders"| render
    surface -->|"kind de cada token"| anchors
    evaluator -->|"símbolo → anchor"| anchors
    evaluator -->|"selector cascade"| resolution
    evaluator -->|"expand macro / serialize"| sexpr
    evaluator -->|"check/next/return"| read_ops
    evaluator -->|"create/assert/ingest"| write_ops
    read_ops -->|"queries"| sldb_bridge
    read_ops -->|"related/common/also"| kgdb_bridge
    write_ops -->|"writes"| sldb_bridge
    write_ops -->|"produces"| write_models
    anchors -->|"AnchorDoc"| sldb_bridge
    sldb_bridge -->|"capa librería"| sldb_lib
    kgdb_bridge -->|"uses"| kgdb_lib
    sldb_bridge -->|"persists"| store
    kgdb_bridge -->|"graph snapshot"| store
    sldb_bridge -->|"documentos markdown"| workspace
    projector -->|"reindexes"| sldb_lib
    projector -->|"rebuilds_graph"| kgdb_lib
    docs_gen -->|"AST de docstrings _cmd_*"| cli
    docs_gen -->|"create_doc / model_names"| sldb_bridge
    docs_gen -->|"CliCommandDoc/SurfaceDoc"| workspace
```

## Objetivo · componentes

Pron pide por dirección, recorre aristas y escribe documentos. No resuelve, no filtra, no declara verbos. Los sustantivos son st.{Modelo+}.doc.campo más un predicado; los verbos transitivos son los modelos de relación de kgdb (RelationTypeDoc, RelationDoc), que sldb almacena como documentos y el ingest de kgdb ensambla; los verbos de acción son docs create, fields update y refrescar.

- El léxico sale de los modelos: nombre, campos con descripción, tags, familias ({Modelo+}). Los RelationTypeDoc dan los verbos transitivos con sus tipos válidos. Los AnchorDoc son alias, no la fuente.
- Un sustantivo es una dirección más un predicado, y eso lo responde sldb (ls, get, glob, find, --where). Pron no tiene cascada de resolución propia.
- Los modelos de relación son de kgdb: RelationTypeDoc declara el verbo con sus tipos válidos y su eje, RelationDoc es una arista autorada. Pron los registra en su store al declarar el mundo; sldb los guarda como documentos; el ingest de kgdb los vuelve aristas. kgdb sigue siendo derivado y de solo lectura.
- El ingest de kgdb tiene que tomar los RelationDoc además del semantic-export. Hoy assemble_authored_graph existe en kgdb pero no está en su CLI ni corre en el proyector de pron, por eso el grafo de pron no tiene ninguna arista de dominio.
- Una transición no se dispara en kgdb. Es una escritura en sldb, arista más campo de estado, seguida de un refresh que reensambla el grafo.
- El kernel son los verbos de acción y cada uno es una operación de sldb que ya existe: docs create, fields update y append, docs untrack, stores update.
- La declaración del mundo es store_index.yaml: modelos registrados, stores enlazados, predicados. La proyección es la parte de eso que una sesión puede nombrar.
- El por qué se lee de las aristas del eje WHY, HOW y PROVENANCE que los predicados del store le dan a cada verbo, más el ledger.
- Los sustantivos del mundo de pron son sus propios modelos: átomo, comando, superficie, anchor. Hoy los átomos están tipados con el AtomDoc de deskops y hay trece modelos de deskops registrados sin documentos; los dos salen, deskops es otra instancia sobre el núcleo, no la fuente de los modelos de pron.

```mermaid
graph TD
    subgraph afuera ["Fuera de pron"]
        hablante["Quien habla · persona, LLM u otro producto"]
    end
    subgraph pron ["pron · el SHRDLU"]
        superficie["Superficie · oración → (alcance, predicado) para sustantivos · (verbo, sujeto, objeto) para verbos · respuesta en natural"]
        proyeccion["Proyección · qué stores, modelos, tipos de relación y alias puede nombrar esta sesión"]
        dialogo["Diálogo · pendiente (¿cuál?) y referentes (ese, la anterior)"]
        kernel["Kernel · verbos de acción · crear doc · cambiar campo · escribir arista · refrescar"]
        embeddings["Embeddings · palabra sin calce → cercanos por descripciones de modelos y campos"]
        ledger["Ledger · oración + direcciones + verbo + resultado · el por qué se lee de las aristas del eje WHY/HOW"]
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
        reltypes["RelationTypeDoc · VERBOS TRANSITIVOS · modelo de kgdb · name, source_types, target_types, eje del predicado (HOW, WHY, WHAT, PROVENANCE)"]
        relinst["RelationDoc · una arista autorada · modelo de kgdb, guardada como documento en sldb · source, target, relation_type, condition_ref"]
        ingest["kgdb ingest · nodos y tags desde semantic-export · aristas desde los RelationDoc · integridad referencial"]
        snapshot["GraphSnapshot · nodos = documentos · aristas = tags, contención y relaciones autoradas"]
        traversal["edges_from · edges_to · scope · ¿existe la arista? · ¿legal desde aquí?"]
    end
    hablante -->|"una oración"| superficie
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
    superficie -->|"verbo transitivo leído · ¿quién implementa X? · ¿legal desde aquí?"| traversal
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

## Objetivo · tres turnos

Tres oraciones, una por tipo de palabra. Un verbo transitivo leído (¿qué implementa X?), uno afirmado (X implementa Y, que se escribe como RelationDoc) y un verbo de acción (cambiar la sinopsis de un comando, que es un fields update). Las tres salidas del grounding se muestran sobre el primer turno.

- La superficie no resuelve el sustantivo: arma find st.{Modelo+} --where y sldb devuelve una dirección, dos (ambiguo) o ninguna (missing).
- Verificar que el verbo aplica es leer source_types y target_types del RelationTypeDoc, el modelo de kgdb, por dirección en sldb. Verificar que la arista existe o es legal desde aquí es kgdb.
- Afirmar un verbo transitivo es docs create de un RelationDoc, el modelo de relación de kgdb guardado en sldb. kgdb nunca recibe una orden; su ingest reensambla y la arista aparece.
- Un verbo de acción es una escritura de sldb: fields update re-renderiza el markdown, valida el roundtrip y actualiza la cascada de hashes.
- Missing consulta embeddings sobre las descripciones de modelos y campos, registra el hueco y termina el turno. Ambiguo abre una pendiente; la próxima oración entra como respuesta.
- El por qué combina el ledger (quién, cuándo, con qué oración) con las aristas del eje WHY y PROVENANCE.
- Todos los sustantivos son del mundo de pron: st.{Atom+} es su modelo de átomo, no el AtomDoc de deskops, y el comando es un CliCommandDoc de la KB de pron.

```mermaid
sequenceDiagram
    actor hablante
    participant superficie
    participant dialogo
    participant proyeccion
    participant embeddings
    participant sldb_addr
    participant sldb_write
    participant kgdb
    participant kernel
    participant proyector
    participant ledger
    hablante->>superficie: ¿qué implementa el átomo de bridges?
    superficie->>dialogo: referentes · ninguno
    superficie->>proyeccion: ¿átomo, implementa están en la proyección?
    proyeccion->>superficie: átomo → st.{Atom} · implementa → RelationTypeDoc implements de kgdb (eje HOW)
    superficie->>embeddings: [missing] 'bridges' sin calce → cercanos por descripciones
    superficie->>ledger: [missing] registrar el hueco y los cercanos
    superficie->>hablante: [missing] no existe · ¿querías Y o Z?
    superficie->>sldb_addr: find st.{Atom+} --where 'doc ~ "bridges"'
    sldb_addr->>superficie: [ambiguo] dos direcciones
    superficie->>dialogo: [ambiguo] guardar candidatos y la oración con hueco
    superficie->>hablante: [ambiguo] ¿cuál? A o B
    sldb_addr->>superficie: [único] st.{Atom}.atom-bridges-are-the-only-doors
    superficie->>kgdb: edges_from(sldb://document/Atom:atom-bridges..., implements)
    kgdb->>superficie: targets · sldb://model/SldbBridge, sldb://model/KgdbBridge
    superficie->>ledger: oración · dirección · verbo · aristas
    superficie->>hablante: Implementa SldbBridge y KgdbBridge.
    hablante->>superficie: ese átomo también implementa el proyector
    superficie->>dialogo: ese átomo → la dirección del turno anterior
    superficie->>sldb_addr: find st.{SurfaceDoc+} --where 'doc ~ "proyector"'
    sldb_addr->>superficie: st.{SurfaceDoc}.surface-pron-infra-projector
    superficie->>sldb_addr: get st.{RelationTypeDoc}.implements · source_types, target_types
    sldb_addr->>superficie: Atom → SurfaceDoc · aplica
    superficie->>kernel: escribir arista implements A → B
    kernel->>sldb_write: docs create --model RelationDoc · source_id, target_id, relation_type
    sldb_write->>kernel: tracked · hashes actualizados
    kernel->>proyector: refrescar
    proyector->>kgdb: kgdb ingest · nodos desde semantic-export · aristas desde los RelationDoc
    kgdb->>proyector: snapshot nuevo · la arista existe
    superficie->>ledger: oración · direcciones · RelationDoc escrito
    superficie->>hablante: Listo. Queda registrado.
    hablante->>superficie: cambia la sinopsis del comando repl a: bucle interactivo sobre el evaluador
    superficie->>proyeccion: cambiar → verbo de acción · sinopsis → campo synopsis de CliCommandDoc
    superficie->>sldb_addr: find st.{CliCommandDoc+} --where 'command_path = "repl"'
    sldb_addr->>superficie: st.{CliCommandDoc}.cmd-pron-repl
    superficie->>kernel: cambiar campo
    kernel->>sldb_write: fields update docs/cmd-pron-repl/synopsis '"bucle interactivo sobre el evaluador"'
    sldb_write->>kernel: re-renderizado · roundtrip ok · hashes
    kernel->>proyector: refrescar
    superficie->>ledger: oración · dirección · campo · valor anterior y nuevo
    superficie->>hablante: Hecho.
    hablante->>superficie: ¿por qué dice eso?
    superficie->>ledger: leer el último movimiento sobre esa dirección
    ledger->>superficie: oración · dirección · campo · quién · cuándo
    superficie->>kgdb: edges_from(cmd-pron-repl, eje WHY / PROVENANCE)
    kgdb->>superficie: grounded_by → el docstring de _cmd_repl
    superficie->>hablante: la traza en natural
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
