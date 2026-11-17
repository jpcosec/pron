FILE:desk/tasks/task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y.md
---
sldb:
  by: agent
  at: '2026-11-17T04:21:38Z'
  authority: generated
  via: save_document_payload
id: task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
- host:robocop2
current_node: ritual-execution
history: []
references:
- desk/inbox/20261116-194348-suggestion-pron-sldb-enlaza-deskops-por-una-ruta-de-robocop2-herramientas-deskops-sldb-y-rompe-el-job-store-del-ci-de-sldb.md
- desk/inbox/20261116-195724-suggestion-sldb-track-con-force-re-indexa-make-world-vuelve-a-pasar-pero-el-enlace-a-deskops-no-resuelve-en-ci.md
- .sldb/store.yaml
- .github/workflows/check.yml
- Makefile
depends_on: []
pills: []
files:
- .sldb/store.yaml
- .sldb/core/store_index.yaml
- .github/workflows/check.yml
- CHANGELOG.md
task_type: task.code
inherits_from: []
inherit_acceptance_context: false
atoms: []
---

# pron/.sldb enlaza deskops como repo hermano ../deskops/.sldb en vez de la ruta de robocop2 ../../../herramientas, y el check de pron clona deskops al lado

## Rationale

_Explain why this task exists or the business driver behind it._

Dos notas de sldb del 2026-11-16 (inbox 20261116-194348 y 20261116-195724): pron/.sldb/store.yaml y .sldb/core/store_index.yaml enlazan el store de deskops como 'path: ../../../herramientas/deskops/.sldb'. sldb resuelve una ruta de enlace relativa desde la raíz del proyecto, es decir, la carpeta que contiene .sldb/ (sldb/src/sldb/store/model_origin.py:30, 'root / link.path' con root = project_root). Desde /mnt/ssd/proyectos/SLDB_1/pron esa ruta apunta a /mnt/ssd/herramientas/deskops/.sldb, que existe solo en robocop2. En el job store del CI de sldb (pron en $GITHUB_WORKSPACE/pron y deskops en $GITHUB_WORKSPACE/deskops) 'pron docs' falla con 'No store_index.yaml at .../herramientas/deskops/.sldb' y el job queda en rojo. El repo hermano ../deskops/.sldb existe en robocop2 (/mnt/ssd/proyectos/SLDB_1/deskops/.sldb, con core/store_index.yaml) y en el runner de sldb. La nota proponía '../../deskops/.sldb', pero como la base es la raíz de pron, esa ruta apuntaría a /mnt/ssd/proyectos/deskops, que no existe. El hermano correcto es '../deskops/.sldb'. El CI propio de pron (.github/workflows/check.yml) clona solo pron, así que su paso docs-check (make world) tampoco tendría deskops al lado.

## Goal

_Describe the concrete result this task must produce._

El enlace deskops de pron es '../deskops/.sldb' en .sldb/store.yaml y en .sldb/core/store_index.yaml. Resuelve en robocop2, en un layout como el del CI de sldb (pron y deskops lado a lado, sin /mnt/ssd/herramientas a la vista) y en el CI propio de pron, porque check.yml clona jpcosec/opsys (repo público de deskops) en ../deskops antes de make check.

## Scope

_State what is in scope and what is out of scope._

Entra (ejecutor): (a) re-enlazar con el CLI de sldb, sin editar a mano .sldb/store.yaml ni .sldb/core/store_index.yaml; (b) en .github/workflows/check.yml, un paso nuevo entre 'Install' y 'check (lints + typecheck + tests + docs)'; (c) una viñeta en CHANGELOG.md. No entra: las rutas absolutas de modelos de paquete de sldb dentro de .sldb/core/store_index.yaml (por ejemplo 'path: /home/jp/proyectos/SLDB_1/sldb/src/sldb/models/relation_type_doc.py' y 'path: /mnt/ssd/herramientas/sldb/src/sldb/models/rule_doc.py'): las escribe sldb y son asunto de sldb; el coordinador le manda una nota aparte. Tampoco entran las fallas de tests de pron (goldens test_16, test_04 y test_10, de la tarea task-pron-vuelve-a-verde-…), src/, el Makefile, el CI de sldb, regenerar el mundo en el checkout real ni git add, commit o push: el ejecutor no indexa nada y el cierre es del coordinador. Si sldb stores add o stores declare cambian en store.yaml o store_index.yaml algo más que la línea path del enlace deskops y el campo store_hash de store_index.yaml, el ejecutor para y lo reporta.

## Implementation Path

_Outline the expected implementation route or affected surface._

Reportes: todo 'para y lo reporta' significa dejar de ejecutar, escribir el motivo y la salida que lo muestra en result-summary.md del run dir que da el brief del coordinador, y responder BLOQUEADO: <motivo>. jpcosec/opsys es el repo de GitHub de deskops (remote origin de /mnt/ssd/proyectos/SLDB_1/deskops: https://github.com/jpcosec/opsys.git; público). p0 (precondiciones, antes de tocar nada): (a) cd /mnt/ssd/proyectos/SLDB_1/pron; git status --porcelain -- . ':!runs' no imprime nada (el mismo alcance que V8). El coordinador commitea en master el TaskDoc, sus recibos de desk/reviews/ y el resto de desk/ y .sldb/ antes de despachar, así que el árbol parte limpio. Si imprime algo, el ejecutor para y lo reporta sin tocar nada. (b) El venv /dev/shm/pron-venv pasa la comprobación /dev/shm/pron-venv/bin/python -c "import pron, sldb; print(pron.__file__, sldb.__file__)" si sale con rc 0 e imprime rutas bajo /mnt/ssd/proyectos/SLDB_1/pron/src y /mnt/ssd/proyectos/SLDB_1/sldb/src. Si no pasa, el ejecutor hace rm -rf /dev/shm/pron-venv y lo recrea con estos dos comandos: uv venv -p 3.12 /dev/shm/pron-venv y VIRTUAL_ENV=/dev/shm/pron-venv uv pip install -e /mnt/ssd/proyectos/SLDB_1/sldb -e '/mnt/ssd/proyectos/SLDB_1/pron[dev,mcp]'. Los extras dev y mcp son de pron; sldb va sin extras. p1, desde /mnt/ssd/proyectos/SLDB_1/pron: TMPDIR=/dev/shm /dev/shm/pron-venv/bin/sldb stores add ../deskops/.sldb --name deskops --replace (actualiza .sldb/core/store_index.yaml) y después TMPDIR=/dev/shm /dev/shm/pron-venv/bin/sldb stores declare --write (reescribe .sldb/store.yaml desde el índice). El coordinador lo probó el 2026-11-17 en una copia de HEAD: los dos comandos cambian solo .sldb/store.yaml y .sldb/core/store_index.yaml, y diff -rq no mostró ningún otro archivo de .sldb/, models/*.yaml incluidos. Cualquier otro archivo modificado, o cualquier otra línea cambiada en esos dos (orden, formato u otro campo), es un desvío: el ejecutor para y lo reporta. p2: en .github/workflows/check.yml, después del paso 'Install' y antes de 'check (lints + typecheck + tests + docs)', agregar el paso: '- name: deskops next to pron' con el comentario '# .sldb/store.yaml links deskops as ../deskops/.sldb (sibling checkout)' y 'run: git clone --depth 1 https://github.com/jpcosec/opsys.git ../deskops'. En GitHub Actions, actions/checkout deja pron en $GITHUB_WORKSPACE (/home/runner/work/pron/pron) y los run arrancan ahí, así que ../deskops queda en /home/runner/work/pron/deskops: la misma posición relativa que usa el enlace. p3: viñeta al final de la lista de viñetas bajo '## Sin publicar' de CHANGELOG.md (la sección existe; la viñeta va justo antes del encabezado '## 1.0.0 — 2026-09-10'): '- El store de pron enlaza deskops como repo hermano (../deskops/.sldb) en vez de la ruta de robocop2 ../../../herramientas/deskops/.sldb; el check de CI clona jpcosec/opsys en ../deskops. Pedido de sldb (job store de su CI).' p4: correr Validation en orden y dejar la evidencia en el run dir.

## Validation

_List the checks required before this task can close._

- V1: cd /mnt/ssd/proyectos/SLDB_1/pron && TMPDIR=/dev/shm /dev/shm/pron-venv/bin/sldb stores list | grep -F 'deskops -> ../deskops/.sldb'   # pasa si grep sale con rc 0 (la línea hoy se ve como '- deskops -> ../../../herramientas/deskops/.sldb')
- V2: grep -n 'herramientas/deskops' .sldb/store.yaml .sldb/core/store_index.yaml   # no imprime nada; rc 1 de grep es lo esperado. Se busca 'herramientas/deskops' y no 'herramientas' a secas porque store_index.yaml conserva, fuera de alcance, 'path: /mnt/ssd/herramientas/sldb/src/sldb/models/rule_doc.py' (un modelo de paquete de sldb; lo atiende sldb)
- V3: /dev/shm/pron-venv/bin/python -c "from pathlib import Path; from sldb.store.model_origin import linked_store; p = linked_store(Path('.sldb').resolve(), 'deskops'); print(p); assert p == Path('/mnt/ssd/proyectos/SLDB_1/deskops/.sldb')"   # rc 0 en el checkout real de robocop2
- V4 (layout del CI de sldb, caché fría): W=/dev/shm/pron-link-ci; rm -rf $W; mkdir -p $W/pron; rsync -a --exclude .git --exclude .sldb_cache /mnt/ssd/proyectos/SLDB_1/pron/ $W/pron/; git clone -q --depth 1 https://github.com/jpcosec/opsys.git $W/deskops; cd $W/pron && PATH=/dev/shm/pron-venv/bin:$PATH TMPDIR=/dev/shm make world PYTHON=python   # rc 0. make world no corre tests: el target world del Makefile (Makefile:29-32; el ejecutor lo comprueba con sed -n 29,32p Makefile y, si no coincide con este texto, para y lo reporta) es exactamente: 'test -f .sldb/core/store_index.yaml || sldb stores init', '$(PYTHON) -m pron.cli.main init --world . --pythonpath . --knowledge > /dev/null' y '$(PYTHON) -m pron.cli.main docs --world . --pythonpath .' (sldb stores init si falta el índice, pron init --world --knowledge y pron docs), así que las fallas de tests fuera de alcance no lo afectan (tarda más de 10 minutos: correrlo con timeout de 40 min o en segundo plano); desde $W/pron, ../../../herramientas resuelve a /herramientas, que no existe, así que la ruta vieja no puede colarse
- V5: en el mismo $W/pron, PATH=/dev/shm/pron-venv/bin:$PATH TMPDIR=/dev/shm python -m pron.cli.main docs --world . --pythonpath .   # rc 0, sin 'No store_index.yaml'
- V6 (control): repetir V4 tal cual pero con W=/dev/shm/pron-link-ci-control y, antes de make world, copiar sobre la copia los dos archivos de HEAD: git -C /mnt/ssd/proyectos/SLDB_1/pron show HEAD:.sldb/store.yaml > $W/pron/.sldb/store.yaml y lo mismo con .sldb/core/store_index.yaml. Pasa si make world sale con rc distinto de 0 y su salida contiene 'No store_index.yaml at' seguido de una ruta que contiene herramientas/deskops/.sldb (make world ya incluye pron docs como su tercera línea; no se corre V5 aparte en el control)
- V7: /dev/shm/pron-venv/bin/python -c "import yaml; w = yaml.safe_load(open('.github/workflows/check.yml')); s = [x.get('name') for x in w['jobs']['check']['steps']]; i = s.index('deskops next to pron'); assert s[i-1] == 'Install' and s[i+1].startswith('check'), s"   # rc 0
- V8: git diff --stat HEAD -- . ':!runs' lista solo .sldb/store.yaml, .sldb/core/store_index.yaml, .github/workflows/check.yml y CHANGELOG.md; git diff HEAD -- .sldb/store.yaml cambia solo la línea path del enlace deskops, y git diff HEAD -- .sldb/core/store_index.yaml solo esa línea path y la de store_hash. El árbol parte limpio en esas rutas: lo comprueba p0(a). Cualquier otro cambio es un hallazgo: el ejecutor para y lo reporta

## Done When

_Name the observable condition that makes the task complete._

Ejecutor: V1-V8 pasan, con la evidencia en el run dir, y quedan modificados solo los cuatro archivos de Files. Coordinador, tras el closeout: commit en master de pron pusheado y nota a sldb con el hash.

FILE:instruccion
Preflight solo-TaskDoc de la tarea task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y: reformula el encargo tal como lo leería un ejecutor sin ningún otro contexto, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

