"""Terminal rendering helpers for Crafter CLI.

This module is the shared presentation layer for the command-line experience.
Keeping renderers here lets the CLI stay thin while preserving a single place
to evolve the educational UX.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from crafter.core.ascii import brand_banner, roadmap_state_symbol, stage_card
from crafter.core.output import (
    bullet_lines,
    definition_list,
    failure_line,
    key_value,
    roadmap_stage_line,
    section_header,
    separator,
    success_line,
)
from crafter.core.progress import progress_bar, progress_percent, progress_summary
from crafter.stages.definitions import (
    STAGES,
    capability_label,
    stage_capability,
    stage_common_mistake,
    stage_description,
    stage_example,
    stage_explanation,
    stage_hint,
    stage_implementation_example,
    stage_minutes,
    stage_why_it_matters,
)


def _quick_start_block() -> str:
    """Render the recommended onboarding workflow."""

    return "\n".join(
        [
            "Quick Start",
            "",
            "1. Create your first agent",
            "   crafter create agent my-agent",
            "",
            "2. Enter the project",
            "   cd my-agent",
            "",
            "3. View your roadmap",
            "   crafter stages",
            "",
            "4. Start building",
            "   crafter hint",
        ]
    )


def render_root_help() -> str:
    """Render the top-level help text that introduces Crafter."""

    return "\n".join(
        [
            "Crafter is an AI Agent Training Lab.",
            "Learn to build AI agents progressively through stages.",
            "",
            _quick_start_block(),
            "",
            "Recommended workflow:",
            "- Create a project",
            "- Enter the project",
            "- View your roadmap",
            "- Start learning",
        ]
    )


def render_home_screen() -> str:
    """Render the no-arguments landing screen for new users."""

    return "\n".join(
        [
            separator(),
            brand_banner(),
            "",
            "CRAFTER — AI Agent Training Lab",
            "",
            "Learn to build AI agents progressively through stages.",
            "",
            "Start here:",
            "  crafter create agent my-agent",
            "",
            _quick_start_block(),
            separator(),
        ]
    )


def render_create_help() -> str:
    """Render the help text for the scaffold creation flow."""

    return "\n".join(
        [
            "Create a new AI agent training project.",
            "",
            "Available scaffolds:",
            definition_list(
                [
                    ("agent", "Create a new AI agent training project"),
                ]
            ),
            "",
            "Example:",
            "  crafter create agent my-agent",
        ]
    )


def render_create_overview() -> str:
    """Render the empty `crafter create` landing view."""

    return "\n".join(
        [
            separator(),
            brand_banner(),
            "",
            "Create your first project",
            "",
            "Available scaffolds:",
            definition_list(
                [
                    ("agent", "Create a new AI agent training project"),
                ]
            ),
            "",
            "Example:",
            "  crafter create agent my-agent",
            separator(),
        ]
    )


def _read_current_stage(project_root: Path | None = None) -> int:
    """Read the current academy stage from crafter.yml.

    The roadmap is a presentation layer, not a validator. If no project file is
    available, the experience starts at the first stage so the learner still
    sees a coherent academy path.
    """

    root = project_root or Path.cwd()
    config_path = root / "crafter.yml"
    if not config_path.exists():
        return 1

    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError:
        return 1

    match = re.search(r"current_stage\s*:\s*([0-9]+)", text)
    if not match:
        return 1

    current_stage = int(match.group(1))
    if current_stage <= 0:
        return 1
    return current_stage


def _roadmap_state(stage: dict[str, Any], current_order: int) -> str:
    """Return the visual state for a stage in the roadmap."""

    order = int(stage.get("academy_order", stage["id"]))
    if order < current_order:
        return "completed"
    if order == current_order:
        return "current"
    return "locked"


def _roadmap_header(total: int, current_order: int) -> str:
    """Render the roadmap heading and progress summary."""

    completed = max(0, min(current_order - 1, total))
    percent = progress_percent(completed, total)
    title_line = f"Build your Agent".ljust(40) + f"{percent}%"
    return "\n".join(
        [
            title_line,
            progress_bar(completed, total),
        ]
    )


def render_roadmap(
    stages: list[dict[str, Any]] = STAGES,
    *,
    project_root: Path | None = None,
) -> str:
    """Render the academy roadmap with visual stage states."""

    current_order = _read_current_stage(project_root)
    total = len(stages)

    lines = [
        separator(),
        brand_banner(),
        "",
        _roadmap_header(total, current_order),
        separator(),
        "",
    ]

    for index, stage in enumerate(stages):
        state = _roadmap_state(stage, current_order)
        symbol = roadmap_state_symbol(state)
        lines.append(
            roadmap_stage_line(
                symbol,
                stage["title"],
                stage_description(stage),
                stage_minutes(stage),
            )
        )
        if index < total - 1:
            lines.append("")

    lines.append(separator())
    return "\n".join(lines)


def render_stage_table(stages: list[dict[str, Any]] = STAGES) -> str:
    """Backward-compatible alias for the roadmap renderer."""

    return render_roadmap(stages)


def render_evaluation_report(report: dict[str, Any], stages: list[dict[str, Any]] = STAGES) -> str:
    """Render the full evaluation output."""

    total = len(stages)
    current_stage = report["current_stage"]
    diagnostics = report["diagnostics"]
    missing_capabilities = report["missing_capabilities"]

    lines = [
        section_header("Crafter Evaluation"),
        progress_summary(report["completed_stages"], total),
        "",
    ]

    if current_stage is None:
        lines.extend(
            [
                "Current Stage: complete",
                "All stages are complete.",
                "",
                "Diagnostics:",
            ]
        )
    else:
        lines.extend(
            [
                f"Current Stage: {current_stage['title']}",
                f"Description: {stage_description(current_stage)}",
                "",
                "Diagnostics:",
            ]
        )

    for key, value in diagnostics.items():
        lines.append(success_line(capability_label(key)) if value else failure_line(capability_label(key)))

    lines.append("")
    if current_stage is None:
        lines.extend(
            [
                "Missing Stage: None",
                "Hint:",
                "Your agent has completed all stages in the learning path.",
                "Example:",
                'Return: {"output": "done", "tools_used": [], "memory": {}}',
            ]
        )
        return "\n".join(lines)

    lines.append(f"Missing Stage: {current_stage['title']}")
    hint = stage_hint(current_stage)
    example = stage_example(current_stage)

    if hint:
        lines.extend(["Hint:", hint])

    if example:
        lines.extend(["Example:", "Return:", example])

    lines.append("")
    lines.append("Missing capabilities:")
    lines.append(
        bullet_lines(capability_label(capability) for capability in missing_capabilities)
        if missing_capabilities
        else "- None"
    )

    return "\n".join(lines)


def render_doctor_report(path: Path, checks: list[Any], summary: dict[str, Any]) -> str:
    """Render project validation results."""

    lines = [
        section_header("Crafter Doctor"),
        key_value("Project", path),
        key_value("Passed", summary["passed"]),
        key_value("Failed", summary["failed"]),
        "",
    ]

    for check in checks:
        lines.append(check.label)
        if check.reason:
            lines.append(f"Reason: {check.reason}")
        if check.fix:
            lines.append(f"Fix: {check.fix}")
        lines.append("")

    return "\n".join(lines).rstrip()


def render_next_report(report: dict[str, Any], stages: list[dict[str, Any]] = STAGES) -> str:
    """Render the next learning objective after the current stage."""

    completed_stage = report["current_stage"]
    next_stage = stages[report["completed_stages"]] if report["completed_stages"] < len(stages) else None

    if completed_stage is None:
        return "\n".join(
            [
                section_header("Crafter Next"),
                "Stage Completed: complete",
                "Unlocked Capability:",
                "Your agent has completed the learning path.",
                "Next Stage:",
                "None",
                "Goal:",
                "There is no next implementation target.",
            ]
        )

    lines = [
        section_header("Crafter Next"),
        f"Stage Completed: {completed_stage['title']}",
        f"Unlocked Capability: {stage_capability(completed_stage)}",
        "",
    ]

    if next_stage is None:
        lines.extend(
            [
                "Next Stage: complete",
                "Next Objective:",
                "Your agent has completed all stages in the learning path.",
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            f"Next Stage: {next_stage['title']}",
            f"Next Objective: {stage_description(next_stage)}",
        ]
    )

    next_hint = stage_hint(next_stage)
    next_example = stage_example(next_stage)

    if next_hint:
        lines.extend(["", "Next Implementation Target:", next_hint])

    if next_example:
        lines.extend(["", "Example:", next_example])

    return "\n".join(lines)


def render_explain_report(stage: dict[str, Any]) -> str:
    """Render a mentor-style explanation for one stage."""

    lines = [
        section_header(f"Stage: {stage['title']}"),
        stage_card(
            stage["title"],
            stage_description(stage),
            status=stage_hint(stage) or stage_capability(stage),
        ),
        f"What it means: {stage_explanation(stage)}",
    ]

    why_it_matters = stage_why_it_matters(stage)
    implementation_example = stage_implementation_example(stage)
    common_mistake = stage_common_mistake(stage)

    if why_it_matters:
        lines.extend(["", f"Why it matters: {why_it_matters}"])

    if implementation_example:
        lines.extend(["", "Implementation Example:", implementation_example])

    if common_mistake:
        lines.extend(["", f"Common Mistake: {common_mistake}"])

    return "\n".join(lines)


def render_hint_report(report: dict[str, Any]) -> str:
    """Render the contextual hint for the current stage."""

    completed_stage = report["current_stage"]
    if completed_stage is None:
        return "\n".join(
            [
                section_header("Crafter Hint"),
                "Current Stage: complete",
                "Explanation:",
                "Your agent has completed all stages in the learning path.",
            ]
        )

    lines = [
        section_header("Crafter Hint"),
        f"Current Stage: {completed_stage['title']}",
    ]

    explanation = stage_description(completed_stage)
    hint_text = stage_hint(completed_stage)
    example = stage_example(completed_stage)

    if explanation:
        lines.extend(["Explanation:", explanation])
    if hint_text:
        lines.extend(["Hint:", hint_text])
    if example:
        lines.extend(["Example:", example])

    return "\n".join(lines)
