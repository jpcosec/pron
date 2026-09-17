# Capas

## Question

¿Qué capas tiene pron?

## Answer

| capa | qué hace | dónde (`src/pron/`) |
|---|---|---|
| primitivas | los datos del turno, el lector de formas, los verbos de acción y el kernel que escribe en sldb con guardas y deshacer | `kernel/` (`parts/`, `sexp/`, `actions/`, `kernel.py`) |
| mundo | abre un store, lee su declaración, refresca su grafo | `world/world.py`, `world/store.py`, `world/graph.py` |
| léxico | deriva las palabras del store y las corta por la proyección | `world/lexicon.py`, `world/matching/` |
| superficie | clasifica, arma frases nominales, interpreta construcciones fijas | `surface/` |
| formas | la forma leída se compila a partes | `sexpr/forms/` |
| sustantivos y verbos | dirección + predicados → sldb; aristas, `RelationTypeDoc`, condiciones, transiciones | `sexpr/resolving/` |
| el movimiento | planificar, prevalidar, ejecutar por tipo de parte | `sexpr/planning/`, `sexpr/prevalidation/`, `sexpr/execution/` |
| diálogo y ledger | la pendiente, los referentes, el `MoveDoc` por turno | `sexpr/dialogue/`, `sexpr/turn/ledger.py` |
| sesión | el turno entero | `session.py`, `sexpr/turn/` |

## Sources
