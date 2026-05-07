"""Small progress helpers for stage-oriented terminal feedback.

Crafter is educational, so progress should be visible and easy to read. The
helpers here stay intentionally tiny so they can be reused in future terminal
views without turning into a framework.
"""

from __future__ import annotations


def progress_percent(completed: int, total: int) -> int:
    """Return a rounded completion percentage."""

    if total <= 0:
        return 100
    completed = max(0, min(completed, total))
    return int(round((completed / total) * 100))


def progress_bar(
    completed: int,
    total: int,
    width: int = 24,
    *,
    fill_char: str = "█",
    empty_char: str = "░",
) -> str:
    """Render a tiny terminal-friendly progress bar."""

    width = max(1, width)
    if total <= 0:
        return fill_char * width

    completed = max(0, min(completed, total))
    filled = int(round((completed / total) * width))
    filled = max(0, min(width, filled))
    return (fill_char * filled) + (empty_char * (width - filled))


def progress_summary(completed: int, total: int) -> str:
    """Render a concise progress summary for the CLI."""

    percent = progress_percent(completed, total)
    bar = progress_bar(completed, total, width=28)
    return f"Progress: {completed} / {total} stages  {percent}%\n{bar}"


def progress_meter(label: str, completed: int, total: int, *, width: int = 28) -> str:
    """Render a polished label + percent + progress bar block."""

    percent = progress_percent(completed, total)
    label_width = max(24, 40 - len(str(percent)))
    header = f"{label.strip():<{label_width}} {percent:>3}%"
    return f"{header}\n{progress_bar(completed, total, width=width)}"
