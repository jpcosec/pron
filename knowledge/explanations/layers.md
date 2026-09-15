# Capas

## Question

¿Qué capas tiene pron?

## Answer

| capa | qué hace | dónde |
|---|---|---|
| mundo | abre un store, lee su declaración, refresca su grafo | `world.py`, `store.py`, `graph.py` |
| léxico | deriva las palabras del store y las corta por la proyección | `lexicon.py`, `embedder.py` |
| superficie | clasifica, arma frases nominales, interpreta construcciones fijas | `surface/` |
| sustantivos | dirección + predicados → sldb | `resolve.py` |
| verbos | lee aristas, verifica contra el `RelationTypeDoc`, afirma, transiciones | `verbs.py` |
| kernel | las escrituras de sldb, con guardas y deshacer | `kernel.py` |
| diálogo y ledger | la pendiente, los referentes, el `MoveDoc` por turno | `dialogue.py`, `ledger.py` |
| sesión | el turno entero | `session.py` |

## Sources
