FILE:desk/tasks/task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y.md
---
sldb:
  by: agent
  at: '2026-11-17T03:01:35Z'
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

p0 (precondiciones, antes de tocar nada): (a) cd /mnt/ssd/proyectos/SLDB_1/pron; git status --porcelain -- .sldb .github CHANGELOG.md desk no imprime nada. El coordinador commitea en master el TaskDoc, sus recibos de desk/reviews/ y el resto de desk/ y .sldb/ antes de despachar, así que el árbol parte limpio. Si imprime algo, el ejecutor para y lo reporta sin tocar nada. (b) El venv /dev/shm/pron-venv pasa la comprobación /dev/shm/pron-venv/bin/python -c "import pron, sldb; print(pron.__file__, sldb.__file__)" si sale con rc 0 e imprime rutas bajo /mnt/ssd/proyectos/SLDB_1/pron/src y /mnt/ssd/proyectos/SLDB_1/sldb/src. Si no pasa, el ejecutor hace rm -rf /dev/shm/pron-venv y lo recrea con estos dos comandos: uv venv -p 3.12 /dev/shm/pron-venv y VIRTUAL_ENV=/dev/shm/pron-venv uv pip install -e /mnt/ssd/proyectos/SLDB_1/sldb -e '/mnt/ssd/proyectos/SLDB_1/pron[dev,mcp]'. Los extras dev y mcp son de pron; sldb va sin extras. p1, desde /mnt/ssd/proyectos/SLDB_1/pron: TMPDIR=/dev/shm /dev/shm/pron-venv/bin/sldb stores add ../deskops/.sldb --name deskops --replace (actualiza .sldb/core/store_index.yaml) y después TMPDIR=/dev/shm /dev/shm/pron-venv/bin/sldb stores declare --write (reescribe .sldb/store.yaml desde el índice). El coordinador lo probó el 2026-11-17 en una copia de HEAD: los dos comandos cambian solo .sldb/store.yaml y .sldb/core/store_index.yaml, y diff -rq no mostró ningún otro archivo de .sldb/, models/*.yaml incluidos. Cualquier otro archivo modificado es un desvío: el ejecutor para y lo reporta. p2: en .github/workflows/check.yml, después del paso 'Install' y antes de 'check (lints + typecheck + tests + docs)', agregar el paso: '- name: deskops next to pron' con el comentario '# .sldb/store.yaml links deskops as ../deskops/.sldb (sibling checkout)' y 'run: git clone --depth 1 https://github.com/jpcosec/opsys.git ../deskops'. En GitHub Actions, actions/checkout deja pron en $GITHUB_WORKSPACE (/home/runner/work/pron/pron) y los run arrancan ahí, así que ../deskops queda en /home/runner/work/pron/deskops: la misma posición relativa que usa el enlace. p3: viñeta al final de la lista de viñetas bajo '## Sin publicar' de CHANGELOG.md (sección en la línea 3; la siguiente, '## 1.0.0 — 2026-09-10', está en la línea 19): '- El store de pron enlaza deskops como repo hermano (../deskops/.sldb) en vez de la ruta de robocop2 ../../../herramientas/deskops/.sldb; el check de CI clona jpcosec/opsys en ../deskops. Pedido de sldb (job store de su CI).' p4: correr Validation en orden y dejar la evidencia en el run dir.

## Validation

_List the checks required before this task can close._

- V1: cd /mnt/ssd/proyectos/SLDB_1/pron && TMPDIR=/dev/shm /dev/shm/pron-venv/bin/sldb stores list | grep -F 'deskops -> ../deskops/.sldb'   # pasa si grep sale con rc 0 (la línea hoy se ve como '- deskops -> ../../../herramientas/deskops/.sldb')
- V2: grep -n 'herramientas/deskops' .sldb/store.yaml .sldb/core/store_index.yaml   # no imprime nada; rc 1 de grep es lo esperado. Se busca 'herramientas/deskops' y no 'herramientas' a secas porque store_index.yaml conserva, fuera de alcance, 'path: /mnt/ssd/herramientas/sldb/src/sldb/models/rule_doc.py' (un modelo de paquete de sldb; lo atiende sldb)
- V3: /dev/shm/pron-venv/bin/python -c "from pathlib import Path; from sldb.store.model_origin import linked_store; p = linked_store(Path('.sldb').resolve(), 'deskops'); print(p); assert p == Path('/mnt/ssd/proyectos/SLDB_1/deskops/.sldb')"   # rc 0 en el checkout real de robocop2
- V4 (layout del CI de sldb, caché fría): W=/dev/shm/pron-link-ci; rm -rf $W; mkdir -p $W/pron; rsync -a --exclude .git --exclude .sldb_cache /mnt/ssd/proyectos/SLDB_1/pron/ $W/pron/; git clone -q --depth 1 https://github.com/jpcosec/opsys.git $W/deskops; cd $W/pron && PATH=/dev/shm/pron-venv/bin:$PATH TMPDIR=/dev/shm make world PYTHON=python   # rc 0. make world no corre tests: el target world del Makefile (Makefile:29-32; el ejecutor puede leerlo con sed -n 29,32p Makefile) es exactamente: 'test -f .sldb/core/store_index.yaml || sldb stores init', '$(PYTHON) -m pron.cli.main init --world . --pythonpath . --knowledge > /dev/null' y '$(PYTHON) -m pron.cli.main docs --world . --pythonpath .' (sldb stores init si falta el índice, pron init --world --knowledge y pron docs), así que las fallas de tests fuera de alcance no lo afectan (tarda más de 10 minutos: correrlo con timeout de 40 min o en segundo plano); desde $W/pron, ../../../herramientas resuelve a /herramientas, que no existe, así que la ruta vieja no puede colarse
- V5: en el mismo $W/pron, PATH=/dev/shm/pron-venv/bin:$PATH TMPDIR=/dev/shm python -m pron.cli.main docs --world . --pythonpath .   # rc 0, sin 'No store_index.yaml'
- V6 (control): repetir V4 tal cual pero con W=/dev/shm/pron-link-ci-control y, antes de make world, copiar sobre la copia los dos archivos de HEAD: git -C /mnt/ssd/proyectos/SLDB_1/pron show HEAD:.sldb/store.yaml > $W/pron/.sldb/store.yaml y lo mismo con .sldb/core/store_index.yaml; make world (o pron docs, V5, si make world pasa) falla con 'No store_index.yaml at' y una ruta que contiene herramientas/deskops/.sldb
- V7: /dev/shm/pron-venv/bin/python -c "import yaml; w = yaml.safe_load(open('.github/workflows/check.yml')); s = [x.get('name') for x in w['jobs']['check']['steps']]; i = s.index('deskops next to pron'); assert s[i-1] == 'Install' and s[i+1].startswith('check'), s"   # rc 0
- V8: git diff --stat HEAD -- . ':!runs' lista solo .sldb/store.yaml, .sldb/core/store_index.yaml, .github/workflows/check.yml y CHANGELOG.md; git diff HEAD -- .sldb/store.yaml cambia solo la línea path del enlace deskops, y git diff HEAD -- .sldb/core/store_index.yaml solo esa línea path y la de store_hash. El árbol parte limpio en esas rutas: lo comprueba p0(a). Cualquier otro cambio es un hallazgo: el ejecutor para y lo reporta

## Done When

_Name the observable condition that makes the task complete._

Ejecutor: V1-V8 pasan, con la evidencia en el run dir, y quedan modificados solo los cuatro archivos de Files. Coordinador, tras el closeout: commit en master de pron pusheado y nota a sldb con el hash.

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

FILE:.sldb/core/store_index.yaml
stores:
- name: deskops
  path: ../../../herramientas/deskops/.sldb
models:
- name: RelationTypeDoc
  model_ref: sldb.models.relation_type_doc:RelationTypeDoc
  path: /home/jp/proyectos/SLDB_1/sldb/src/sldb/models/relation_type_doc.py
  models_index: .sldb/core/models/RelationTypeDoc.yaml
  version: 1
  canonical: false
  family: relation
  semantics:
  - layer.topology
  - representation.markdown
  - source.document.markdown
  - type.relation.type
- name: RelationDoc
  model_ref: sldb.models.relation_doc:RelationDoc
  path: /home/jp/proyectos/SLDB_1/sldb/src/sldb/models/relation_doc.py
  models_index: .sldb/core/models/RelationDoc.yaml
  version: 1
  canonical: false
  family: relation
  semantics:
  - layer.topology
  - representation.markdown
  - source.document.markdown
  - type.relation.instance
- name: AnchorDoc
  model_ref: pron.models:AnchorDoc
  path: src/pron/models/anchor.py
  models_index: .sldb/core/models/AnchorDoc.yaml
  version: 1
  canonical: false
  family: knowledge
  semantics:
  - representation.markdown
  - source.document.markdown
  - type.knowledge.anchor
  - workspace.knowledge.anchors
- name: ProjectionDoc
  model_ref: pron.models:ProjectionDoc
  path: src/pron/models/projection.py
  models_index: .sldb/core/models/ProjectionDoc.yaml
  version: 1
  canonical: false
  family: knowledge
  semantics:
  - representation.markdown
  - source.document.markdown
  - type.knowledge.projection
  - workspace.knowledge.projections
- name: MoveDoc
  model_ref: pron.models:MoveDoc
  path: src/pron/models/move.py
  models_index: .sldb/core/models/MoveDoc.yaml
  version: 1
  canonical: false
  family: ledger
  semantics:
  - representation.markdown
  - source.document.markdown
  - type.pron.move
  - workspace.knowledge.ledger
- name: TheoremDoc
  model_ref: pron.models:TheoremDoc
  path: src/pron/models/theorem.py
  models_index: .sldb/core/models/TheoremDoc.yaml
  version: 1
  canonical: false
  family: knowledge
  semantics:
  - representation.markdown
  - source.document.markdown
  - type.knowledge.theorem
  - workspace.knowledge.theorems
- name: SpecDoc
  model_ref: pron.models:SpecDoc
  path: src/pron/models/spec.py
  models_index: .sldb/core/models/SpecDoc.yaml
  version: 1
  canonical: false
  family: knowledge
  semantics:
  - representation.markdown
  - source.document.markdown
  - type.knowledge.spec
  - workspace.source.spec
- name: CliCommandDoc
  model_ref: sldb.models.knowledge_surface:CliCommandDoc
  path: /home/jp/proyectos/SLDB_1/sldb/src/sldb/models/cli_command_doc.py
  models_index: .sldb/core/models/CliCommandDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics:
  - representation.markdown
  - source.document.markdown
  - type.knowledge.cli_command
  - workspace.knowledge.commands
- name: SurfaceDoc
  model_ref: sldb.models.knowledge_surface:SurfaceDoc
  path: /home/jp/proyectos/SLDB_1/sldb/src/sldb/models/surface_doc.py
  models_index: .sldb/core/models/SurfaceDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics:
  - representation.markdown
  - source.document.markdown
  - type.knowledge.surface
  - workspace.knowledge.surfaces
- name: ExplanationDoc
  model_ref: pron.models:ExplanationDoc
  path: src/pron/models/explanation.py
  models_index: .sldb/core/models/ExplanationDoc.yaml
  version: 1
  canonical: false
  family: knowledge
  semantics:
  - representation.markdown
  - source.document.markdown
  - type.knowledge.explanation
  - workspace.knowledge.explanations
- name: ReadmeDoc
  model_ref: pron.models:ReadmeDoc
  path: src/pron/models/readme.py
  models_index: .sldb/core/models/ReadmeDoc.yaml
  version: 1
  canonical: false
  family: knowledge
  semantics:
  - representation.markdown
  - source.document.markdown
  - type.knowledge.readme
  - workspace.knowledge
- name: CrossroadDoc
  model_ref: deskops.models:CrossroadDoc
  path: ''
  models_index: .sldb/core/models/CrossroadDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: AtomDoc
  model_ref: deskops.models:AtomDoc
  path: ''
  models_index: .sldb/core/models/AtomDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: BoardDoc
  model_ref: deskops.models:BoardDoc
  path: ''
  models_index: .sldb/core/models/BoardDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: DeskFAQDoc
  model_ref: deskops.models:DeskFAQDoc
  path: ''
  models_index: .sldb/core/models/DeskFAQDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: InboxNoteDoc
  model_ref: deskops.models:InboxNoteDoc
  path: ''
  models_index: .sldb/core/models/InboxNoteDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: MaterializationContractDoc
  model_ref: deskops.models:MaterializationContractDoc
  path: ''
  models_index: .sldb/core/models/MaterializationContractDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: PillDoc
  model_ref: deskops.models:PillDoc
  path: ''
  models_index: .sldb/core/models/PillDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: ProtoAtomDoc
  model_ref: deskops.models:ProtoAtomDoc
  path: ''
  models_index: .sldb/core/models/ProtoAtomDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: RepositoryDoc
  model_ref: deskops.models:RepositoryDoc
  path: ''
  models_index: .sldb/core/models/RepositoryDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: ReviewDoc
  model_ref: deskops.models:ReviewDoc
  path: ''
  models_index: .sldb/core/models/ReviewDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: RitualDoc
  model_ref: deskops.models:RitualDoc
  path: ''
  models_index: .sldb/core/models/RitualDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: RoleDoc
  model_ref: deskops.models:RoleDoc
  path: ''
  models_index: .sldb/core/models/RoleDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: RunDoc
  model_ref: deskops.models:RunDoc
  path: ''
  models_index: .sldb/core/models/RunDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: RuntimeProfileDoc
  model_ref: deskops.models:RuntimeProfileDoc
  path: ''
  models_index: .sldb/core/models/RuntimeProfileDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: StepDoc
  model_ref: deskops.models:StepDoc
  path: ''
  models_index: .sldb/core/models/StepDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: TaskAggregateDoc
  model_ref: deskops.models:TaskAggregateDoc
  path: ''
  models_index: .sldb/core/models/TaskAggregateDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: TaskCodeDoc
  model_ref: deskops.models:TaskCodeDoc
  path: ''
  models_index: .sldb/core/models/TaskCodeDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: TaskDebugDoc
  model_ref: deskops.models:TaskDebugDoc
  path: ''
  models_index: .sldb/core/models/TaskDebugDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: TaskDecisionDoc
  model_ref: deskops.models:TaskDecisionDoc
  path: ''
  models_index: .sldb/core/models/TaskDecisionDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: TaskDoc
  model_ref: deskops.models:TaskDoc
  path: ''
  models_index: .sldb/core/models/TaskDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: TaskDocsDoc
  model_ref: deskops.models:TaskDocsDoc
  path: ''
  models_index: .sldb/core/models/TaskDocsDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: TaskExternalDoc
  model_ref: deskops.models:TaskExternalDoc
  path: ''
  models_index: .sldb/core/models/TaskExternalDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: TaskRefactorDoc
  model_ref: deskops.models:TaskRefactorDoc
  path: ''
  models_index: .sldb/core/models/TaskRefactorDoc.yaml
  version: 1
  canonical: false
  family: null
  semantics: []
  origin: deskops
- name: RuleDoc
  model_ref: sldb.models.rule_doc:RuleDoc
  path: /mnt/ssd/herramientas/sldb/src/sldb/models/rule_doc.py
  models_index: .sldb/core/models/RuleDoc.yaml
  version: 1
  canonical: false
  family: rule
  semantics:
  - layer.governance
  - representation.markdown
  - source.document.markdown
  - type.rule
predicates:
- name: is_solved_by
  axis: HOW
  description: Identifies how the source is solved.
- name: implements
  axis: HOW
  description: Identifies what the source implements.
- name: mathematically_proves
  axis: WHY
  description: Provides a mathematical proof.
- name: explains_failure_of
  axis: WHY
  description: Explains why the target fails.
- name: grounded_by
  axis: PROVENANCE
  description: Identifies supporting provenance.
- name: restricts
  axis: WHEN_WHERE
  description: Restricts the target context.
- name: defines
  axis: WHAT
  description: Defines the target concept.
- name: has_model
  axis: WHAT
  description: 'The store registers this model: its own, or one it inherits from the
    linked store that owns it.'
- name: links_to
  axis: WHERE
  description: 'The store links that store under an alias (`stores add`): it reads
    its documents and inherits its models.'
- name: has_document
  axis: WHAT
  description: The model has this document as an instance.
- name: has_section
  axis: WHERE
  description: The document contains this section.
- name: tagged_as
  axis: WHAT
  description: The model, document or section carries this semantic tag.
- name: semantic_parent
  axis: WHAT
  description: This tag is a child of that tag in the semantic DAG.
- name: semantic_equivalent
  axis: WHAT
  description: This local tag maps to that global tag across linked stores.
- name: has_field
  axis: WHAT
  description: The model declares this field; the field node carries its type and
    description.
- name: extends
  axis: WHAT
  description: The model inherits from that model (base_models); instances of the
    source are instances of the target.
- name: applies_to_source
  axis: WHAT
  description: 'Instances of this model may be the source of edges of this relation
    type: the verbs a class can be subject of.'
- name: applies_to_target
  axis: WHAT
  description: Instances of this model may be the target of edges of this relation
    type.
- name: names
  axis: WHAT
  description: The anchor (an alias word) names this model, field, relation type or
    document.
- name: references
  axis: WHAT
  description: A field the model declared in `__references__` holds this document's
    id; the edge carries the field name.
- name: contains
  axis: WHERE
  description: A field the model declared in `__containment__` holds this document
    as a child; the edge carries the field name and the models the declaration allows.
- name: composes
  axis: WHAT
  description: A composed field of the source (`__compositions__`) renders this document's
    payload into the source's text; the edge carries the composed field, the field
    holding the refs and the ref as authored.
store_hash: ea1dd7e7004bba1568a5037146f5f4b74cfb36695f4386c82dcaac284a781d40

FILE:.github/workflows/check.yml
name: check

on:
  push:
    branches: [master]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - name: Install
        # sldb comes from main: there are no releases until the whole suite is ready, and
        # pron follows the sldb the rest of the suite runs on.
        run: |
          python -m pip install "structuredLanguageDB @ git+https://github.com/jpcosec/sldb@main"
          python -m pip install -e ".[dev,mcp]"
      - name: check (lints + typecheck + tests + docs)
        run: make check

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
- El store de sldb de pron se versiona (.sldb/store.yaml y .sldb/core/), como en el resto de los repos; su caché .sldb_cache/ sigue ignorada (decisión de JP del 2026-11-16).

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
Cold-bundle de la tarea task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y: con el TaskDoc, los rituales enrutados por el Board, las pills ligadas, los átomos ligados y los archivos que el TaskDoc nombra, reformula el encargo, lista ambigüedades con cita textual del input y da el DRY-RUN sin ejecutar nada. No ejecutes nada.

Sección de validación del TaskDoc:
- V1: cd /mnt/ssd/proyectos/SLDB_1/pron && TMPDIR=/dev/shm /dev/shm/pron-venv/bin/sldb stores list | grep -F 'deskops -> ../deskops/.sldb'   # pasa si grep sale con rc 0 (la línea hoy se ve como '- deskops -> ../../../herramientas/deskops/.sldb')
- V2: grep -n 'herramientas/deskops' .sldb/store.yaml .sldb/core/store_index.yaml   # no imprime nada; rc 1 de grep es lo esperado. Se busca 'herramientas/deskops' y no 'herramientas' a secas porque store_index.yaml conserva, fuera de alcance, 'path: /mnt/ssd/herramientas/sldb/src/sldb/models/rule_doc.py' (un modelo de paquete de sldb; lo atiende sldb)
- V3: /dev/shm/pron-venv/bin/python -c "from pathlib import Path; from sldb.store.model_origin import linked_store; p = linked_store(Path('.sldb').resolve(), 'deskops'); print(p); assert p == Path('/mnt/ssd/proyectos/SLDB_1/deskops/.sldb')"   # rc 0 en el checkout real de robocop2
- V4 (layout del CI de sldb, caché fría): W=/dev/shm/pron-link-ci; rm -rf $W; mkdir -p $W/pron; rsync -a --exclude .git --exclude .sldb_cache /mnt/ssd/proyectos/SLDB_1/pron/ $W/pron/; git clone -q --depth 1 https://github.com/jpcosec/opsys.git $W/deskops; cd $W/pron && PATH=/dev/shm/pron-venv/bin:$PATH TMPDIR=/dev/shm make world PYTHON=python   # rc 0. make world no corre tests: el target world del Makefile (Makefile:29-32; el ejecutor puede leerlo con sed -n 29,32p Makefile) es exactamente: 'test -f .sldb/core/store_index.yaml || sldb stores init', '$(PYTHON) -m pron.cli.main init --world . --pythonpath . --knowledge > /dev/null' y '$(PYTHON) -m pron.cli.main docs --world . --pythonpath .' (sldb stores init si falta el índice, pron init --world --knowledge y pron docs), así que las fallas de tests fuera de alcance no lo afectan (tarda más de 10 minutos: correrlo con timeout de 40 min o en segundo plano); desde $W/pron, ../../../herramientas resuelve a /herramientas, que no existe, así que la ruta vieja no puede colarse
- V5: en el mismo $W/pron, PATH=/dev/shm/pron-venv/bin:$PATH TMPDIR=/dev/shm python -m pron.cli.main docs --world . --pythonpath .   # rc 0, sin 'No store_index.yaml'
- V6 (control): repetir V4 tal cual pero con W=/dev/shm/pron-link-ci-control y, antes de make world, copiar sobre la copia los dos archivos de HEAD: git -C /mnt/ssd/proyectos/SLDB_1/pron show HEAD:.sldb/store.yaml > $W/pron/.sldb/store.yaml y lo mismo con .sldb/core/store_index.yaml; make world (o pron docs, V5, si make world pasa) falla con 'No store_index.yaml at' y una ruta que contiene herramientas/deskops/.sldb
- V7: /dev/shm/pron-venv/bin/python -c "import yaml; w = yaml.safe_load(open('.github/workflows/check.yml')); s = [x.get('name') for x in w['jobs']['check']['steps']]; i = s.index('deskops next to pron'); assert s[i-1] == 'Install' and s[i+1].startswith('check'), s"   # rc 0
- V8: git diff --stat HEAD -- . ':!runs' lista solo .sldb/store.yaml, .sldb/core/store_index.yaml, .github/workflows/check.yml y CHANGELOG.md; git diff HEAD -- .sldb/store.yaml cambia solo la línea path del enlace deskops, y git diff HEAD -- .sldb/core/store_index.yaml solo esa línea path y la de store_hash. El árbol parte limpio en esas rutas: lo comprueba p0(a). Cualquier otro cambio es un hallazgo: el ejecutor para y lo reporta

