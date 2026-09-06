# KNOWLEDGE CODE STANDARD — Cómo se escribirá el código

## Estado
Capa 4. El código se escribe al final, cuando no quede ambigüedad en core,
usability y components. Este spec fija las reglas para ese momento.

## Regla madre

El código materializa los specs; no decide diseño. Si al implementar aparece
una decisión no cubierta, se detiene el código y se resuelve primero como
atom/spec (documentar → luego codear). Esto operacionaliza
`atom-clean-code-reduces-knowledge-drift`.

## Estructura

```
src/knowledge/
  core/
    sexpr.py          # parser + serializer de s-expressions (sin deps)
    anchors.py        # anchor_registry + AnchorDoc lookup
    resolution.py     # noun_resolver: Resolved | Ambiguous | Missing
    session.py        # estado de clarificación persistido
    evaluator.py      # eval de Meaning: dispatch por anchor kind
    results.py        # tipos: OperationResult, SemanticError, refs
  ops/
    read.py           # check, next, return
    write.py          # assert, create, ingest (con provenance)
  bridges/
    sldb_bridge.py    # única importación de sldb
    kgdb_bridge.py    # única importación de kgdb
  infra/
    projector.py      # model add / project
  cli/
    surface.py        # tokenizer + desugarer
    render.py         # JSON/text + refs
    main.py           # entry point
```

Un archivo = un componente del spec de components. Un componente = un motivo.

## Contratos de código

- Tipos de resultado (`Resolved/Ambiguous/Missing/SemanticError`) son
  dataclasses/pydantic con campos fijos; jamás excepciones para control de
  flujo. Excepciones solo para bugs.
- Cada función pública lleva docstring de una línea con su motivo (el mismo
  motive del anchor/componente que implementa).
- `bridges/` son los únicos módulos que importan sldb/kgdb. Import de sldb
  fuera de bridges = defecto de revisión.
- Sin estado global; la session es un archivo explícito.
- `sexpr.py` no depende de nada del proyecto (es el kernel puro).

## Práctica (domain:code_craft aplicado)

- `practice:clean_code`: módulos pequeños, nombres descriptivos, cero
  comentarios narrativos que dupliquen atoms.
- `practice:patterns`: los shapes de components.md son obligatorios; no crear
  variantes ad hoc.
- `practice:testing`: por componente, tests de contrato (unit) + un test de
  UX por comando canónico (surface → JSON esperado). Los dos ejemplos
  canónicos (`next task --summary`, `user juanito check preferences`) son
  tests de aceptación desde el día uno.
- `practice:linting_mechanical`: ruff + mypy estrictos antes de commit.
- `practice:traceability`: cada módulo nuevo referencia su atom/componente en
  el docstring de cabecera; cada commit toca código y docs juntos.

## Definition of done por componente

1. Contrato del spec implementado sin extensiones no documentadas.
2. Tests de contrato en verde.
3. Atom(s) del componente actualizados: `impl:pending` → `impl:here`.
4. CliCommandDoc/SurfaceDoc regenerados desde el argparse real.
5. `sldb stores check` = PASS tras trackear docs nuevos.

## Señal de alarma

Si el código necesita un if que el spec no explica, el spec estaba ambiguo:
volver a la capa de documentación. El objetivo es que escribir el código sea
lo de menos.
