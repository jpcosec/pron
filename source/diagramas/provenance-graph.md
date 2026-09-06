```mermaid
flowchart LR
    SRC[Source]
    SAM[Sample]
    ATM[Atom]
    CMP[Composition]

    SRC -->|sampled_from| SAM
    SAM -->|supports| ATM
    ATM -->|distilled_from| SAM
    CMP -->|composes| ATM
    CMP -->|derived_from| SAM
    CMP -->|derived_from| SRC
```
