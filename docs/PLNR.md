# plnr · metas entre las formas y los stores

## Qué es esto

Una forma con cabeza `goal` no la resuelve pron: la **prueba el mundo**, con reglas que el
mundo declara como documentos suyos (`TheoremDoc`). Dentro de una meta hay combinadores
—`and`, `or`, `not`, `find`, `bind`, `use`— y hojas que son lecturas del mundo (`is`,
`where`, `field`, `edge`, `compare`) o aserciones pendientes (`assert-doc`, `assert-field`,
`assert-edge`).

La búsqueda corre entera sobre un **overlay**: lee sldb y kgdb y no escribe nada. Lo que
afirma queda pendiente, y solo cuando el plan entero cierra lo escribe el **kernel**, con
los mismos verbos, permisos, coerción y roundtrip que una oración — un refresh al final y un
`MoveDoc` como cualquier movimiento. Retroceder es no leer la rama que falló: no hay trail
ni rollback porque nunca se comparte estado.

Es el recorte de MicroPlanner (`THGOAL`, `THCONSE`, `THANTE`, `THUSE`, `THFIND`, `TIMID`)
aplicado a un store que no está en memoria y que no tiene transacciones.

## Dónde vive

| qué | dónde | rama | HEAD |
|---|---|---|---|
| el motor | `/home/jp/proyectos/pron-plnr` | `plnr` | `cf76404` |
| la integración en pron | `/home/jp/proyectos/_worktrees/plnr/pron` | `plnr-integration` | `27a97d0` |

El motor se instala editable, como sldb y kgdb: `pip install -e /home/jp/proyectos/pron-plnr`.
La rama de integración sale de `5a9aaed`; `master` la pasó por 15 commits después, así que
al mergear mirar `world_init.py` (`PRON_MODELS`) y los snapshots dorados, que es donde toca.

## Qué se agregó a pron

| archivo | qué hace |
|---|---|
| `src/pron/models/theorem.py` | `TheoremDoc`: nombre, `kind` (`consequent`/`antecedent`), `pattern` y `body` como formas en texto, motivo. Registrado en `PRON_MODELS`, así que todo mundo lo tiene y entra a `hash_mundo`. |
| `src/pron/plnr/pron_world.py` | `plnr.World` sobre sldb y kgdb: `docs`/`payload`/`matches` con `store.docs_of`, `payload`, `matches`; `edges` con `Verbs.edges_from/to` (kgdb, o los RelationDoc con grafo viejo). Cada lectura queda en `record["queries"]`. Acepta el nombre corto de un documento, no solo el export id. |
| `src/pron/plnr/theorem_load.py` | Los `TheoremDoc` del mundo, leídos en orden de declaración. |
| `src/pron/plnr/commit.py` | Las escrituras pendientes, por los verbos del kernel. Un `create` se lleva sus campos al payload; un nombre corto se vuelve export id con el modelo que declaró su propia creación. |
| `src/pron/plnr/plan_planning.py` | La fase que busca: lo que no cierra es `missing`, lo mal formado es `error`, y nada se ejecuta. Deja el plan, su traza y sus queries en el `MoveDoc`. |
| `src/pron/plnr/plan_execution.py` | La fase que escribe: commit por el kernel y el texto de la respuesta. |
| `src/pron/sexpr/forms/goal_form.py` | `(goal PATRÓN …)` como una forma más. |
| `planner.py`, `executor.py`, `form_registry.py`, `syntax.py`, `render_said.py` | Una línea cada uno: el `kind` `plan`, la fase de planificación, la ejecución y cómo se escribe la forma de vuelta. |

Los capítulos 01, 03 y 13 de `source/spec/` dicen lo que hay: `TheoremDoc`, las reglas, y el
lenguaje de metas con la invocación por CLI.

## Una regla

```yaml
- name: transition-guarded
  kind: consequent
  pattern: "(transition ?doc ?field ?machine ?from ?to)"
  body: |
    (goal (field ?doc ?field ?from))
    (goal (state-of ?machine ?from ?src))
    (goal (state-of ?machine ?to ?tgt))
    (goal (edge transitions_to ?src ?tgt))
    (goal (guard ?src ?tgt ?condition))
    (goal (compare != ?condition ""))
    (goal (where ?doc ?condition))
  motive: Una transición cuya arista trae condición, y la condición se cumple.
```

Una transición de estado deja de ser un caso del motor: es una regla del mundo. Ningún nombre
de ningún mundo aparece en `src/plnr` — un test lo verifica (`tests/test_rules.py`).

## Cómo se usa

```bash
pron eval --world MUNDO --pythonpath PYTHONPATH '(goal (free ?t))'
pron eval --world MUNDO --pythonpath PYTHONPATH '(goal (find all ?a (goal (atoms-with-axis how ?a))))' --trace
```

Las reglas de un mundo se escriben como `TheoremDoc` bajo `knowledge/theorems/`. El ejemplo
con el que se probó todo esto es `examples/cobranza.theorems.yaml` del motor.

## Qué se probó

- **266 tests** en la rama de integración (239 de base + 27 nuevos): lecturas por regla,
  encadenamiento, transiciones con y sin guard, un `book` compuesto que crea y afirma, una
  regla `antecedent` que dispara con la aserción, nombres cortos y ausentes, predicados que
  sldb rechaza, y una meta leída con el grafo viejo. `make lint`, `format-check`, `typecheck`
  y `docs-check` verdes.
- **La KB real de un agente** (`AgentsKBs/knowledge_antonia-cobranza`, copiada a /tmp: 14
  `DomainAtom`, 13 `RuleAtom`, 4 `ToolAtom`, 54 RelationDoc con `grounded_by`, `uses_tool` y
  un flujo de pasos con `transitions_to`), con 10 reglas propias. Salieron, entre otras:

  | meta | qué devolvió |
  |---|---|
  | `(answer-about why ?t ?a)` | "Cómo reconocer que este mensaje es real" + su respuesta |
  | `(answer-of atom-cobranza-pago ?t ?a)` | "Cómo se paga la factura" + su respuesta |
  | `(atoms-with-axis how ?a)` | los 4 átomos de eje `how` |
  | `(grounded-answers …respuesta ?a ?answer)` | 5 átomos que sostienen ese paso: arista → payload |
  | `(step-tools …reenviar ?tool ?t)` | "Tool enviar template de WhatsApp" |
  | `(reach …respuesta ?to)` | pagada, reenviar, texto-libre, despedida (y el ciclo del flujo) |

  Las dos primeras son las preguntas que la nota del `HANDOFF` del 2026-09-17 deja como
  límite de `say`: fallan en el léxico porque "pay" no es palabra del mundo. Con metas salen,
  porque leen campos y aristas, no un léxico cerrado.

## Lo que la KB rompió, y quedó arreglado

1. **El símbolo del anfitrión.** `plnr` solo reconocía su propia clase `Sym`; pron tiene la
   suya. Ahora un símbolo es cualquier subclase de `str` que no sea `str`, así que un literal
   sigue siendo literal y las formas pasan sin conversión.
2. **Aristas invertidas.** El adaptador emitía `(relación, extremo, otro)` sin importar la
   dirección: leer hacia atrás devolvía source y target cambiados y `free` decía que todas las
   mesas lo estaban. Lo cazó un test.
3. **Nombres cortos.** La KB nombra `atom-cobranza-pago`; el adaptador exigía
   `DomainAtom:atom-cobranza-pago` y dejaba escapar un `ValueError` crudo. Ahora resuelve el
   nombre contra el índice del store, una vez, cacheado.
4. **Una búsqueda que revienta no es una respuesta.** `plnr.WorldError` (con `absent=True`
   cuando el nombre no está) y `Plan.failure` = `none | malformed | budget | world | absent`:
   un nombre que no está es `missing` —un sustantivo que no resolvió—, y un store que se
   niega (un predicado que sldb no entiende) es `error`.
5. **`find` con su variable.** `(find all ?s (goal …))` con `?s` que no ocurre en la meta
   ligaba `?s` a una lista que se contiene a sí misma y volaba la pila. Ahora `unify` no liga
   una variable a una forma que la contiene, y `find` rechaza la variable que no ocurre.

## Pendiente, y por qué

- **`naming`.** El plan nombra el documento; la regla de `naming` del mundo no se usa. Falta
  que el commit remapee el nombre del plan al que eligió el mundo y reescriba las
  referencias posteriores.
- **Coerción y permisos durante la búsqueda.** Hoy los aplica el commit: un plan puede
  encontrarse y ser rechazado al escribir. La forma limpia son dos primitivas del anfitrión
  —`(coerces MODELO CAMPO ?valor)`, `(allowed ?verbo)`— que el motor deja pasar pero no
  conoce.
- **`state_machine.py` sigue siendo código.** La ruta de reglas funciona en paralelo (el test
  de `transition-guarded` la prueba sobre el mundo del restaurante), pero nadie mudó el
  original a `TheoremDoc`. Mudarlo toca los capítulos 03 y 10 y los snapshots.
