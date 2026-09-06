# 13. SQL como nodo

```yaml
id: customer_database

runtime:
  type: postgres

inputs:
  - CustomerQuery

outputs:
  - CustomerRecordSet

knowledge:
  read:
    - database_schema

capabilities:
  - query_customer
  - aggregate_orders
```

El orquestador no necesita saber SQL.

Solo:

```text
CustomerQuery
      ↓
customer_database
      ↓
CustomerRecordSet
```

---

