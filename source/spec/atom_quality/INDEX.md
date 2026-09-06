# Atom Quality Index

## Propósito

Definir una base operativa compartida para:

- crear átomos con criterio consistente
- revisar calidad de átomos existentes
- reducir variación editorial y semántica
- establecer skills, procedimientos, estándares y rutinas de trabajo

## Documentos en esta carpeta

- [`ATOM_QUALITY_CHECKLIST.md`](./ATOM_QUALITY_CHECKLIST.md)
- [`ATOM_AUTHORING_STANDARD.md`](./ATOM_AUTHORING_STANDARD.md)
- [`ATOM_AUTHORING_PROCEDURE.md`](./ATOM_AUTHORING_PROCEDURE.md)
- [`ATOM_REVIEW_ROUTINE.md`](./ATOM_REVIEW_ROUTINE.md)
- [`ATOM_AUTHOR_SKILLS.md`](./ATOM_AUTHOR_SKILLS.md)
- [`ATOM_TAGGING_AND_PROVENANCE_CONVENTIONS.md`](./ATOM_TAGGING_AND_PROVENANCE_CONVENTIONS.md)
- [`ATOM_MODEL_ALIGNMENT_AND_MIGRATION_NOTES.md`](./ATOM_MODEL_ALIGNMENT_AND_MIGRATION_NOTES.md)

## Idea central

El problema actual no es solo de cobertura temática. También es de estandarización:

- cómo decidir si algo merece ser un átomo
- cómo redactarlo
- cómo etiquetarlo
- cómo registrar su procedencia
- cómo revisar si alcanzó calidad suficiente

Esta carpeta propone una disciplina mínima compartida para que el corpus deje de depender de intuiciones ad hoc.

En particular, `ATOM_TAGGING_AND_PROVENANCE_CONVENTIONS.md` intenta cerrar una ambigüedad detectada en la prueba con subagentes: la falta de una convención suficientemente explícita para tags y para el wording del campo de frontmatter `provenance`.

`ATOM_MODEL_ALIGNMENT_AND_MIGRATION_NOTES.md` resume además cómo se alinea el corpus heredado con el modelo formal usando `provenance` en frontmatter y por qué, durante la migración, muchos átomos heredados conservan una procedencia provisional a nivel de corpus mientras se completa el backfill fino por átomo.

## Resultado esperado

Si esta carpeta se adopta, un átomo nuevo o refinado debería poder responder claramente:

- qué afirmación estable contiene
- por qué es atómico y no una nota difusa
- qué pregunta 5WH1+ responde
- qué evidencia o spec lo respalda
- cómo se recupera por tags y facetas
- qué criterio se usó para considerarlo “suficientemente bueno”
