# 20. Integración con DeepSeek Harness

DeepSeek Harness no debería convertirse en la arquitectura principal.

Debe ser un runtime:

```text
Knowledge System
      │
      ▼
AgentSpec
      │
      ▼
DeepSeekHarnessAdapter
      │
      ▼
DeepSeek Harness
```

El adapter traduce:

```text
SelfDoc             → system/context
KnowledgeProjection → context
Capabilities        → tools
StateMachine        → execution rules
CompletionTests     → verification
```

Así puedes posteriormente tener:

```text
DeepSeekHarnessRuntime
ClaudeRuntime
LocalLLMRuntime
DeterministicRuntime
```

sin cambiar los agentes.

---

