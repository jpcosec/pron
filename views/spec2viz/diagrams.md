# Arquitectura de pron

Actual: derivado del código. Objetivo: el SHRDLU sobre un mundo declarado. La diferencia entre ambos es la lista de trabajo.

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

Un SHRDLU sobre un mundo declarado. Quien habla es un solo actor externo; una única superficie natural ↔ Meaning; evaluador que grounda contra la gramática viva acotada por la proyección; operaciones abiertas; una puerta por backend; ledger transversal.

- El vocabulario base no tiene palabras de dominio. Las de dominio (regla, paso, herramienta) se declaran por mundo como anchors.
- Un símbolo que no es anchor de la proyección vuelve como pregunta desde la superficie; nunca llega al evaluador.
- Un missing usa el bridge de embeddings para ofrecer cercanos por similitud, no solo por texto. Qué pasa después con el hueco no es de pron.
- El ledger guarda por movimiento la oración, su Meaning, los refs y los motivos. "¿Por qué?" lo lee. La traducción puede ser difusa porque el grounding es estricto.

```mermaid
graph TD
    subgraph afuera ["Fuera de pron"]
        hablante["Quien habla · persona, LLM u otro producto"]
    end
    subgraph capa0 ["Capa 0 · Mundo"]
        mundo["Declaración del mundo · stores, modelos, anchors, proyecciones"]
    end
    subgraph capa1 ["Capa 1 · Superficie"]
        superficie["Superficie · natural → Meaning · Meaning → natural"]
    end
    subgraph capa2 ["Capa 2 · Meaning"]
        gramatica["Gramática viva · anchors · qué hay · qué puedo hacer con X"]
        proyeccion["Proyección · lo que esta sesión ve y puede"]
        dialogo["Diálogo · pendiente y referentes (ese, la anterior)"]
        evaluador["Evaluador · grounding · resolución · expansión · dispatch · traza"]
        operaciones["Operaciones · leer / escribir / operar / declarar · abiertas"]
    end
    subgraph capa3 ["Capa 3 · Bridges"]
        bridge_sldb["Bridge sldb · documentos, campos, secciones"]
        bridge_kgdb["Bridge kgdb · grafo, relaciones, estados"]
        bridge_emb["Bridge embeddings · parecido a · cercanos"]
        bridge_otros["Bridge lo-que-venga · SQL, APIs, ..."]
    end
    subgraph transversal ["Transversal"]
        proyector["Proyector · reindexa · reconstruye grafo · recalcula embeddings"]
        ledger["Ledger · oración + Meaning + refs + motivos + resultado · provenance"]
    end
    subgraph backends ["Backends"]
        sldb["sldb"]
        kgdb["kgdb"]
        embeddings["embeddings"]
        otros["SQL · APIs · lo que venga"]
    end
    mundo -->|"carga los anchors"| gramatica
    mundo -->|"define"| proyeccion
    mundo -->|"qué puertas existen"| capa3
    hablante -->|"una oración"| superficie
    superficie -->|"referentes"| dialogo
    superficie -->|"cada símbolo es anchor"| gramatica
    proyeccion -->|"acota"| gramatica
    superficie -->|"un Meaning"| evaluador
    evaluador -->|"grounds"| gramatica
    evaluador -->|"pendiente si ambiguo"| dialogo
    evaluador -->|"missing → cercanos por similitud"| bridge_emb
    evaluador -->|"dispatches"| operaciones
    operaciones -->|"consulta / escribe"| bridge_sldb
    operaciones -->|"relaciones / opera estados"| bridge_kgdb
    operaciones -->|"parecido a"| bridge_emb
    operaciones -->|"lo que declaren"| bridge_otros
    operaciones -->|"refresca tras escribir"| proyector
    proyector -->|"reindexa · reconstruye · recalcula"| capa3
    bridge_sldb -->|"serves"| sldb
    bridge_kgdb -->|"serves"| kgdb
    bridge_emb -->|"serves"| embeddings
    bridge_otros -->|"serves"| otros
    evaluador -->|"el movimiento entero"| ledger
    ledger -->|"por qué · cómo · de dónde"| evaluador
    evaluador -->|"resultado · ¿cuál? · no existe, cercanos"| superficie
    superficie -->|"en natural"| hablante
```

## Objetivo · un turno

Desde que entra una oración hasta que sale una respuesta en natural, con las tres salidas del grounding — único, ambiguo, missing — y el "¿por qué?" que lee el ledger.

- Los referentes (al usuario, ese, la anterior) se resuelven en el diálogo antes de groundear.
- Ambiguo abre una pendiente; la próxima oración entra como respuesta.
- Missing consulta embeddings para cercanos, registra el hueco y termina el turno.
- El proyector refresca solo después de una escritura.

```mermaid
sequenceDiagram
    actor hablante
    participant superficie
    participant dialogo
    participant gramatica
    participant evaluador
    participant operaciones
    participant bridge
    participant embeddings
    participant proyector
    participant ledger
    hablante->>superficie: agrega cita al usuario a las 16:00
    superficie->>dialogo: ¿a quién refiere 'al usuario'?
    dialogo->>superficie: el usuario de esta sesión
    superficie->>gramatica: ¿cada símbolo es anchor de la proyección?
    gramatica->>superficie: [símbolo sin anchor] 'cita' no es anchor
    superficie->>hablante: [símbolo sin anchor] no tengo 'cita' como palabra · sí tengo ...
    superficie->>evaluador: Meaning
    evaluador->>gramatica: groundar cada símbolo
    evaluador->>dialogo: [ambiguo] guardar candidatos y Meaning con hueco
    evaluador->>superficie: [ambiguo] ¿cuál?
    superficie->>hablante: [ambiguo] ¿cuál? A o B
    evaluador->>embeddings: [missing] cercanos por similitud
    evaluador->>ledger: [missing] registrar el hueco con motivo y cercanos
    evaluador->>superficie: [missing] no existe · cercanos · esto buscaba
    superficie->>hablante: [missing] no existe X · ¿querías Y o Z?
    evaluador->>operaciones: [único] despachar
    operaciones->>bridge: escribir
    bridge->>operaciones: ok + refs
    operaciones->>proyector: refrescar tras escribir
    evaluador->>ledger: oración + Meaning + refs + motivos + resultado
    evaluador->>superficie: resultado + traza
    superficie->>hablante: Listo. Queda registrado.
    hablante->>superficie: ¿por qué?
    superficie->>evaluador: explicar el último movimiento
    evaluador->>ledger: leer la traza
    ledger->>evaluador: oración · Meaning · refs · motivos
    evaluador->>superficie: la traza
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
