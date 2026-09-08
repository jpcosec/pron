# Arquitectura de pron

Actual: derivado del código. Objetivo: el SHRDLU sobre el mundo — sustantivos en sldb, verbos en kgdb, el léxico como puente. La diferencia entre ambos es la lista de trabajo.

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

Un SHRDLU montado sobre el mundo tal como los dos stores lo reparten. Sustantivos en sldb (documentos, modelos, recetas, el léxico mismo). Verbos en kgdb (acciones, transiciones, relaciones). Pron no tiene operaciones — las lee del grafo y las interpreta — y lo único que es código es un kernel de cuatro primitivas.

- Los anchors son el léxico. Nombran cosas que ya existen en el mundo, por proyección, con un motivo. No declaran operaciones ni contienen semántica. Su kind se deriva de a qué apuntan — modelo = sustantivo, arista/transición/acción = verbo.
- Lo que un operador puede decir es lo que puede hacer. Una entidad del grafo sin anchor en tu proyección es invisible desde la superficie.
- La pregunta qué puedo hacer con un paso la responde el grafo — las aristas, transiciones y acciones incidentes a ese tipo — y el léxico lo traduce a palabras.
- La superficie traduce comparando la oración con los motivos del léxico (embeddings). Un missing ofrece cercanos por similitud, no solo por texto. Qué pasa después con el hueco no es de pron.
- Las recetas (contexto, seguridad) son documentos del mundo. El anchor solo las nombra.
- El _dispatch con seis verbos fijos en Python es lo que desaparece: los verbos se declaran en kgdb.

```mermaid
graph TD
    subgraph afuera ["Fuera de pron"]
        hablante["Quien habla · persona, LLM u otro producto"]
    end
    subgraph capa0 ["Capa 0 · Mundo"]
        mundo["Declaración del mundo · qué stores y grafo, qué léxico, qué proyecciones"]
    end
    subgraph capa1 ["Capa 1 · Superficie"]
        superficie["Superficie · natural → Meaning · Meaning → natural"]
    end
    subgraph capa2 ["Capa 2 · Meaning"]
        lexico["Léxico · anchors · palabra → entidad del mundo · motivo"]
        proyeccion["Proyección · lo que esta sesión puede nombrar"]
        dialogo["Diálogo · pendiente y referentes (ese, la anterior)"]
        evaluador["Evaluador · grounding · resolución · interpreta verbos del grafo · traza"]
        kernel["Kernel de primitivas · leer doc · escribir doc · recorrer arista · disparar transición"]
    end
    subgraph capa3 ["Capa 3 · Bridges"]
        bridge_sldb["Bridge sldb · documentos, campos, secciones"]
        bridge_kgdb["Bridge kgdb · aristas, transiciones, estados"]
        bridge_emb["Bridge embeddings · oración ↔ motivos · cercanos"]
        bridge_otros["Bridge lo-que-venga · SQL, APIs, ..."]
    end
    subgraph transversal ["Transversal"]
        proyector["Proyector · reindexa · reconstruye grafo · recalcula embeddings"]
        ledger["Ledger · oración + Meaning + refs + motivos + resultado · provenance"]
    end
    subgraph backends ["Backends · el mundo"]
        sldb["sldb · SUSTANTIVOS · documentos, modelos, recetas, el léxico mismo"]
        kgdb["kgdb · VERBOS · acciones, transiciones, relaciones"]
        embeddings["embeddings"]
        otros["SQL · APIs · lo que venga"]
    end
    mundo -->|"carga el léxico"| lexico
    mundo -->|"define"| proyeccion
    mundo -->|"qué puertas existen"| capa3
    hablante -->|"una oración"| superficie
    superficie -->|"referentes"| dialogo
    superficie -->|"oración ↔ motivos del léxico"| bridge_emb
    superficie -->|"cada palabra está en la proyección"| lexico
    proyeccion -->|"acota"| lexico
    lexico -->|"se carga de AnchorDocs"| bridge_sldb
    superficie -->|"un Meaning"| evaluador
    evaluador -->|"palabra → entidad"| lexico
    evaluador -->|"el sustantivo · cascada"| bridge_sldb
    evaluador -->|"el verbo · aplica a este sustantivo · transición legal"| bridge_kgdb
    evaluador -->|"missing → cercanos por similitud"| bridge_emb
    evaluador -->|"pendiente si ambiguo"| dialogo
    evaluador -->|"primitivas"| kernel
    kernel -->|"leer / escribir documento"| bridge_sldb
    kernel -->|"recorrer arista · disparar transición"| bridge_kgdb
    kernel -->|"lo que declaren"| bridge_otros
    kernel -->|"refresca tras escribir"| proyector
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

Desde que entra una oración hasta que sale una respuesta en natural. La superficie compara la oración con los motivos del léxico; el evaluador resuelve el sustantivo en sldb y lee el verbo en kgdb; las tres salidas del grounding — único, ambiguo, missing — y el "¿por qué?" que lee el ledger.

- Los referentes (al usuario, ese, la anterior) se resuelven en el diálogo antes de groundear.
- Sin palabra en la proyección, la oración vuelve desde la superficie sin llegar al evaluador.
- Leer el verbo en kgdb incluye si aplica a este sustantivo y si la transición es legal desde el estado actual.
- Ambiguo abre una pendiente; la próxima oración entra como respuesta. Missing consulta embeddings, registra el hueco y termina el turno.
- El kernel solo ejecuta primitivas; el proyector refresca solo después de una escritura.

```mermaid
sequenceDiagram
    actor hablante
    participant superficie
    participant dialogo
    participant lexico
    participant evaluador
    participant kernel
    participant sldb
    participant kgdb
    participant embeddings
    participant proyector
    participant ledger
    hablante->>superficie: agrega cita al usuario a las 16:00
    superficie->>dialogo: ¿a quién refiere 'al usuario'?
    dialogo->>superficie: el usuario de esta sesión
    superficie->>embeddings: oración ↔ motivos del léxico de esta proyección
    embeddings->>superficie: palabras candidatas por similitud
    superficie->>lexico: ¿cada palabra está en la proyección?
    lexico->>superficie: [sin palabra] 'cita' no está en tu léxico
    superficie->>hablante: [sin palabra] no tengo 'cita' · sí tengo ...
    superficie->>evaluador: Meaning
    evaluador->>lexico: cada palabra → su entidad del mundo
    evaluador->>sldb: resolver el sustantivo · cascada
    evaluador->>kgdb: leer el verbo · ¿aplica a este sustantivo? · ¿transición legal desde aquí?
    evaluador->>dialogo: [ambiguo] guardar candidatos y Meaning con hueco
    evaluador->>superficie: [ambiguo] ¿cuál?
    superficie->>hablante: [ambiguo] ¿cuál? A o B
    evaluador->>embeddings: [missing] cercanos por similitud
    evaluador->>ledger: [missing] registrar el hueco con motivo y cercanos
    evaluador->>superficie: [missing] no existe · cercanos · esto buscaba
    superficie->>hablante: [missing] no existe X · ¿querías Y o Z?
    evaluador->>kernel: [único] escribir documento · disparar transición
    kernel->>sldb: escribir el documento
    sldb->>kernel: ok + refs
    kernel->>kgdb: disparar la transición
    kgdb->>kernel: nuevo estado
    kernel->>proyector: refrescar tras escribir
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
