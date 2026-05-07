"""Capability diagnostics for agent evaluation.

These checks are intentionally heuristic. The platform is teaching users how to
build agents, so the goal is to determine whether the agent demonstrates a
capability rather than enforcing a single implementation style.
"""

from __future__ import annotations

import re
from typing import Any, Callable

from crafter.evaluator.normalizer import normalize_result


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


def _diagnose_first_response(agent: Any) -> bool:
    """Determine whether the agent can answer a basic prompt at all."""

    result = _safe_run(agent, "hello")
    return _has_meaningful_output(result)


def _diagnose_llm_connection(agent: Any) -> bool:
    """Determine whether the agent can answer a conversational prompt."""

    result = _safe_run(agent, "ping")
    output = str(result.get("output", "")).strip().lower()
    return bool(output)


def _diagnose_reasoning(agent: Any) -> bool:
    """Determine whether the agent can solve a trivial arithmetic prompt."""

    result = _safe_run(agent, "2+2")
    output = str(result.get("output", ""))
    return bool(re.search(r"\b4(\.0)?\b", output))


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


def _diagnose_memory_primer(agent: Any) -> bool:
    """Determine whether the agent returns a useful in-run memory mapping."""

    result = _safe_run(agent, "Store alpha=blue in memory.")
    memory = result.get("memory", {})
    if isinstance(memory, dict):
        memory_blob = " ".join(f"{key}:{value}" for key, value in memory.items()).lower()
        return "blue" in memory_blob or "alpha" in memory_blob
    return False


def _diagnose_persistent_memory(agent: Any) -> bool:
    """Determine whether the agent remembers a value across two calls.

    The first call stores a value in the agent's context. The second call asks
    for it back. We accept either the returned ``memory`` field or the output as
    evidence, because agents may expose memory differently.
    """

    # Two calls are necessary because memory is only meaningful when state is
    # preserved across separate invocations, not within a single response.
    _safe_run(agent, "Remember the value alpha=blue.")
    result = _safe_run(agent, "What is alpha?")

    memory = result.get("memory", {})
    output = str(result.get("output", "")).lower()

    if isinstance(memory, dict):
        memory_blob = " ".join(f"{key}:{value}" for key, value in memory.items()).lower()
        if "blue" in memory_blob or "alpha" in memory_blob:
            return True

    return "blue" in output or "alpha" in output


DIAGNOSTIC_FUNCTIONS: dict[str, Callable[[Any], bool]] = {
    "first_response": _diagnose_first_response,
    "llm_connection": _diagnose_llm_connection,
    "reasoning": _diagnose_reasoning,
    "tool_definition": _diagnose_tool_definition,
    "tool_execution": _diagnose_tool_execution,
    "memory_primer": _diagnose_memory_primer,
    "persistent_memory": _diagnose_persistent_memory,
}


def run_diagnostics(agent: Any) -> DiagnosticResult:
    """Run every capability diagnostic and return a stable boolean map."""

    results: DiagnosticResult = {}
    for name, diagnostic in DIAGNOSTIC_FUNCTIONS.items():
        try:
            results[name] = bool(diagnostic(agent))
        except Exception:
            # Diagnostics should never crash the learning platform.
            results[name] = False
    return results
