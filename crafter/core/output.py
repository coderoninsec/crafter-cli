"""Lightweight text rendering helpers for the CLI.

This module deliberately handles very small pieces of formatting. The goal is
to keep presentation code reusable without hiding the output flow behind an
abstraction layer.
"""

from __future__ import annotations

from collections.abc import Iterable
from textwrap import wrap

from crafter.core.styles import DEFAULT_WIDTH, colorize, rule, status_color, status_label


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


def _visible_width(text: str) -> int:
    """Return a rough visible width for ASCII/ANSI-safe strings.

    Crafter keeps terminal rendering intentionally simple, so this uses a plain
    length-based estimate instead of a heavier text layout dependency.
    """

    return len(text)


def box_block(
    lines: Iterable[str],
    *,
    width: int = DEFAULT_WIDTH,
    state: str | None = None,
    enable_color: bool | None = None,
) -> str:
    """Render a lightweight terminal card with box drawing characters."""

    content = [str(line).rstrip() for line in lines]
    inner_width = max(18, width - 4)
    padded: list[str] = []

    for line in content:
        wrapped = wrap(line, width=inner_width) or [""]
        for chunk in wrapped:
            padded.append(chunk)

    longest = max((_visible_width(line) for line in padded), default=0)
    card_width = min(width, max(24, longest + 4))
    inner_width = card_width - 4

    top = f"╭{'─' * (card_width - 2)}╮"
    bottom = f"╰{'─' * (card_width - 2)}╯"
    state_color = status_color(state or "info")

    rendered: list[str] = [top]
    for line in padded:
        clean = line[:inner_width]
        rendered.append(f"│ {clean.ljust(inner_width)} │")
    rendered.append(bottom)

    if state:
        rendered = [colorize(line, state_color, enable=enable_color) for line in rendered]
    return "\n".join(rendered)


def stage_card(
    symbol: str,
    title: str,
    description: str,
    minutes: str,
    *,
    state: str = "info",
    width: int = DEFAULT_WIDTH,
    enable_color: bool | None = None,
) -> str:
    """Render a visual stage card for roadmap and unlock screens."""

    head = f"{symbol} {title}".rstrip()
    body = [head, description.strip(), minutes.strip()]
    return box_block(body, width=width, state=state, enable_color=enable_color)


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
