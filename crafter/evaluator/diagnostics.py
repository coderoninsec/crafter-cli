"""Capability diagnostics for agent evaluation.

These checks are intentionally heuristic. The platform is teaching users how to
build agents, so the goal is to determine whether the agent demonstrates a
capability rather than enforcing a single implementation style.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from crafter.evaluator.normalizer import normalize_result
from crafter.project import project_structure_is_valid


DiagnosticResult = dict[str, bool]


def _safe_run(agent: Any, input_text: str) -> dict:
    """Run the agent and normalize the result, even if the agent misbehaves."""

    try:
        result = agent.run(input_text)
    except Exception as exc:
        # A broken prompt should never crash the evaluator; it just becomes a
        # failed diagnostic result.
        return normalize_result({"output": "", "tools_used": [], "memory": {}, "error": str(exc)})
    return normalize_result(result)


def _has_meaningful_output(result: dict) -> bool:
    """Check whether the agent produced a non-empty, non-error response."""

    return bool(str(result.get("output", "")).strip()) and result.get("error") is None


def _diagnose_local_setup(project_root: Path | None) -> bool:
    """Determine whether the learner project is structurally ready.

    Local setup is the first concrete milestone after introduction, so this
    check looks at the project scaffold rather than the agent's runtime output.
    """

    if project_root is None:
        return False
    return project_structure_is_valid(project_root)


def _diagnose_first_response(agent: Any) -> bool:
    """Determine whether the agent can answer a basic prompt at all."""

    result = _safe_run(agent, "hello")
    return _has_meaningful_output(result)


def _diagnose_llm_connection(agent: Any) -> bool:
    """Determine whether the agent can answer a conversational prompt."""

    result = _safe_run(agent, "ping")
    output = str(result.get("output", "")).strip().lower()
    return bool(output) and output != "ping"


def _diagnose_tool_definition(agent: Any) -> bool:
    """Determine whether the agent exposes a usable tool registry."""

    tools = getattr(agent, "tools", None)
    if isinstance(tools, dict) and tools:
        return True
    if isinstance(tools, list) and tools:
        return True

    for attribute in ("tool_registry", "available_tools"):
        value = getattr(agent, attribute, None)
        if isinstance(value, dict) and value:
            return True
        if isinstance(value, list) and value:
            return True
        if callable(value):
            try:
                result = value()
            except Exception:
                continue
            if isinstance(result, dict) and result:
                return True
            if isinstance(result, list) and result:
                return True

    return False


def _diagnose_tool_execution(agent: Any) -> bool:
    """Determine whether the agent reports that it used tools."""

    result = _safe_run(agent, "Use a tool if needed and report what you used.")
    tools_used = result.get("tools_used", [])
    return isinstance(tools_used, list) and len(tools_used) > 0


def _diagnose_agent_loop(agent: Any) -> bool:
    """Determine whether the agent can follow a small multi-step prompt."""

    result = _safe_run(agent, "Add 1 to 3, then multiply by 2.")
    output = str(result.get("output", ""))
    return bool(re.search(r"\b8\b", output))


def _diagnose_write_tool(agent: Any) -> bool:
    """Determine whether the agent exposes a custom tool implementation."""

    tools = getattr(agent, "tools", None)
    if isinstance(tools, dict) and tools:
        for name, value in tools.items():
            if callable(value) and str(name).strip().lower() not in {"fetch", "tool", "tools"}:
                return True
    if isinstance(tools, list) and tools:
        for item in tools:
            if callable(item):
                return True

    for attribute in ("tool_registry", "available_tools"):
        value = getattr(agent, attribute, None)
        if isinstance(value, dict) and value:
            for name, tool in value.items():
                if callable(tool) and str(name).strip().lower() not in {"fetch", "tool", "tools"}:
                    return True
        if isinstance(value, list) and value:
            for item in value:
                if callable(item):
                    return True
        if callable(value):
            try:
                result = value()
            except Exception:
                continue
            if isinstance(result, dict) and result:
                for name, tool in result.items():
                    if callable(tool) and str(name).strip().lower() not in {"fetch", "tool", "tools"}:
                        return True
            if isinstance(result, list) and result:
                for item in result:
                    if callable(item):
                        return True

    return False


DIAGNOSTIC_FUNCTIONS: dict[str, Callable[..., bool]] = {
    "project_structure": _diagnose_local_setup,
    "first_response": _diagnose_first_response,
    "llm_connection": _diagnose_llm_connection,
    "tool_definition": _diagnose_tool_definition,
    "tool_execution": _diagnose_tool_execution,
    "agent_loop": _diagnose_agent_loop,
    "write_tool": _diagnose_write_tool,
}


def run_diagnostics(agent: Any, *, project_root: Path | None = None) -> DiagnosticResult:
    """Run every capability diagnostic and return a stable boolean map.

    The academy is sequential, so diagnostics are read from the same stage
    definitions the roadmap uses. The evaluator does not invent its own order.
    """

    results: DiagnosticResult = {}
    for name, diagnostic in DIAGNOSTIC_FUNCTIONS.items():
        try:
            if name == "project_structure":
                results[name] = bool(diagnostic(project_root))
            else:
                results[name] = bool(diagnostic(agent))
        except Exception:
            # Diagnostics should never crash the learning platform.
            results[name] = False
    return results
