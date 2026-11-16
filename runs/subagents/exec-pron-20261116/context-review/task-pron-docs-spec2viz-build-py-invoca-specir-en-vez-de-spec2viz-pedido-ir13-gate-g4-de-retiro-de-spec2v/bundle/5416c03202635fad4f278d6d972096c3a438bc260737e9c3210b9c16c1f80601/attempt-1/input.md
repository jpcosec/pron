FILE:desk/tasks/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v.md
---
sldb:
  by: agent
  at: '2026-11-16T05:25:57Z'
  authority: generated
  via: save_document_payload
id: task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v
status: active
summary: ''
tags:
- workspace:desk
- artifact:task
- host:robocop2
current_node: ritual-testing
history:
- task_activates
references:
- desk/inbox/20261115-224816-suggestion-ir13-pide-pasar-docs-spec2viz-build-py-de-pron-de-spec2viz-a-specir.md
- ../IR/docs/spec2viz/correspondencia-cli.md
- ../IR/docs/spec2viz/acta-de-retiro.md
depends_on: []
pills: []
files:
- docs/spec2viz/build.py
- docs/spec2viz/README.md
- docs/spec2viz/specs/target.components.yml
- CHANGELOG.md
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# pron docs/spec2viz/build.py invoca specir en vez de spec2viz (pedido IR13, gate G4 de retiro de spec2viz)

## Rationale

_Explain why this task exists or the business driver behind it._

IR13 (repo IR, gate de retiro de spec2viz) pide a pron migrar su única dependencia de spec2viz: las tres llamadas run('spec2viz', ...) de docs/spec2viz/build.py líneas 22, 23 y 24. Mientras estén, la fila de pron en IR/docs/spec2viz/acta-de-retiro.md (línea 53) queda "pendiente" y spec2viz no se puede retirar. specIR (repo IR, script `specir`) ofrece los mismos comandos con las mismas opciones (IR/docs/spec2viz/correspondencia-cli.md filas SV-K16, SV-K13 y SV-K04). Origen: nota del inbox desk/inbox/20261115-224816-suggestion-ir13-pide-pasar-docs-spec2viz-build-py-de-pron-de-spec2viz-a-specir.md.

## Goal

_Describe the concrete result this task must produce._

docs/spec2viz/build.py llama a `specir diagram validate`, `specir diagram render` y `specir catalog build` con los mismos argumentos que hoy pasa a spec2viz, `python3 docs/spec2viz/build.py` termina con rc 0 sin spec2viz en el camino, y IR recibe por deskops message send el hash del commit que lo resuelve.

## Scope

_State what is in scope and what is out of scope._

Entra: docs/spec2viz/build.py (los tres run() de las líneas 22-24, los docstrings de las líneas 1 y 30, y los argumentos de mmdc de la línea 46: '-w' pasa a '--size' por mermaid-cli 12), docs/spec2viz/README.md (líneas 14 y 20-25), docs/spec2viz/specs/target.components.yml (solo entrecomillar los label de las líneas 121 y 128), CHANGELOG.md, instalar specir en la máquina como herramienta de uv, y la respuesta a IR con el commit. No entra: renombrar el directorio docs/spec2viz, sus specs o catalog.yml, ni cambiar otro contenido de los specs; regenerar y commitear las salidas (docs/spec2viz/out/, index.html, offline.html y diagrams.md están en .gitignore); instalar o cambiar mermaid-cli; tocar el repo IR, spec2viz o sldb; desinstalar spec2viz; la mención de spec2viz de la línea 5 del README; la política de .gitignore de .sldb/ (otra tarea).

## Implementation Path

_Outline the expected implementation route or affected surface._

Dos binarios de specir con papeles distintos: build.py llama a 'specir' del PATH, que es la herramienta uv que instala p1; la comprobación de retiro usa /mnt/ssd/proyectos/SLDB_1/IR/.venv/bin/specir, que ya existe en robocop2 (verificado el 2026-11-16) y no se toca. Las líneas citadas son las de master al crear la tarea; si cambiaron, ubicar cada cambio por el texto citado. p1: instalar specir en el PATH con el sldb de la instalación única de la máquina (no el de PyPI: structuredlanguagedb 0.1.13 no exporta SpecView y specir falla con ImportError, visto el 2026-11-16): 'uv tool install --reinstall --editable /mnt/ssd/proyectos/SLDB_1/IR --with-editable /home/robocop/herramientas/sldb' (reemplaza la instalación rota que haya; /home/robocop/herramientas/sldb es el checkout de origin/main de sldb y no se toca). Comprobar que 'specir diagram validate --help', 'specir diagram render --help' (acepta --backend y --out) y 'specir catalog build --help' (acepta --config y --out) salen con rc 0; si alguno falla, parar y reportar sin tocar pron. p2: en docs/spec2viz/build.py cambiar solo el primer argumento 'spec2viz' por 'specir' en las tres llamadas run('spec2viz', ...) de main() (líneas 22, 23 y 24: diagram validate, diagram render, catalog build); el resto de los argumentos y export_views no cambian. Docstring del módulo (línea 1), texto exacto: """Rebuild the specIR catalog and portable SVG views from semantic YAML.""" ; docstring de export_views (línea 30), texto exacto: """Export a specIR catalog with pre-rendered Mermaid to portable views.""". p3: en docs/spec2viz/README.md, en la frase de requisitos 'Desde este directorio, con spec2viz, mmdc, Python y PyYAML disponibles' (línea 14) y en el bloque 'Comandos principales del CLI de spec2viz' con sus tres comandos (líneas 20-25), reemplazar el comando spec2viz por specir y 'CLI de spec2viz' por 'CLI de specIR'; el nombre del directorio docs/spec2viz y el resto del README no cambian. p3b: arreglos que build.py necesita para llegar a rc 0 y que ya fallaban en master con spec2viz (verificado el 2026-11-16): (i) en docs/spec2viz/specs/target.components.yml entrecomillar dos label de aristas que, sin comillas, el flow mapping de YAML corta en la coma: 'label: verbo de acción, o verbo transitivo afirmado}' (línea 121) pasa a 'label: "verbo de acción, o verbo transitivo afirmado"}' y 'label: nodos, tags, contención}' (línea 128) pasa a 'label: "nodos, tags, contención"}'; nada más del spec cambia. (ii) en docs/spec2viz/build.py, en la llamada a mmdc de export_views (línea 46), cambiar los argumentos '-w', '1800' por '--size', '1800': mermaid-cli 12.2 (la instalación de la máquina, /mnt/ssd/herramientas/mermaid-cli) ya no acepta -w. build.py llama a 'mmdc' del PATH; en robocop2 es el envoltorio /mnt/ssd/herramientas/mermaid-cli/mmdc (Chrome headless), que se antepone al PATH solo al correr la validación. p4: agregar en CHANGELOG.md, al final de la lista bajo '## Sin publicar', con el mismo formato de viñeta: '- docs/spec2viz/build.py valida, renderiza y arma el catálogo con specir en vez de spec2viz (pedido IR13 del gate de retiro de spec2viz).' p5: correr las tres comprobaciones de Validation, en ese orden, sobre el árbol de trabajo antes de commitear (la de retiro lee los archivos en disco); con las tres en verde, commit de build.py, README.md y CHANGELOG.md en master y push a origin. p6: deskops message send --root . --to IR --title 'pron: IR13 resuelto' '<hash del commit de p5>: docs/spec2viz/build.py usa specir (líneas 22-24)'.

## Validation

_List the checks required before this task can close._

- grep -nE "run\('spec2viz'" docs/spec2viz/build.py   # sin salida: ninguna llamada run() con spec2viz como comando
- cd docs/spec2viz && PATH=/mnt/ssd/herramientas/mermaid-cli:$PATH TMPDIR=/dev/shm python3 build.py   # rc 0; imprime 'Generated 4 SVGs, diagrams.md and offline.html'
- cd /mnt/ssd/proyectos/SLDB_1/IR && .venv/bin/specir retirement check --path graph_ui=../UIs/graph_ui --path deskops=../deskops --path pron=../pron --path sldb=../sldb --path spec2viz/.sldb=../spec2viz/.sldb | grep -P '^\s*pron\t'   # sin salida (el rc global sigue en 1 por otros repos)

## Done When

_Name the observable condition that makes the task complete._

grep -nE "run\('spec2viz'" docs/spec2viz/build.py vacío; python3 docs/spec2viz/build.py rc 0 con specir; specir retirement check no lista filas de pron; commit en master de pron pusheado; mensaje a IR enviado con ese hash.

FILE:desk/rituals/phase.md
---
id: ritual-phase
steps: []
tags:
- workspace:desk
---

# Phase ritual for dependency-layer execution

Run one horizontal layer of pron-repair tasks whose prerequisites are satisfied and whose
planned changes do not overlap, then close the layer with integration validation,
pill reconciliation, and next-phase preparation.

Each task in the phase still closes with its own validation and its own commit;
the phase adds the pass that only makes sense once those tasks are integrated.

FILE:desk/rituals/execution.md
---
id: ritual-execution
steps: []
tags:
- workspace:desk
---

# Execution ritual

Review the board, bind the relevant pills, keep scope tight, and implement only the active task for pron-repair.

FILE:desk/rituals/testing.md
---
id: ritual-testing
steps: []
tags:
- workspace:desk
---

# Testing ritual

Run the smallest relevant validation first, then broaden coverage when pron-repair changes shared behavior.

FILE:desk/rituals/closeout.md
---
id: ritual-closeout
steps: []
tags:
- workspace:desk
---

# Closeout ritual

Close a pron-repair task only after validation passes, any durable knowledge from bound pills is linked to an atom when needed, the board is updated, and the final change is ready to commit.

FILE:docs/spec2viz/build.py
"""Rebuild the specIR catalog and portable SVG views from semantic YAML."""
from pathlib import Path
import argparse
import base64
import html
import subprocess
import yaml

ROOT = Path(__file__).resolve().parent


def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exports-only', action='store_true', help='Reuse existing Mermaid and HTML outputs')
    args = parser.parse_args()
    specs = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'specs').glob('*.yml'))
    if not args.exports_only:
        run('specir', 'diagram', 'validate', *specs)
        run('specir', 'diagram', 'render', *specs, '--backend', 'mermaid', '--out', 'out/mermaid')
        run('specir', 'catalog', 'build', '--config', 'catalog.yml', '--out', 'index.html')

    export_views(ROOT)


def export_views(root):
    """Export a specIR catalog with pre-rendered Mermaid to portable views."""
    catalog = yaml.safe_load((root / 'catalog.yml').read_text())['diagram_store']
    items = catalog['items']
    title_text = catalog.get('title', 'pron')
    subtitle = catalog.get('brand_subtitle', 'Vistas derivadas del código fuente.')
    title_html = html.escape(title_text)
    subtitle_html = html.escape(subtitle)
    svg_dir = root / 'out/svg'
    svg_dir.mkdir(parents=True, exist_ok=True)
    markdown = [f'# {title_text}', '', subtitle, '']
    cards = []
    nav = []
    for item in items:
        ident = item['id']
        title = item['title']
        svg = f'out/svg/{Path(item["mmd"]).stem}.svg'
        subprocess.run(['mmdc', '-i', item['mmd'], '-o', svg, '-t', 'neutral', '-b', 'white', '-w', '1800', '-q'], cwd=root, check=True)
        notes = '\n'.join(f'- {note}' for note in item['notes'])
        mermaid = (root / item['mmd']).read_text()
        markdown.extend([f'## {title}', '', item['desc'], '', notes, '', f'```mermaid\n{mermaid}\n```', ''])
        esc = html.escape
        nav.append(f'<a href="#{ident}">{esc(item["nav"])}</a>')
        encoded_svg = base64.b64encode((root / svg).read_bytes()).decode('ascii')
        inline_svg = f'<img src="data:image/svg+xml;base64,{encoded_svg}" alt="{esc(title)}">'
        cards.append(f'<section id="{ident}"><h2>{esc(title)}</h2><p>{esc(item["desc"])}</p>'
                     f'<div class="diagram">{inline_svg}</div><ul>' +
                     ''.join(f'<li>{esc(note)}</li>' for note in item['notes']) +
                     f'</ul><p><a href="{svg}">Abrir SVG</a> · '
                     f'<a href="{item["specs"][0]}">YAML semántico</a></p></section>')
    (root / 'diagrams.md').write_text('\n'.join(markdown))
    page = '''<!doctype html><html lang="es"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CATALOG_TITLE</title>
<style>
*{box-sizing:border-box}body{margin:0;font:16px/1.6 system-ui,sans-serif;color:#182839;background:#eef2f6}
nav{position:fixed;inset:0 auto 0 0;width:270px;padding:24px;background:#142638;color:#fff;overflow:auto}
nav a{display:block;color:#dce8f5;text-decoration:none;padding:8px 0;font-size:14px}
main{margin-left:270px;padding:36px;max-width:1800px}h1{line-height:1.15;font-size:36px}
section{background:white;padding:28px;margin:24px 0;border:1px solid #d9e1e8;border-radius:12px;scroll-margin-top:20px}
h2{margin:0;font-size:24px}a{color:#175ca1}.diagram{overflow:auto;padding:20px 0}
.diagram img{display:block;margin:auto;max-width:100%;height:auto}li{margin:8px 0;color:#46566a}
@media(max-width:900px){nav{position:static;width:auto}main{margin:0;padding:18px}}
@media print{nav{display:none}main{margin:0;padding:0}section{break-before:page;border:0}.diagram{overflow:visible}}
</style><nav><strong>CATALOG_TITLE</strong>''' + ''.join(nav) + f'''</nav>
<main><h1>{title_html}</h1><p>{len(items)} vistas · SVG integrados · lectura sin conexión</p>
<p>{subtitle_html}</p>''' + ''.join(cards) + '</main></html>'
    (root / 'offline.html').write_text(page.replace('CATALOG_TITLE', title_html))
    print(f'Generated {len(items)} SVGs, diagrams.md and offline.html')


if __name__ == '__main__':
    main()

FILE:docs/spec2viz/README.md
# pron — Diagramas de arquitectura

Vistas de `pron`: la arquitectura objetivo, proyección gráfica de [`source/spec`](../../source/spec/README.md) (`target.*.yml`), y las capas reales de código (`codigo.capas.yml`, mapeo de la tabla "Capas" de [`../../README.md`](../../README.md)). Cuando el spec o el código cambien, se edita el `specs/*.yml` correspondiente y se regenera todo con `build.py`; no se editan los archivos de `out/` ni los HTML directamente. La vista de la arquitectura v1 está en la rama `v1-code-and-kb`.

- [Catálogo navegable de spec2viz](index.html): filtros, navegación y herramientas del visor nativo. Carga Mermaid desde el CDN configurado por spec2viz.
- [Visor sin conexión](offline.html): el SVG está integrado en un único HTML, sin dependencias de red.
- [Diagrama en Markdown](diagrams.md): Mermaid y notas de lectura.
- [SVG](out/svg/): archivo para abrir o compartir.

## Fuentes y regeneración

`specs/*.yml` son las fuentes semánticas de los diagramas. `catalog.yml` contiene sus descripciones y notas de interpretación. Los archivos de `out/`, los HTML y `diagrams.md` son generados y no se versionan: los enlaces de arriba existen después de correr `python build.py`.

Desde este directorio, con `specir`, `mmdc`, Python y PyYAML disponibles:

```bash
python build.py
```

Comandos principales del CLI de specIR:

```bash
specir diagram validate specs/*.yml
specir diagram render specs/*.yml --backend mermaid --out out/mermaid
specir catalog build --config catalog.yml --out index.html
```

`python build.py --exports-only` regenera SVG, Markdown y visor sin conexión a partir del Mermaid ya producido.

## Agregar una vista nueva

1. Escribir `specs/<nombre>.yml` (tipo `component`, `class`, `sequence`, `state`, `activity`, `deployment` o `component_view_matrix` según corresponda).
2. Agregar un `item` en `catalog.yml` con su `id`, `desc`, `nav`, `specs` y `notes`.
3. Correr `python build.py`.

FILE:docs/spec2viz/specs/target.components.yml
id: pron.target.components
title: pron — arquitectura objetivo · componentes
type: component
version: '3.0'
metadata:
  description: >
    Pron es un SHRDLU sobre el mundo que sldb y kgdb ya reparten. Los
    sustantivos son documentos de sldb y se nombran por dirección
    (st.{Modelo+}.doc.campo más un predicado). Los verbos transitivos son los
    modelos de relación de kgdb (RelationTypeDoc declara el verbo, RelationDoc
    es una arista autorada); sldb los almacena como documentos y el ingest de
    kgdb los ensambla en el grafo. Los verbos de acción son las escrituras de
    sldb (crear doc, cambiar campo, refrescar). El léxico sale de los modelos:
    nombre, campos con descripción, tags, familias; los AnchorDoc son alias.
    Pron no resuelve, no filtra y no declara verbos: registra los modelos de
    kgdb en su mundo, pide por dirección, recorre aristas y escribe documentos.
style:
  theme: default
data:
  nodes:
    afuera:
      label: Fuera de pron
      kind: boundary
      contains: [hablante, editor]
    hablante:
      label: Quien habla · persona, LLM u otro producto
      kind: actor
    editor:
      label: "Editor · sldb serve (/schema, /graph, POST /save) + graph_ui · formularios desde el esquema, relaciones como RelationDoc"
      kind: actor
    pron:
      label: pron · el SHRDLU
      kind: layer
      contains: [superficie, proyeccion, dialogo, kernel, embeddings, ledger, proyector]
    superficie:
      label: "Superficie · oración → (alcance, predicado) para sustantivos · (verbo, sujeto, objeto) para verbos · respuesta en natural"
      kind: surface
    proyeccion:
      label: "Proyección · ProjectionDoc · stores, modelos, relaciones con modo read / assert, acciones, alias, naming, display, key"
      kind: core
    dialogo:
      label: "Diálogo · pendiente (¿cuál?) y referentes (ese, la anterior)"
      kind: core
    kernel:
      label: "Kernel · verbos de acción · crear · cambiar · agregar · limpiar · quitar · olvidar · refrescar · lee antes de escribir · reevalúa condiciones"
      kind: core
    embeddings:
      label: "Embeddings · palabra sin calce → cercanos por descripciones de modelos y campos"
      kind: infra
    ledger:
      label: "Ledger · MoveDoc por turno · interpretación, consultas, escritura, hash_mundo antes y después · movimientos externos detectados"
      kind: infra
    proyector:
      label: "Proyector · stores update · semantic-export · kgdb ingest"
      kind: infra
    mundo:
      label: Mundo · sldb · los sustantivos · almacena todo documento, incluidas las relaciones de kgdb
      kind: boundary
      contains: [store_index, modelos, anchors, docs]
    store_index:
      label: "store_index.yaml · la declaración del mundo · modelos registrados (los de contenido y los de relación de kgdb) · stores enlazados · predicados"
      kind: config
    modelos:
      label: "Modelos de contenido · SUSTANTIVOS · nombre, campos con descripción, tags, familia"
      kind: external
    anchors:
      label: "AnchorDoc · alias y motivos · solo lo que no coincide con un modelo, campo o tag"
      kind: external
    docs:
      label: "Documentos · los objetos del mundo · markdown reversible"
      kind: external
    superficies:
      label: Superficies de sldb · lo que pron usa, no reimplementa
      kind: layer
      contains: [addr, writes, export]
    addr:
      label: "Direcciones · st.{Modelo+}.doc.campo.sub · se.tag · gse.tag · --where · ls, get, glob, find"
      kind: bridge
    writes:
      label: "Escrituras · docs create / untrack · fields update, append, clean · re-renderiza, valida roundtrip, cascada de hashes"
      kind: bridge
    export:
      label: "semantic-export · modelos, documentos, secciones, tags, DAG"
      kind: bridge
    grafo:
      label: kgdb · dueño de los verbos transitivos · el grafo es derivado y de solo lectura
      kind: boundary
      contains: [reltypes, relinst, ingest, snapshot, traversal]
    reltypes:
      label: "RelationTypeDoc · VERBOS TRANSITIVOS · modelo de kgdb · name, source_types, target_types, cardinality, condition, eje del predicado"
      kind: external
    relinst:
      label: "RelationDoc · una arista autorada · modelo de kgdb, guardada como documento en sldb · source_id, target_id, relation_type, condition"
      kind: external
    ingest:
      label: "kgdb ingest · nodos desde semantic-export · nodos relation_type · aristas desde los RelationDoc y los links con predicado · excluye el ledger · hash_mundo · integridad como error"
      kind: external
    snapshot:
      label: "GraphSnapshot · nodos = documentos · aristas = tags, contención y relaciones autoradas"
      kind: external
    traversal:
      label: "edges_from · edges_to · ¿existe la arista? · cada arista trae origin y condition"
      kind: external
  edges:
    - {from: hablante, to: superficie, relation: dice, label: una oración}
    - {from: editor, to: writes, relation: uses, label: "POST /save · misma save_payload"}
    - {from: superficie, to: ledger, relation: registra, label: "movimiento externo si hash_mundo cambió sin pron"}
    - {from: superficie, to: dialogo, relation: resuelve, label: referentes}
    - {from: superficie, to: proyeccion, relation: verifica, label: cada palabra está en la proyección}
    - {from: proyeccion, to: store_index, relation: reads, label: qué mundo}
    - {from: proyeccion, to: modelos, relation: reads, label: "léxico de sustantivos · nombres, campos, tags, familias"}
    - {from: store_index, to: reltypes, relation: registers, label: "models add kgdb…:RelationTypeDoc, RelationDoc · el mundo declara qué verbos existen"}
    - {from: proyeccion, to: reltypes, relation: reads, label: léxico de verbos transitivos}
    - {from: proyeccion, to: anchors, relation: reads, label: alias}
    - {from: superficie, to: embeddings, relation: consulta, label: "palabra sin calce → cercanos"}
    - {from: superficie, to: addr, relation: pide, label: "sustantivo = st.{Modelo+} + where · un campo = .campo.sub"}
    - {from: addr, to: docs, relation: reads}
    - {from: superficie, to: reltypes, relation: verifica, label: "¿el verbo aplica al sujeto y al objeto? · source_types, target_types"}
    - {from: superficie, to: traversal, relation: pregunta, label: "verbo transitivo leído · ¿quién implementa X? · ¿existe transitions_to desde el estado actual?"}
    - {from: superficie, to: addr, relation: pide, label: "condición de la arista evaluada por sldb sobre el sujeto · find … --where"}
    - {from: superficie, to: kernel, relation: ejecuta, label: verbo de acción, o verbo transitivo afirmado}
    - {from: kernel, to: writes, relation: uses, label: "crear doc · cambiar campo · escribir RelationDoc"}
    - {from: writes, to: docs, relation: writes, label: re-renderiza y valida}
    - {from: writes, to: relinst, relation: writes, label: "una arista nueva es un documento más del store"}
    - {from: kernel, to: proyector, relation: triggers, label: refrescar tras escribir}
    - {from: proyector, to: export, relation: runs}
    - {from: proyector, to: ingest, relation: runs}
    - {from: export, to: ingest, relation: feeds, label: nodos, tags, contención}
    - {from: relinst, to: ingest, relation: feeds, label: una arista por RelationDoc}
    - {from: ingest, to: snapshot, relation: builds}
    - {from: traversal, to: snapshot, relation: reads}
    - {from: superficie, to: ledger, relation: registra, label: el movimiento entero}
    - {from: ledger, to: traversal, relation: reads, label: "¿por qué? · aristas del eje WHY / HOW"}
    - {from: superficie, to: hablante, relation: responde, label: "resultado · ¿cuál? · no existe, cercanos"}

FILE:CHANGELOG.md
# Changelog

## Sin publicar

- Python 3.12 o superior (`requires-python >=3.12`; ruff `py312`, mypy `3.12`): 3.10 llega a fin
  de vida. La CI corre `make check` en 3.12 y 3.13, con sldb instalado desde `main`.
- `constraints.txt` se retira: fijaba sldb y kgdb a commits que ya no existen, y la CI fallaba en
  ese paso desde la fusión de kgdb en sldb.
- `pron serve --listen HOST:PORT`: el daemon atiende además por TCP, con el mismo
  protocolo, a un cliente que no comparte su sistema de archivos (spec 12 §7).
  `request`, `alive`, `RemoteSession`, `RemoteGraph` y `RemoteWorld` aceptan `HOST:PORT`
  donde iba la ruta del socket; `pron.remote.tcp_address` dice cuál es
  (`tests/remote/test_07_serve_tcp.py`).
- La caché derivada de sldb se lee de `.sldb_cache/` (su `stores migrate-layout`) en los
  tests y en el montaje MCP.
- docs/spec2viz/build.py valida, renderiza y arma el catálogo con specir en vez de spec2viz (pedido IR13 del gate de retiro de spec2viz).

## 1.0.0 — 2026-09-10

First tagged release. pron exists by its own right: SHRDLU over an sldb store whose
nouns are addresses and whose verbs are kgdb relation types plus sldb writes.

### Surface (frozen by spec 12 and `tests/test_12_runtime_surface.py`)

- `Session(world, projection, speaker, speaker_address, now, embedder, read_only, home)`
  and `turn(sentence) -> Response`.
- `pron.response.Response` with five fields: `text`, `outcome`, `trace`, `move_id`, `record`.
- `pron.client`: `socket_path`, `alive`, `request`, `RemoteSession(sock, ...)` with
  `world`/`home` and `payload(model, doc)`, `RemoteGraph`, `RemoteWorld`.
- Socket at `<world>/.pron/serve.sock`; `pron say`, `pron repl` and hosts use it when it
  answers.
- `World.store.payload(model, doc)`; export ids qualified by store (`A:Model:doc`), split
  and joined by `pron.ids` (`split_id`, `join_id`, `store_of`, `scope`, `address_of`).

### Since 1.0.0.dev1

- Composition validation: `$created`-before-`create` prevalidated in both the live and the
  dry-run paths (`tests/test_composition_validation.py`).
- Self-KB hole closed: docs are discovered by walking the package, so every module —
  including `models/*` — is checked to cite a spec chapter.
- Revision lock for sibling dependencies (`constraints.txt`) and CI running `make check`.
- Spec 12 updated to match the shipped signatures; runtime-surface freeze test added.
- Architecture catalog no longer describes the abandoned AtomDoc/deskops models.
- Makefile (`make check`), mypy hardening, dev extras pinned.

FILE:instruccion
Cold-bundle de la tarea task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v: con el TaskDoc, los rituales enrutados por el Board, las pills ligadas, los átomos ligados y los archivos que el TaskDoc nombra, reformula el encargo, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

Sección de validación del TaskDoc:
- grep -nE "run\('spec2viz'" docs/spec2viz/build.py   # sin salida: ninguna llamada run() con spec2viz como comando
- cd docs/spec2viz && PATH=/mnt/ssd/herramientas/mermaid-cli:$PATH TMPDIR=/dev/shm python3 build.py   # rc 0; imprime 'Generated 4 SVGs, diagrams.md and offline.html'
- cd /mnt/ssd/proyectos/SLDB_1/IR && .venv/bin/specir retirement check --path graph_ui=../UIs/graph_ui --path deskops=../deskops --path pron=../pron --path sldb=../sldb --path spec2viz/.sldb=../spec2viz/.sldb | grep -P '^\s*pron\t'   # sin salida (el rc global sigue en 1 por otros repos)

