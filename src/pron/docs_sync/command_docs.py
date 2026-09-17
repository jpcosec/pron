"""A CliCommandDoc per pron command (spec 08 step 9): synopsis, how it works and usage from
the handler's docstring, one argument line per click parameter, and the spec chapters the
docstring cites.
"""

from __future__ import annotations

import re
from typing import Any

TAGS = [
    "system:pron",
    "domain:system_architecture",
    "kind:software",
    "impl:here",
    "entity:cli_command",
]
SPEC_REF = re.compile(r"\bspec\s+(\d{2}[a-z]?)\b", re.I)


class CommandDocs:
    """The CliCommandDoc payloads of pron's click group, in the order the commands were added."""

    def __call__(self) -> list[dict[str, Any]]:
        from pron.cli.main import cli

        return [self._spec(name, command) for name, command in cli.commands.items()]

    def _spec(self, name: str, command: Any) -> dict[str, Any]:
        fn = command.callback
        synopsis, how, usage = self._parse_doc(fn.__doc__ or "")
        args = [self._argument_line(param) for param in command.params]
        return {
            "id": f"cmd-pron-{name}",
            "system": "pron",
            "command_path": name,
            "synopsis": synopsis or command.help or "",
            "purpose": synopsis,
            "how_it_works": how or synopsis,
            "arguments": "\n".join(args) or "(none)",
            "usage": usage or f"pron {name}",
            "tags": TAGS,
            "provenance": f"src/{fn.__module__.replace('.', '/')}.py:{fn.__name__}",
            "_cites": sorted(set(SPEC_REF.findall(fn.__doc__ or ""))),
        }

    @staticmethod
    def _parse_doc(doc: str) -> tuple[str, str, str]:
        """synopsis (first line), how it works (paragraphs before Usage), usage block."""
        lines = (doc or "").strip().splitlines()
        synopsis = lines[0].strip() if lines else ""
        rest = "\n".join(lines[1:]).strip()
        how, _, usage = rest.partition("Usage:")
        return synopsis, how.strip(), usage.strip()

    @staticmethod
    def _argument_line(param: Any) -> str:
        """`<flag> | required|optional | <help>`; a positional counts as required even when it may be
        omitted, as the documents have always said."""
        import click

        positional = isinstance(param, click.Argument)
        flag = param.name if positional else param.opts[0]
        required = "required" if param.required or positional else "optional"
        return f"{flag} | {required} | {getattr(param, 'help', None) or ''}"
