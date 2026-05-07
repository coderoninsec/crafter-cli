"""Terminal rendering helpers for Crafter CLI.

This module is the shared presentation layer for the command-line experience.
Keeping renderers here lets the CLI stay thin while preserving a single place
to evolve the educational UX.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from crafter.core.ascii import brand_banner, roadmap_state_symbol
from crafter.core.output import (
    bullet_lines,
    definition_list,
    box_block,
    failure_line,
    key_value,
    numbered_lines,
    section_header,
    separator,
    stage_card,
    success_line,
)
from crafter.core.progress import progress_meter, progress_summary
from crafter.core.styles import BLUE, CYAN, GREEN, YELLOW, colorize, status_color
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


def _academy_intro() -> str:
    """Render the short motivational introduction shown across entry screens."""

    return "\n".join(
        [
            "Learn to build AI agents progressively through stages.",
            "",
            "Start your journey:",
            "  crafter create agent my-agent",
        ]
    )


def render_root_help() -> str:
    """Render the top-level help text that introduces Crafter."""

    return "\n".join(
        [
            colorize("Crafter is an AI Agent Training Lab.", BLUE, bold=True),
            _academy_intro(),
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

    title = colorize("CRAFTER — AI Agent Training Lab", CYAN, bold=True)
    return "\n".join(
        [
            separator(),
            brand_banner(),
            "",
            title,
            "",
            "Learn to build AI agents progressively through stages.",
            "",
            box_block(
                [
                    "Start your journey",
                    "crafter create agent my-agent",
                    "Then explore the roadmap and hints.",
                ],
                width=54,
                state="info",
            ),
            "",
            _quick_start_block(),
            "",
            "Why this matters:",
            "Crafter is designed to guide you step by step, not overwhelm you with technical noise.",
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
            colorize("Create your first project", CYAN, bold=True),
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


def _roadmap_state(stage: dict[str, Any], report: dict[str, Any]) -> str:
    """Return the visual state for a stage in the roadmap.

    The state comes from the academy report so the roadmap cannot drift away
    from the evaluator. A stage is completed only if it appears before the
    current stage in the sequential progression.
    """

    current_stage = report.get("current_stage")
    completed_stages = int(report.get("completed_stages", 0))
    order = int(stage.get("academy_order", stage["id"]))
    current_order = int(current_stage.get("academy_order", current_stage["id"])) if current_stage else None

    if current_stage is None and completed_stages >= len(STAGES):
        return "completed"

    if order <= completed_stages:
        return "completed"

    if current_order is not None and order == current_order:
        return "current"

    return "locked"


def _roadmap_header(total: int, completed: int) -> str:
    """Render the roadmap heading and progress summary."""

    return progress_meter("Build your Agent", completed, total, width=28)


def _preview_report_from_stages(stages: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a minimal preview report from the official stage definitions."""

    completed_stages = 0
    current_stage = None

    for stage in stages:
        if stage.get("check") is None:
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


def render_roadmap(report: dict[str, Any], stages: list[dict[str, Any]] = STAGES) -> str:
    """Render the academy roadmap with visual stage states."""

    total = len(stages)
    completed = max(0, min(int(report.get("completed_stages", 0)), total))
    current_stage = report.get("current_stage")

    lines = [
        separator(),
        brand_banner(),
        "",
        _roadmap_header(total, completed),
        separator(),
        "",
    ]

    for index, stage in enumerate(stages):
        state = _roadmap_state(stage, report)
        symbol = roadmap_state_symbol(state)

        card = stage_card(
            symbol,
            stage["title"],
            stage_description(stage),
            stage_minutes(stage),
            state=state,
        )
        lines.append(card)
        if state == "current":
            lines.append(
                colorize(
                    f"Current milestone: {stage['title']}",
                    YELLOW,
                    bold=True,
                )
            )
            lines.append("Next action:")
            lines.append("Open this stage and build toward the next unlock.")
            lines.append("")
        elif state == "completed":
            lines.append(
                colorize(
                    f"Unlocked: {stage['title']}",
                    GREEN,
                    bold=True,
                )
            )
            lines.append("")
        else:
            lines.append("")

    lines.append(separator())
    return "\n".join(lines)


def render_stage_table(stages: list[dict[str, Any]] = STAGES) -> str:
    """Backward-compatible alias for the roadmap renderer."""

    return render_roadmap(_preview_report_from_stages(stages), stages)


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
                box_block(
                    [
                        "Stage Complete: Your First Agent",
                        "You unlocked the full academy path.",
                        "Next steps:",
                        "Run crafter stages to review the full roadmap.",
                    ],
                    width=54,
                    state="completed",
                ),
                "",
            ]
        )
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

    current_stage = report["current_stage"]
    completed_count = int(report.get("completed_stages", 0))

    if current_stage is None:
        completed_stage = stages[-1] if stages else None
        next_stage = None
    else:
        completed_stage = stages[completed_count - 1] if completed_count > 0 else None
        next_stage = current_stage

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
        completion_card = box_block(
            [
                f"Stage Complete: {completed_stage['title']}",
                "You unlocked the next milestone in the academy.",
                "What to do next:",
                "Review the roadmap and keep progressing.",
            ],
            width=54,
            state="completed",
        )
        lines.extend(
            [
                "Next Stage: complete",
                "Next Objective:",
                "Your agent has completed all stages in the learning path.",
                "",
                completion_card,
            ]
        )
        return "\n".join(lines)

    unlock_steps = numbered_lines(
        [
            f"Open {stages[completed_count].get('title', 'the next stage')} in the roadmap.",
            f"Update app/agent.py to match the next milestone.",
            "Run crafter test --path . to confirm the unlock.",
        ]
    )

    unlock_card = box_block(
        [
            f"Stage Complete: {completed_stage['title']}",
            f"You unlocked: {next_stage['title']}",
            "",
            "Next steps:",
            *unlock_steps.splitlines(),
        ],
        width=54,
        state="completed",
    )

    lines.extend(
        [
            f"Next Stage: {next_stage['title']}",
            f"Next Objective: {stage_description(next_stage)}",
            "",
            unlock_card,
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
            roadmap_state_symbol("info"),
            stage["title"],
            stage_description(stage),
            stage_minutes(stage) or " ",
            state="info",
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
        f"Learning Goal: {stage_capability(completed_stage)}",
    ]

    explanation = stage_description(completed_stage)
    why_it_matters = stage_why_it_matters(completed_stage)
    hint_text = stage_hint(completed_stage)
    example = stage_implementation_example(completed_stage)

    if explanation:
        lines.extend(["Explanation:", explanation])
    if why_it_matters:
        lines.extend(["Why it matters:", why_it_matters])
    if hint_text:
        lines.extend(["Hint:", hint_text])
    if example:
        lines.extend(["Implementation Example:", example])

    lines.extend(
        [
            "",
            "Next Action:",
            "Edit app/agent.py and run crafter test again.",
        ]
    )

    return "\n".join(lines)
