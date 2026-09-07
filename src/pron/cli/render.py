"""Renderer: result values -> JSON (default) or text, always with refs.

Implements atom-every-read-response-carries-refs-for-auditability and
atom-semantic-errors-answer-symbol-motive-and-next-action.
"""

from __future__ import annotations

import json
from typing import Any

from knowledge.core.results import (
    Ambiguous,
    Missing,
    OperationResult,
    SemanticError,
    to_dict,
)


def render(value: object, fmt: str = "json") -> tuple[str, int]:
    """Render any result value; returns (text, exit_code)."""
    if isinstance(value, OperationResult):
        payload = to_dict(value)
        code = 0 if value.status == "ok" else 1
        return _fmt(payload, fmt), code
    if isinstance(value, Ambiguous):
        return _fmt({"status": "ambiguous", **to_dict(value)}, fmt), 2
    if isinstance(value, Missing):
        data = to_dict(value)
        text = {
            "status": "missing",
            "message": f"No existe doc de ese tipo ({data['motive']}).",
            "nearest": data["nearest"],
        }
        return _fmt(text, fmt), 1
    if isinstance(value, SemanticError):
        data = to_dict(value)
        return _fmt({"status": "semantic_error", **data}, fmt), 1
    return _fmt({"status": "ok", "payload": value}, fmt), 0


def _fmt(data: dict[str, Any], fmt: str) -> str:
    if fmt == "text":
        return _text(data)
    return json.dumps(data, ensure_ascii=False, indent=1, default=str)


def _text(data: dict[str, Any]) -> str:
    lines = []
    status = data.get("status", "")
    if status == "semantic_error":
        lines.append(f"✗ {data.get('message', '')}")
        if data.get("hint"):
            lines.append(f"  {data['hint']}")
    elif status == "ambiguous":
        lines.append(f"? {data.get('question', '')}")
    elif status == "missing":
        lines.append(f"✗ {data.get('message', '')}")
        if data.get("nearest"):
            lines.append(f"  Cercanos: {', '.join(data['nearest'])}")
    else:
        lines.append(
            json.dumps(data.get("payload"), ensure_ascii=False, indent=1, default=str)
        )
        if data.get("refs"):
            lines.append("refs: " + ", ".join(data["refs"]))
    return "\n".join(lines)
