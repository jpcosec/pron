# 7. Capabilities

Una capability describe **qué puede garantizar el nodo**.

```yaml
capabilities:

  - id: extract.website
    input: WebSource
    output: SourceDocument

  - id: normalize.article
    input: RawArticle
    output: NormalizedArticle
```

Capabilities y runtime son conceptos distintos.

Por ejemplo:

```text
Capability:
    summarize_document

Runtime:
    DeepSeek
```

o:

```text
Capability:
    execute_query

Runtime:
    PostgreSQL
```

---

