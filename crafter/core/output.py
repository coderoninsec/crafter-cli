"""Lightweight text rendering helpers for the CLI.

This module deliberately handles very small pieces of formatting. The goal is
to keep presentation code reusable without hiding the output flow behind an
abstraction layer.
"""

from __future__ import annotations

from collections.abc import Iterable

from crafter.core.styles import DEFAULT_WIDTH, rule, status_label


def section_header(title: str, width: int = DEFAULT_WIDTH) -> str:
    """Render a simple section header for terminal output."""

    clean_title = title.strip()
    return "\n".join((clean_title, rule(width)))


def separator(width: int = DEFAULT_WIDTH, char: str = "=") -> str:
    """Render a plain separator line."""

    return rule(width, char)


def bullet_lines(items: Iterable[str]) -> str:
    """Render a compact bullet list using standard ASCII markers."""

    lines = [f"- {item}" for item in items if str(item).strip()]
    return "\n".join(lines)


def numbered_lines(items: Iterable[str], *, start: int = 1) -> str:
    """Render a simple numbered list for onboarding copy."""

    lines: list[str] = []
    for index, item in enumerate(items, start=start):
        text = str(item).strip()
        if text:
            lines.append(f"{index}. {text}")
    return "\n".join(lines)


def key_value(label: str, value: object) -> str:
    """Render a single label/value pair."""

    return f"{label}: {value}"


def definition_list(items: Iterable[tuple[str, str]]) -> str:
    """Render a small label/description list for onboarding views."""

    lines: list[str] = []
    for label, description in items:
        clean_label = str(label).strip()
        clean_description = str(description).strip()
        if clean_label and clean_description:
            lines.append(f"* {clean_label.ljust(8)} {clean_description}")
    return "\n".join(lines)


def success_line(text: str) -> str:
    """Render a success message using Crafter's minimal status label."""

    return f"{status_label(True)} {text}"


def failure_line(text: str) -> str:
    """Render a failure message using Crafter's minimal status label."""

    return f"{status_label(False)} {text}"


def roadmap_stage_line(symbol: str, title: str, description: str, minutes: str) -> str:
    """Render one stage entry for the roadmap view."""

    lines = [f"{symbol} {title.strip()}", f"  {description.strip()}"]
    if minutes.strip():
        lines.append(f"  {minutes.strip()}")
    return "\n".join(lines)
