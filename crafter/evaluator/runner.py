"""Evaluation orchestration for Crafter CLI.

This module turns raw diagnostics into stage progression data. The CLI only
needs the final report, so this file centralizes the progression logic and keeps
the command layer thin.
"""

from __future__ import annotations

from pathlib import Path
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


def academy_preview_report() -> dict[str, Any]:
    """Return the roadmap state before a project has been evaluated.

    This keeps the academy discoverable for first-time users. The preview still
    comes from the official stage definitions, so it stays synchronized with the
    academy path instead of inventing its own order.
    """

    completed_stages = 0
    current_stage = None

    for stage in STAGES:
        check = stage["check"]
        if check is None:
            completed_stages += 1
            continue

        current_stage = stage
        break

    missing_capabilities = [current_stage["check"]] if current_stage and current_stage.get("check") else []

    return {
        "diagnostics": {},
        "completed_stages": completed_stages,
        "current_stage": current_stage,
        "missing_capabilities": missing_capabilities,
    }


def current_failed_stage(report: dict[str, Any]) -> dict[str, Any] | None:
    """Return the first stage that still needs work for the given report."""

    return report.get("current_stage")


def evaluate_agent(agent: Any, *, project_root: Path | None = None) -> dict[str, Any]:
    """Evaluate an agent against the academy ladder and return a full report.

    The evaluator does not invent its own order. It walks the official academy
    stages sequentially so the roadmap, diagnostics, and progression stay in
    sync.
    """

    diagnostics = run_diagnostics(agent, project_root=project_root)

    completed_stages = 0
    current_stage = None

    for stage in STAGES:
        check = stage["check"]

        # Stages without a check are academy milestones, not validator gates.
        # They complete automatically once the learner reaches this point in the
        # progression.
        if check is None:
            completed_stages += 1
            continue

        if diagnostics.get(check, False):
            completed_stages += 1
            continue

        current_stage = stage
        break

    if current_stage is None and completed_stages == len(STAGES):
        current_stage = None

    missing_capabilities = _next_missing_capabilities(diagnostics)

    return {
        "diagnostics": diagnostics,
        "completed_stages": completed_stages,
        "current_stage": current_stage,
        "missing_capabilities": missing_capabilities,
    }
