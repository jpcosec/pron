"""The tools of the MCP server as a table (spec 14 §3, §4, §5): name, function, mutability
level. The server registers whatever the table holds, so a new tool is one `add` and never a
change to the server. Each function's signature is its input schema and its docstring its
description; the gate, when set, sees every call first and may answer it without running it
(a level the session does not have, spec 14 §5).
"""

from __future__ import annotations

import functools
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any

Gate = Callable[["ToolSpec", dict[str, Any]], "dict[str, Any] | None"]


@dataclass(frozen=True)
class ToolSpec:
    """One tool: its name, its function, the mutability level it needs (0 reads)."""

    name: str
    fn: Callable[..., Any]
    level: int = 0

    @property
    def description(self) -> str:
        return (self.fn.__doc__ or self.name).strip()


class ToolTable:
    """name -> ToolSpec, in the order they were added, and the gate every call goes through."""

    def __init__(self, gate: Gate | None = None) -> None:
        self.specs: dict[str, ToolSpec] = {}
        self.gate = gate

    def add(self, name: str, fn: Callable[..., Any], level: int = 0) -> ToolSpec:
        if name in self.specs:
            raise ValueError(f"tool {name!r} is already in the table")
        self.specs[name] = spec = ToolSpec(name, fn, level)
        return spec

    def __iter__(self) -> Iterator[ToolSpec]:
        return iter(self.specs.values())

    def __getitem__(self, name: str) -> ToolSpec:
        return self.specs[name]

    def call(self, tool: str, /, **args: Any) -> Any:
        """A tool by name, through the gate: what the server runs, and what tests can too.
        Positional-only, so a tool may take an argument called `name`."""
        return self.guarded(self.specs[tool])(**args)

    def guarded(self, spec: ToolSpec) -> Callable[..., Any]:
        """The tool's function behind the gate, with the function's own signature."""

        @functools.wraps(spec.fn)
        def run(**args: Any) -> Any:
            refused = self.gate(spec, args) if self.gate is not None else None
            return refused if refused is not None else spec.fn(**args)

        return run
