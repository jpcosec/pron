# KNOWLEDGE USABILITY — Cómo se usa el evaluador anclado

## Estado
Capa 2 (después del núcleo `KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md`).

## Principio de usabilidad

El usuario escribe surface; el sistema responde con significado o con diálogo.
Nunca con un stacktrace, nunca con un "unknown flag".

## Gramática surface

Posicional, determinista, sin NLP libre:

```
<expr>     := <noun-first> | <verb-first>
<noun-first> := <noun> [<id>] <verb> [<target>] [--<projection>]
<verb-first> := <verb> <noun> [<id>] [--<projection>]
```

Ambos órdenes desugaran a la misma s-expression. Ejemplos canónicos:

```
next task --summary            → (next (docs task) :project summary)
task next --summary            → (next (docs task) :project summary)
user juanito check preferences → (check (rel preferences (doc user "juanito")))
show atom atom-searchvector    → (check (doc atom "atom-searchvector"))
```

Todo token se resuelve contra la anchor table. El primer token sin anchor
determina el mensaje de error.

## Modo s-expression directo

La capa Meaning es utilizable directamente (power users, scripts, agentes):

```
knowledge eval '(check (rel preferences (doc user "juanito")))'
```

Surface y eval son equivalentes por construcción; surface es solo azúcar.

## Diálogo de clarificación (sesión)

```
> user juanito check preferences
? Ambiguo: ¿'juanito-perez' o 'juanito-soto'?
> juanito-perez
{ "preferences": [ ... ] }
```

Reglas:
- La ambigüedad retorna candidatos y deja la expresión pendiente.
- La siguiente entrada se interpreta primero como clarificación; si no matchea
  ningún candidato, se trata como comando nuevo y se descarta lo pendiente.
- La sesión persiste el estado pendiente entre invocaciones del CLI
  (archivo de sesión), para que el diálogo funcione en terminal.

## Errores semánticos (formato fijo)

Todo error responde tres cosas: qué símbolo falló, qué motivo tiene (o que no
tiene), y qué se puede hacer:

```
> user juanito frobnicate preferences
✗ 'frobnicate' no tiene anchor.
  Motivos conocidos para operaciones: check (leer), next (siguiente), ...
  Declara un anchor: knowledge anchor add frobnicate --kind operation ...
```

```
> user pedro check preferences
✗ No existe doc de 'user' (un humano registrado) con id 'pedro'.
  Cercanos: pedro-rojas, juan-pedro.
```

## Salida

- Default: JSON estructurado (consumible por agentes y pipes).
- `--format text`: proyección legible.
- Toda respuesta de lectura incluye `refs` (paths de los docs/nodos usados)
  para que el resultado sea auditable.

## Descubribilidad

- `knowledge anchors` — lista la gramática viva (símbolo, kind, motive).
- `knowledge anchors <symbol>` — motivo y ref de un símbolo.
- `--help` de cada superficie se deriva de los AnchorDoc/CliCommandDoc, no de
  strings hardcodeados: la ayuda es una proyección del conocimiento.

## Anti-metas

- No autocompletar semántica adivinando (fuzzy solo para sugerir en errores).
- No flags crípticos: toda opción es una projection o un anchor con motive.
- No modos interactivos obligatorios: cada intercambio funciona como comando
  aislado con estado de sesión persistido.
