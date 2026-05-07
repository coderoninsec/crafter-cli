"""Evaluation orchestration for Crafter CLI.

This module turns raw diagnostics into stage progression data. The CLI only
needs the final report, so this file centralizes the progression logic and keeps
the command layer thin.
"""

from __future__ import annotations

from typing import Any

from crafter.evaluator.diagnostics import run_diagnostics
from crafter.stages.definitions import STAGES


def _next_missing_capabilities(diagnostics: dict[str, bool]) -> list[str]:
    """Return the next unmet capability in the sequential stage ladder."""

    for stage in STAGES:
        check = stage["check"]
        if check is None:
            continue
        if diagnostics.get(check, False):
            continue
        return [check]
    return []


def current_failed_stage(report: dict[str, Any]) -> dict[str, Any] | None:
    """Return the first stage that still needs work for the given report."""

    completed_stages = int(report.get("completed_stages", 0))
    if completed_stages >= len(STAGES):
        return None
    return STAGES[completed_stages]


def evaluate_agent(agent: Any) -> dict[str, Any]:
    """Evaluate an agent against the stage ladder and return a full report."""

    diagnostics = run_diagnostics(agent)

    completed_stages = 0
    current_stage = STAGES[0] if STAGES else None

    for stage in STAGES:
        check = stage["check"]

        # Stages without a check are design/introductory stages and are always complete.
        if check is None:
            completed_stages += 1
            current_stage = stage
            continue

        if diagnostics.get(check, False):
            completed_stages += 1
            current_stage = stage
            continue

        break

    if completed_stages == len(STAGES):
        current_stage = None

    missing_capabilities = _next_missing_capabilities(diagnostics)

    return {
        "diagnostics": diagnostics,
        "completed_stages": completed_stages,
        "current_stage": current_stage,
        "missing_capabilities": missing_capabilities,
    }
