FILE:desk/tasks/task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y.md
---
sldb:
  by: agent
  at: '2026-11-17T02:08:43Z'
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

p1, desde /mnt/ssd/proyectos/SLDB_1/pron, con el venv /dev/shm/pron-venv (pron y sldb main en modo editable; si falta, el ejecutor lo recrea con: uv venv -p 3.12 /dev/shm/pron-venv && VIRTUAL_ENV=/dev/shm/pron-venv uv pip install -e /mnt/ssd/proyectos/SLDB_1/sldb -e '.[dev,mcp]'): 'TMPDIR=/dev/shm /dev/shm/pron-venv/bin/sldb stores add ../deskops/.sldb --name deskops --replace' (actualiza .sldb/core/store_index.yaml) y después 'TMPDIR=/dev/shm /dev/shm/pron-venv/bin/sldb stores declare --write' (reescribe .sldb/store.yaml desde el índice). p2: en .github/workflows/check.yml, después del paso 'Install' y antes de 'check (lints + typecheck + tests + docs)', agregar el paso: '- name: deskops next to pron' con el comentario '# .sldb/store.yaml links deskops as ../deskops/.sldb (sibling checkout)' y 'run: git clone --depth 1 https://github.com/jpcosec/opsys.git ../deskops'. p3: viñeta al final de la lista bajo '## Sin publicar' de CHANGELOG.md: '- El store de pron enlaza deskops como repo hermano (../deskops/.sldb) en vez de la ruta de robocop2 ../../../herramientas/deskops/.sldb; el check de CI clona jpcosec/opsys en ../deskops. Pedido de sldb (job store de su CI).' p4: correr Validation en orden y dejar la evidencia en el run dir.

## Validation

_List the checks required before this task can close._

- V1: cd /mnt/ssd/proyectos/SLDB_1/pron && TMPDIR=/dev/shm /dev/shm/pron-venv/bin/sldb stores list   # imprime 'deskops -> ../deskops/.sldb'
- V2: grep -n 'herramientas' .sldb/store.yaml .sldb/core/store_index.yaml   # no imprime nada (rc 1 de grep es lo esperado)
- V3: /dev/shm/pron-venv/bin/python -c "from pathlib import Path; from sldb.store.model_origin import linked_store; p = linked_store(Path('.sldb').resolve(), 'deskops'); print(p); assert p == Path('/mnt/ssd/proyectos/SLDB_1/deskops/.sldb')"   # rc 0 en el checkout real de robocop2
- V4 (layout del CI de sldb, caché fría): W=/dev/shm/pron-link-ci; rm -rf $W; mkdir -p $W/pron; rsync -a --exclude .git --exclude .sldb_cache /mnt/ssd/proyectos/SLDB_1/pron/ $W/pron/; git clone -q --depth 1 https://github.com/jpcosec/opsys.git $W/deskops; cd $W/pron && PATH=/dev/shm/pron-venv/bin:$PATH TMPDIR=/dev/shm make world PYTHON=python   # rc 0. make world no corre tests: son las tres líneas del target world del Makefile (sldb stores init si falta el índice, pron init --world --knowledge y pron docs), así que las fallas de tests fuera de alcance no lo afectan (tarda más de 10 minutos: correrlo con timeout de 40 min o en segundo plano); desde $W/pron, ../../../herramientas resuelve a /herramientas, que no existe, así que la ruta vieja no puede colarse
- V5: en el mismo $W/pron, PATH=/dev/shm/pron-venv/bin:$PATH TMPDIR=/dev/shm python -m pron.cli.main docs --world . --pythonpath .   # rc 0, sin 'No store_index.yaml'
- V6 (control): repetir V4 tal cual pero con W=/dev/shm/pron-link-ci-control y, antes de make world, copiar sobre la copia los dos archivos de HEAD: git -C /mnt/ssd/proyectos/SLDB_1/pron show HEAD:.sldb/store.yaml > $W/pron/.sldb/store.yaml y lo mismo con .sldb/core/store_index.yaml; make world (o pron docs, V5, si make world pasa) falla con 'No store_index.yaml at' y una ruta que contiene herramientas/deskops/.sldb
- V7: /dev/shm/pron-venv/bin/python -c "import yaml; w = yaml.safe_load(open('.github/workflows/check.yml')); s = [x.get('name') for x in w['jobs']['check']['steps']]; i = s.index('deskops next to pron'); assert s[i-1] == 'Install' and s[i+1].startswith('check'), s"   # rc 0
- V8: git diff --stat HEAD -- . ':!runs' lista solo .sldb/store.yaml, .sldb/core/store_index.yaml, .github/workflows/check.yml y CHANGELOG.md; git diff HEAD -- .sldb/store.yaml cambia solo la línea path del enlace deskops, y git diff HEAD -- .sldb/core/store_index.yaml solo esa línea path y la de store_hash. El árbol parte limpio en esas rutas: el coordinador commitea el desk antes del despacho y no escribe en desk/ ni en .sldb/ mientras trabaja el ejecutor. Cualquier otro cambio es un hallazgo: el ejecutor para y lo reporta

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

FILE:.sldb/store.yaml
version: 1
links:
- name: deskops
  path: ../../../herramientas/deskops/.sldb
models:
- name: RelationTypeDoc
  model_ref: sldb.models.relation_type_doc:RelationTypeDoc
- name: RelationDoc
  model_ref: sldb.models.relation_doc:RelationDoc
- name: AnchorDoc
  model_ref: pron.models:AnchorDoc
  path: src/pron/models/anchor.py
- name: ProjectionDoc
  model_ref: pron.models:ProjectionDoc
  path: src/pron/models/projection.py
- name: MoveDoc
  model_ref: pron.models:MoveDoc
  path: src/pron/models/move.py
- name: TheoremDoc
  model_ref: pron.models:TheoremDoc
  path: src/pron/models/theorem.py
- name: SpecDoc
  model_ref: pron.models:SpecDoc
  path: src/pron/models/spec.py
- name: CliCommandDoc
  model_ref: sldb.models.knowledge_surface:CliCommandDoc
- name: SurfaceDoc
  model_ref: sldb.models.knowledge_surface:SurfaceDoc
- name: ExplanationDoc
  model_ref: pron.models:ExplanationDoc
  path: src/pron/models/explanation.py
- name: ReadmeDoc
  model_ref: pron.models:ReadmeDoc
  path: src/pron/models/readme.py
- name: CrossroadDoc
  model_ref: deskops.models:CrossroadDoc
  origin: deskops
- name: AtomDoc
  model_ref: deskops.models:AtomDoc
  origin: deskops
- name: BoardDoc
  model_ref: deskops.models:BoardDoc
  origin: deskops
- name: DeskFAQDoc
  model_ref: deskops.models:DeskFAQDoc
  origin: deskops
- name: InboxNoteDoc
  model_ref: deskops.models:InboxNoteDoc
  origin: deskops
- name: MaterializationContractDoc
  model_ref: deskops.models:MaterializationContractDoc
  origin: deskops
- name: PillDoc
  model_ref: deskops.models:PillDoc
  origin: deskops
- name: ProtoAtomDoc
  model_ref: deskops.models:ProtoAtomDoc
  origin: deskops
- name: RepositoryDoc
  model_ref: deskops.models:RepositoryDoc
  origin: deskops
- name: ReviewDoc
  model_ref: deskops.models:ReviewDoc
  origin: deskops
- name: RitualDoc
  model_ref: deskops.models:RitualDoc
  origin: deskops
- name: RoleDoc
  model_ref: deskops.models:RoleDoc
  origin: deskops
- name: RunDoc
  model_ref: deskops.models:RunDoc
  origin: deskops
- name: RuntimeProfileDoc
  model_ref: deskops.models:RuntimeProfileDoc
  origin: deskops
- name: StepDoc
  model_ref: deskops.models:StepDoc
  origin: deskops
- name: TaskAggregateDoc
  model_ref: deskops.models:TaskAggregateDoc
  origin: deskops
- name: TaskCodeDoc
  model_ref: deskops.models:TaskCodeDoc
  origin: deskops
- name: TaskDebugDoc
  model_ref: deskops.models:TaskDebugDoc
  origin: deskops
- name: TaskDecisionDoc
  model_ref: deskops.models:TaskDecisionDoc
  origin: deskops
- name: TaskDoc
  model_ref: deskops.models:TaskDoc
  origin: deskops
- name: TaskDocsDoc
  model_ref: deskops.models:TaskDocsDoc
  origin: deskops
- name: TaskExternalDoc
  model_ref: deskops.models:TaskExternalDoc
  origin: deskops
- name: TaskRefactorDoc
  model_ref: deskops.models:TaskRefactorDoc
  origin: deskops
- name: RuleDoc
  model_ref: sldb.models.rule_doc:RuleDoc
predicates:
  applies_to_source:
    axis: WHAT
    description: 'Instances of this model may be the source of edges of this relation type: the verbs
      a class can be subject of.'
  applies_to_target:
    axis: WHAT
    description: Instances of this model may be the target of edges of this relation type.
  composes:
    axis: WHAT
    description: A composed field of the source (`__compositions__`) renders this document's payload into
      the source's text; the edge carries the composed field, the field holding the refs and the ref as
      authored.
  contains:
    axis: WHERE
    description: A field the model declared in `__containment__` holds this document as a child; the edge
      carries the field name and the models the declaration allows.
  defines:
    axis: WHAT
    description: Defines the target concept.
  explains_failure_of:
    axis: WHY
    description: Explains why the target fails.
  extends:
    axis: WHAT
    description: The model inherits from that model (base_models); instances of the source are instances
      of the target.
  grounded_by:
    axis: PROVENANCE
    description: Identifies supporting provenance.
  has_document:
    axis: WHAT
    description: The model has this document as an instance.
  has_field:
    axis: WHAT
    description: The model declares this field; the field node carries its type and description.
  has_model:
    axis: WHAT
    description: 'The store registers this model: its own, or one it inherits from the linked store that
      owns it.'
  has_section:
    axis: WHERE
    description: The document contains this section.
  implements:
    axis: HOW
    description: Identifies what the source implements.
  is_solved_by:
    axis: HOW
    description: Identifies how the source is solved.
  links_to:
    axis: WHERE
    description: 'The store links that store under an alias (`stores add`): it reads its documents and
      inherits its models.'
  mathematically_proves:
    axis: WHY
    description: Provides a mathematical proof.
  names:
    axis: WHAT
    description: The anchor (an alias word) names this model, field, relation type or document.
  references:
    axis: WHAT
    description: A field the model declared in `__references__` holds this document's id; the edge carries
      the field name.
  restricts:
    axis: WHEN_WHERE
    description: Restricts the target context.
  semantic_equivalent:
    axis: WHAT
    description: This local tag maps to that global tag across linked stores.
  semantic_parent:
    axis: WHAT
    description: This tag is a child of that tag in the semantic DAG.
  tagged_as:
    axis: WHAT
    description: The model, document or section carries this semantic tag.
generate: []
derived: []
include:
- model: AnchorDoc
  paths:
  - path: knowledge/anchors/chapter.md
    name: anchor-chapter
  - path: knowledge/anchors/command.md
    name: anchor-command
  - path: knowledge/anchors/implements.md
    name: anchor-implements
  - path: knowledge/anchors/module.md
    name: anchor-module
  - path: knowledge/anchors/move.md
    name: anchor-move
- model: CliCommandDoc
  glob: knowledge/commands/*.md
- model: ExplanationDoc
  glob: knowledge/explanations/*.md
- model: InboxNoteDoc
  glob: desk/inbox/*.md
- model: MoveDoc
  glob: ledger/*.md
- model: ProjectionDoc
  paths:
  - path: knowledge/projections/all.md
    name: projection-all
- model: ReadmeDoc
  paths:
  - knowledge/readme.md
- model: RelationDoc
  paths:
  - knowledge/relations/implements--CliCommandDoc:cmd-pron-eval--SpecDoc:spec-13.md
  - knowledge/relations/implements--CliCommandDoc:cmd-pron-mcp--SpecDoc:spec-14.md
  - knowledge/relations/implements--CliCommandDoc:cmd-pron-serve--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-check--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-docs--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-eval--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-eval--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-init--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-init--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-lexicon--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-lexicon--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-mcp--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-refresh--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-refresh--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-repl--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-repl--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-say--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-say--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-say--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-serve--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-commands-serve--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-main--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-options--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-options--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-repl--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-cli-session--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-corpus-corpus--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-corpus-corpus_audit--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-corpus-corpus_entry--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-corpus-hit--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-corpus-index_projection--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs_sync-command_docs--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs_sync-doc_drift--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs_sync-generated_docs--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs_sync-implements_edges--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs_sync-implements_edges--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs_sync-readme_render--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs_sync-spec_docs--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs_sync-stale_surfaces--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs_sync-surface_docs--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs_sync-written_docs--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-docs_sync-written_docs--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-actions-add_verb--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-actions-change_verb--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-actions-clean_verb--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-actions-create_verb--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-actions-dry_run--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-actions-forget_verb--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-actions-move_undo--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-actions-remove_verb--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-actions-verb--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-actions-verb_registry--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-actions-write--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-display--SpecDoc:spec-09a.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-display--SpecDoc:spec-10.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-field_coercion--SpecDoc:spec-04.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-field_coercion--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-ids--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-kernel--SpecDoc:spec-04.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-kernel--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-parts-interpretation--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-parts-item--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-parts-noun_phrase--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-parts-part--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-parts-response--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-parts-word--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-parts-word--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-sexp-read_write--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-sexp-sexp_error--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-kernel-sexp-sym--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-lints--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-app--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-audit_tool--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-doc_entries--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-family_selector--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-finder--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-found--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-kb_uri--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-ladder_gate--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-literal_reads--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-literal_reads--SpecDoc:spec-10.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-literal_reads--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-model_tools--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-mount--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-mount--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-neighbors--SpecDoc:spec-10.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-neighbors--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-page--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-ranked_search--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-read_plane--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-read_plane--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-read_tools--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-rule_tools--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-schema-draft_file--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-schema-draft_file--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-schema-field_decl--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-schema-model_check--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-schema-model_create--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-schema-model_create--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-schema-model_extend--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-schema-model_extend--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-schema-model_source--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-semantic_reads--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-semantic_reads--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-server--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-tool_table--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-transitions--SpecDoc:spec-10.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-transitions--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-value_selector--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-value_selector--SpecDoc:spec-10.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-value_selector--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-walk--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-world_mounts--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-world_state--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-write_tools--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-arg_error--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-content_forms--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-content_writes--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-dry_evaluator--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-dry_move--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-edge_ids--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-form_runner--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-form_values--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-ladder--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-response_json--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-rule_edges--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-rule_edges--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-rule_effect--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-rule_forms--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-rule_judge--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-rule_writes--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-mcp-writes-writes--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-models-anchor--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-models-explanation--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-models-move--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-models-projection--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-models-readme--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-models-readme--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-models-spec--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-models-theorem--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-plnr-commit--SpecDoc:spec-04.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-plnr-commit--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-plnr-plan_execution--SpecDoc:spec-04.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-plnr-plan_planning--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-plnr-plan_planning--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-plnr-pron_world--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-plnr-theorem_load--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-remote-client--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-remote-remote--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-remote-remote_graph--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-remote-remote_session--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-remote-remote_world--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-serve--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-serve--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-serving-request_dispatcher--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-serving-request_handler--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-serving-session_ops--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-serving-session_pool--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-serving-socket_serving--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-serving-socket_serving--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-serving-world_names--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-serving-world_ops--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-session--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-dialogue-asker--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-dialogue-corrector--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-dialogue-designation--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-dialogue-dialogue--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-dialogue-parse_hint--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-dialogue-parse_hint--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-dialogue-pending--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-dialogue-replier--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-dialogue-unknown_words--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-dialogue-unknown_words--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-dialogue-value_suggestions--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-action_executor--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-assert_executor--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-compose_executor--SpecDoc:spec-04.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-compose_executor--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-executor--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-listing--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-read_executor--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-read_executor--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-relation_write--SpecDoc:spec-04.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-relation_write--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-relation_write--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-undo_executor--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-undo_executor--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-execution-why_executor--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-assert_form--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-bare_form--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-compiler--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-composed_steps--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-create_form--SpecDoc:spec-04.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-form--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-form--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-form_error--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-form_registry--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-form_words--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-form_words--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-goal_form--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-legacy_ref--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-not_a_move--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-noun_compiler--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-read_form--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-ref--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-refs--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-say_form--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-show_form--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-syntax--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-unknown_word--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-why_form--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-write_form--SpecDoc:spec-04.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-forms-write_form--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-planning-compose_planner--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-planning-compose_slots--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-planning-needed_model--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-planning-phrase_planner--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-planning-phrase_planner--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-planning-planner--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-prevalidation-action_verb--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-prevalidation-action_verb--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-prevalidation-dry_action--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-prevalidation-dry_assert--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-prevalidation-dry_assert--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-prevalidation-dry_compose--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-prevalidation-dry_compose--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-prevalidation-dry_runner--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-prevalidation-prevalidator--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-complement_links--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-condition_check--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-decision--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-decision--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-edge_assertion--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-edge_read--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-edge_reader--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-field_kind--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-field_values--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-leftover_predicates--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-pending_match--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-predicate_filter--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-proper_names--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-relation_checks--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-resolution--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-resolution--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-resolve--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-state_machine--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-resolving-verbs--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-evaluator--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-form_turn--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-ledger--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-move--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-move_context--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-move_context--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-move_context--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-move_context--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-move_order--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-move_order--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-new_sentence--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-note_reads--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-projection_load--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-projection_load--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-projection_load--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-projection_settings--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-projection_state--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-projection_state--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-sentence_turn--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-turn_tools--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-sexpr-turn-turn_tools--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-classifier--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-classifying-form_matcher--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-classifying-form_matcher--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-classifying-function_word_table--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-classifying-function_word_table--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-action_alias_construction--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-assert_relation_construction--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-change_to_construction--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-compose_construction--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-construction--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-construction_registry--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-create_construction--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-field_and_value--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-field_literals--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-field_literals--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-forget_construction--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-list_op_construction--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-lone_verb_construction--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-nominal_construction--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-read_relation_construction--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-set_field_construction--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-constructions-why_construction--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-dates--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-interpret--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-interpreter--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-nouns--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-phrases-field_values--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-phrases-field_values--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-phrases-modifier_reader--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-phrases-phrase_opening--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-phrases-phrase_reader--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-phrases-phrase_words--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-phrases-proper_run--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-phrases-word_modifier--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-render--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-render_addresses--SpecDoc:spec-07.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-render_noun--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-render_said--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-surface-tokens--SpecDoc:spec-06.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-doc_id--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-doc_kind--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-fingerprint--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-graph--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-graph_ids--SpecDoc:spec-03.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-lexicon--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-lexicon_parts-alias_words--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-lexicon_parts-alias_words--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-lexicon_parts-document_values--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-lexicon_parts-model_words--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-lexicon_parts-relation_words--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-lexicon_parts-spoken_forms--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-lexicon_parts-verbs_for--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-lexicon_parts-vocabulary--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-lexicon_parts-vocabulary--SpecDoc:spec-13.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-matching-difflib_matcher--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-matching-document_index--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-matching-embedder_protocol--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-matching-matcher--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-mutability--SpecDoc:spec-05.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-mutability--SpecDoc:spec-14.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-pending_refresh--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-projection_reader--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-projection_reader--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-cleaned_list--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-document_reader--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-document_tracker--SpecDoc:spec-04.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-document_tracker--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-linked_stores--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-linked_stores--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-model_editor--SpecDoc:spec-10.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-model_editor--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-model_registry--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-model_registry--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-payload_editor--SpecDoc:spec-04.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-payload_editor--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-structural_query--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-storage-structural_query--SpecDoc:spec-11.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-store--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-store--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-store--SpecDoc:spec-04.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-store--SpecDoc:spec-10.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-store--SpecDoc:spec-12.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-store_error--SpecDoc:spec-02.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-world--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-world_declaration--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-world_init--SpecDoc:spec-01.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-world_init--SpecDoc:spec-08.md
  - knowledge/relations/implements--SurfaceDoc:surface-pron-world-world_template--SpecDoc:spec-01.md
  - desk/lifecycle/execution-task_activates.md
  - desk/lifecycle/testing-task_hands_to_closeout.md
  - desk/lifecycle/closeout-task_completes.md
- model: RelationTypeDoc
  paths:
  - path: knowledge/relations/types/implements.md
    name: rt-implements
  - desk/lifecycle/type-task_activates.md
  - desk/lifecycle/type-task_completes.md
  - desk/lifecycle/type-task_hands_to_closeout.md
- model: RelationTypeDoc
  paths:
  - path: sldb/relation_types/applies_to_source.md
    name: reltype-applies_to_source
  - path: sldb/relation_types/applies_to_target.md
    name: reltype-applies_to_target
  - path: sldb/relation_types/composes.md
    name: reltype-composes
  - path: sldb/relation_types/contains.md
    name: reltype-contains
  - path: sldb/relation_types/extends.md
    name: reltype-extends
  - path: sldb/relation_types/has_document.md
    name: reltype-has_document
  - path: sldb/relation_types/has_field.md
    name: reltype-has_field
  - path: sldb/relation_types/has_model.md
    name: reltype-has_model
  - path: sldb/relation_types/has_section.md
    name: reltype-has_section
  - path: sldb/relation_types/links_to.md
    name: reltype-links_to
  - path: sldb/relation_types/names.md
    name: reltype-names
  - path: sldb/relation_types/references.md
    name: reltype-references
  - path: sldb/relation_types/semantic_equivalent.md
    name: reltype-semantic_equivalent
  - path: sldb/relation_types/semantic_parent.md
    name: reltype-semantic_parent
  - path: sldb/relation_types/tagged_as.md
    name: reltype-tagged_as
- model: ReviewDoc
  paths:
  - path: desk/reviews/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c/bundle-1.md
    name: review-task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c-bundle-1
  - path: desk/reviews/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c/bundle-2.md
    name: review-task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c-bundle-2
  - path: desk/reviews/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c/owner-1.md
    name: review-task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c-owner-1
  - path: desk/reviews/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c/owner-2.md
    name: review-task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c-owner-2
  - path: desk/reviews/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c/preflight-1.md
    name: review-task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c-preflight-1
  - path: desk/reviews/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c/preflight-2.md
    name: review-task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c-preflight-2
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/preflight-5.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-preflight-5
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/bundle-4.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-bundle-4
  - path: desk/reviews/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada/preflight-1.md
    name: review-task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada-preflight-1
  - path: desk/reviews/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada/bundle-1.md
    name: review-task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada-bundle-1
  - path: desk/reviews/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada/preflight-2.md
    name: review-task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada-preflight-2
  - path: desk/reviews/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada/bundle-2.md
    name: review-task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada-bundle-2
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/preflight-6.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-preflight-6
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/bundle-5.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-bundle-5
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/evidence-tests-1.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-evidence-tests-1
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/evidence-commit-1.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-evidence-commit-1
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/evidence-atom-1.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-evidence-atom-1
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/evidence-tests-2.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-evidence-tests-2
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/evidence-commit-2.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-evidence-commit-2
  - path: desk/reviews/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c/evidence-commit-1.md
    name: review-task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c-evidence-commit-1
  - path: desk/reviews/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c/evidence-document-1.md
    name: review-task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c-evidence-document-1
  - path: desk/reviews/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada/preflight-3.md
    name: review-task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada-preflight-3
  - path: desk/reviews/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c/evidence-commit-2.md
    name: review-task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c-evidence-commit-2
  - path: desk/reviews/task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c/evidence-document-2.md
    name: review-task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c-evidence-document-2
  - path: desk/reviews/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada/bundle-3.md
    name: review-task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada-bundle-3
  - path: desk/reviews/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada/evidence-tests-1.md
    name: review-task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada-evidence-tests-1
  - path: desk/reviews/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada/evidence-commit-1.md
    name: review-task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada-evidence-commit-1
  - path: desk/reviews/task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada/evidence-atom-1.md
    name: review-task-pron-versiona-sldb-store-yaml-y-sldb-core-opción-a-de-jp-sldb-cache-sigue-ignorada-evidence-atom-1
  - path: desk/reviews/task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y/preflight-1.md
    name: review-task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y-preflight-1
  - path: desk/reviews/task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y/preflight-2.md
    name: review-task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y-preflight-2
- model: ReviewDoc
  paths:
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/bundle-1.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-bundle-1
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/bundle-2.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-bundle-2
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/bundle-3.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-bundle-3
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/preflight-1.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-preflight-1
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/preflight-2.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-preflight-2
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/preflight-3.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-preflight-3
  - path: desk/reviews/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v/preflight-4.md
    name: review-task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v-preflight-4
- model: SpecDoc
  paths:
  - path: source/spec/01-mundo.md
    name: spec-01
  - path: source/spec/02-sustantivos.md
    name: spec-02
  - path: source/spec/03-verbos-transitivos.md
    name: spec-03
  - path: source/spec/04-verbos-de-accion.md
    name: spec-04
  - path: source/spec/05-lexico-y-proyeccion.md
    name: spec-05
  - path: source/spec/06-superficie-y-dialogo.md
    name: spec-06
  - path: source/spec/07-ledger.md
    name: spec-07
  - path: source/spec/08-prerequisitos-y-orden.md
    name: spec-08
  - path: source/spec/09-una-conversacion.md
    name: spec-09
  - path: source/spec/09a-el-mundo-del-restaurante.md
    name: spec-09a
  - path: source/spec/10-el-shrdlu-sobre-el-modelo.md
    name: spec-10
  - path: source/spec/11-decisiones-de-implementacion.md
    name: spec-11
  - path: source/spec/12-pron-para-un-runtime.md
    name: spec-12
  - path: source/spec/13-formas.md
    name: spec-13
  - path: source/spec/14-superficie-mcp.md
    name: spec-14
- model: SurfaceDoc
  glob: knowledge/surfaces/*.md
- model: TaskCodeDoc
  paths:
  - desk/tasks/task-pron-vuelve-a-verde-contra-sldb-main-la-caché-de-aristas-se-lee-de-sldb-cache-y-los-goldens-de-la-co.md
  - desk/tasks/task-pron-sldb-enlaza-deskops-como-repo-hermano-deskops-sldb-en-vez-de-la-ruta-de-robocop2-herramientas-y.md
- model: RuleDoc
  paths:
  - desk/lifecycle/rule-activation-task-aggregate.md
  - desk/lifecycle/rule-activation-task-code.md
  - desk/lifecycle/rule-activation-task-debug.md
  - desk/lifecycle/rule-activation-task-decision.md
  - desk/lifecycle/rule-activation-task-docs.md
  - desk/lifecycle/rule-activation-task-external.md
  - desk/lifecycle/rule-activation-task-refactor.md
  - desk/lifecycle/rule-closeout-alert-implicit-code.md
  - desk/lifecycle/rule-closeout-alert-pill-graduation.md
  - desk/lifecycle/rule-closeout-task-aggregate.md
  - desk/lifecycle/rule-closeout-task-code.md
  - desk/lifecycle/rule-closeout-task-debug.md
  - desk/lifecycle/rule-closeout-task-decision.md
  - desk/lifecycle/rule-closeout-task-docs.md
  - desk/lifecycle/rule-closeout-task-external.md
  - desk/lifecycle/rule-closeout-task-refactor.md
- model: BoardDoc
  paths:
  - desk/tasks/Board.md
- model: RitualDoc
  paths:
  - path: desk/rituals/phase.md
    name: ritual-phase
  - path: desk/rituals/execution.md
    name: ritual-execution
  - path: desk/rituals/testing.md
    name: ritual-testing
  - path: desk/rituals/closeout.md
    name: ritual-closeout
- model: RunDoc
  paths:
  - path: runs/subagents/exec-pron-20261116-e-6327bf9f19e7/run.md
    name: run-deskops-e-6327bf9f19e7
  - path: runs/subagents/exec-pron-20261116-e-a2/run.md
    name: run-deskops-e-86f5d629bc99-a2
  - path: runs/subagents/exec-pron-20261116-e-c2/run.md
    name: run-deskops-e-fe40ac7a9ef8-a2
  - path: runs/subagents/exec-pron-20261116-t-c2/run.md
    name: run-deskops-t-69a6715f4520
  - path: runs/subagents/exec-pron-20261116-d-e1/run.md
    name: run-deskops-e-a868cc40330a
  - path: runs/subagents/exec-pron-20261116-d-t1/run.md
    name: run-deskops-t-7fd22c4b0c80
  - path: runs/subagents/exec-pron-20261116-d-t2/run.md
    name: run-deskops-t-7fd22c4b0c80-a2
  - path: runs/subagents/exec-pron-20261116-s-e1/run.md
    name: run-deskops-e-5772eb9505bd
  - path: runs/subagents/exec-pron-20261116-s-t1/run.md
    name: run-deskops-t-5c0748a304c0
- model: RepositoryDoc
  paths:
  - desk/registry/repo-IR.md
graph_backend: networkx
policy: {}
tag_models:
- AtomDoc
- ProtoAtomDoc
tag_namespaces:
- name: domain
  hierarchical: true
  folder_axis: false
  anchored_by:
    model: CrossroadDoc
    field: path
    value: bare
- name: layer
  hierarchical: true
  folder_axis: false
- name: system
  hierarchical: true
  folder_axis: false
- name: topic
  hierarchical: true
  folder_axis: false

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
store_hash: e10ba65810c22186914a80865a7e4410be26f1b8bed1da7092dcd7086760f8e9

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
- V1: cd /mnt/ssd/proyectos/SLDB_1/pron && TMPDIR=/dev/shm /dev/shm/pron-venv/bin/sldb stores list   # imprime 'deskops -> ../deskops/.sldb'
- V2: grep -n 'herramientas' .sldb/store.yaml .sldb/core/store_index.yaml   # no imprime nada (rc 1 de grep es lo esperado)
- V3: /dev/shm/pron-venv/bin/python -c "from pathlib import Path; from sldb.store.model_origin import linked_store; p = linked_store(Path('.sldb').resolve(), 'deskops'); print(p); assert p == Path('/mnt/ssd/proyectos/SLDB_1/deskops/.sldb')"   # rc 0 en el checkout real de robocop2
- V4 (layout del CI de sldb, caché fría): W=/dev/shm/pron-link-ci; rm -rf $W; mkdir -p $W/pron; rsync -a --exclude .git --exclude .sldb_cache /mnt/ssd/proyectos/SLDB_1/pron/ $W/pron/; git clone -q --depth 1 https://github.com/jpcosec/opsys.git $W/deskops; cd $W/pron && PATH=/dev/shm/pron-venv/bin:$PATH TMPDIR=/dev/shm make world PYTHON=python   # rc 0. make world no corre tests: son las tres líneas del target world del Makefile (sldb stores init si falta el índice, pron init --world --knowledge y pron docs), así que las fallas de tests fuera de alcance no lo afectan (tarda más de 10 minutos: correrlo con timeout de 40 min o en segundo plano); desde $W/pron, ../../../herramientas resuelve a /herramientas, que no existe, así que la ruta vieja no puede colarse
- V5: en el mismo $W/pron, PATH=/dev/shm/pron-venv/bin:$PATH TMPDIR=/dev/shm python -m pron.cli.main docs --world . --pythonpath .   # rc 0, sin 'No store_index.yaml'
- V6 (control): repetir V4 tal cual pero con W=/dev/shm/pron-link-ci-control y, antes de make world, copiar sobre la copia los dos archivos de HEAD: git -C /mnt/ssd/proyectos/SLDB_1/pron show HEAD:.sldb/store.yaml > $W/pron/.sldb/store.yaml y lo mismo con .sldb/core/store_index.yaml; make world (o pron docs, V5, si make world pasa) falla con 'No store_index.yaml at' y una ruta que contiene herramientas/deskops/.sldb
- V7: /dev/shm/pron-venv/bin/python -c "import yaml; w = yaml.safe_load(open('.github/workflows/check.yml')); s = [x.get('name') for x in w['jobs']['check']['steps']]; i = s.index('deskops next to pron'); assert s[i-1] == 'Install' and s[i+1].startswith('check'), s"   # rc 0
- V8: git diff --stat HEAD -- . ':!runs' lista solo .sldb/store.yaml, .sldb/core/store_index.yaml, .github/workflows/check.yml y CHANGELOG.md; git diff HEAD -- .sldb/store.yaml cambia solo la línea path del enlace deskops, y git diff HEAD -- .sldb/core/store_index.yaml solo esa línea path y la de store_hash. El árbol parte limpio en esas rutas: el coordinador commitea el desk antes del despacho y no escribe en desk/ ni en .sldb/ mientras trabaja el ejecutor. Cualquier otro cambio es un hallazgo: el ejecutor para y lo reporta

