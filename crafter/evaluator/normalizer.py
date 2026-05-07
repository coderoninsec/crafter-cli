"""Normalize agent responses into a stable shape.

External agents can return different payloads depending on how they are built.
Crafter normalizes those payloads first so the diagnostic layer can evaluate
them consistently.
"""

from __future__ import annotations

from typing import Any


def normalize_result(res: Any) -> dict:
    """Return the canonical result schema expected by the evaluator.

    The function is intentionally forgiving. If the agent returns something that
    is not a dictionary, Crafter converts it into a dictionary-like fallback so
    the rest of the pipeline can keep working.
    """

    if not isinstance(res, dict):
        res = {"output": str(res)}

    return {
        "output": res.get("output", ""),
        "tools_used": res.get("tools_used", []),
        "memory": res.get("memory", {}),
        "error": res.get("error", None),
    }
