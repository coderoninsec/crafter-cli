"""ASCII renderers for simple banner and card views.

These helpers are intentionally plain. Crafter should feel guided and readable,
not like a terminal UI framework. The goal is to provide reusable presentation
primitives that remain easy to inspect and modify.
"""

from __future__ import annotations

from textwrap import wrap

from crafter.core.styles import DEFAULT_WIDTH, rule


def banner(title: str, width: int = DEFAULT_WIDTH) -> str:
    """Render a small banner for the top of a screen or section."""

    clean_title = title.strip()
    return "\n".join((rule(width), clean_title, rule(width)))


def brand_banner(subtitle: str = "AI Agent Training Lab", width: int = DEFAULT_WIDTH) -> str:
    """Render a lightweight Crafter brand banner."""

    art = [
        r"   _____                 __            ",
        r"  / ___/____  ____  ____/ /____  _____ ",
        r"  \__ \/ __ \/ __ \/ __  / ___/ / ___/ ",
        r" ___/ / /_/ / /_/ / /_/ / /    (__  )  ",
        r"/____/ .___/\____/\__,_/_/    /____/   ",
        r"    /_/                                ",
    ]
    centered_subtitle = subtitle.strip().center(width)
    return "\n".join((*art, "", centered_subtitle))


def stage_card(
    title: str,
    description: str,
    *,
    status: str | None = None,
    width: int = DEFAULT_WIDTH,
) -> str:
    """Render a compact ASCII card for a stage or educational milestone."""

    inner_width = max(10, width - 4)
    content_lines: list[str] = [title.strip()]
    if status:
        content_lines.append(status.strip())
    content_lines.extend(wrap(description.strip(), width=inner_width))

    border = "+" + "-" * (width - 2) + "+"
    rendered = [border]
    for content in content_lines:
        rendered.append(f"| {content.ljust(width - 4)} |")
    rendered.append(border)
    return "\n".join(rendered)


def roadmap_state_symbol(state: str) -> str:
    """Return the symbol used to mark a roadmap state."""

    mapping = {
        "completed": "✓",
        "current": "▶",
        "locked": "🔒",
    }
    return mapping.get(state, "•")
