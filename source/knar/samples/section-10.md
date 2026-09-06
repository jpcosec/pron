# 10. Completion Tests

Cada nodo define qué significa **haber terminado correctamente**.

Esto es distinto de un unit test tradicional.

Ejemplo:

```yaml
completion_tests:

  - name: source_exists
    assert:
      output.document != null

  - name: valid_schema
    schema:
      output.document: SourceDocument

  - name: stored
    assert:
      knowledge.exists(output.document.id)

  - name: no_missing_required_fields
    validator:
      SourceDocument.required_fields
```

Hay por tanto al menos tres niveles:

```text
Unit tests
    ↓
Contract tests
    ↓
Completion tests
```

### Unit test

¿Funciona la implementación?

### Contract test

¿Respeta inputs/outputs?

### Completion test

¿Cumplió realmente el objetivo prometido?

---

