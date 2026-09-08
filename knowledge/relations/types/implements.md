---
name: implements
direction: directed
cardinality: many_to_many
axis: HOW
source_types:
- SurfaceDoc
- CliCommandDoc
target_types:
- SpecDoc
condition: ''
---

# implements

## Description

This module or command implements that chapter of the specification: the direct branch from the code to what it is supposed to do, derived from the spec references in the module's docstring.
