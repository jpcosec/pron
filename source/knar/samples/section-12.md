# 12. LLM como nodo

```text
Input
  │
  ▼
Knowledge Projection
  │
  ▼
LLM Runtime
  │
  ▼
Typed Output
```

Ejemplo:

```yaml
id: research.interpreter

runtime:
  type: llm
  provider: deepseek

inputs:
  - SourceDocument

outputs:
  - KnowledgeAtom[]

knowledge:
  read:
    - ontology
    - source_notes

capabilities:
  - extract_claims
  - relate_concepts
```

El prompt debería ser una **proyección derivada del SelfDoc + conocimiento + contrato**, no la fuente primaria de comportamiento.

---

