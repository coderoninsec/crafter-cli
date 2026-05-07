"""Small style primitives for Crafter's terminal output.

These values keep the CLI consistent without introducing a heavyweight theming
system. Future contributors can extend the module with more labels if the
terminal UX grows.
"""

from __future__ import annotations

import os
import sys


DEFAULT_WIDTH = 60
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BLUE = "\033[34m"
RED = "\033[31m"
GRAY = "\033[90m"


def supports_color(stream: object | None = None) -> bool:
    """Return whether ANSI color is likely to render cleanly."""

    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True

    target = stream if stream is not None else sys.stdout
    return bool(getattr(target, "isatty", lambda: False)())


def colorize(text: str, color: str, *, bold: bool = False, enable: bool | None = None) -> str:
    """Wrap text in a minimal ANSI color sequence when supported."""

    if enable is None:
        enable = supports_color()
    if not enable:
        return text

    prefix = (BOLD if bold else "") + color
    return f"{prefix}{text}{RESET}"


def status_color(state: str) -> str:
    """Return the color used for a roadmap or status state."""

    mapping = {
        "completed": GREEN,
        "current": CYAN,
        "locked": GRAY,
        "failed": RED,
        "info": BLUE,
        "warning": YELLOW,
    }
    return mapping.get(state, GRAY)


def rule(width: int = DEFAULT_WIDTH, char: str = "=") -> str:
    """Return a plain divider line for section headers."""

    return char * max(1, width)


def status_label(passed: bool) -> str:
    """Return the smallest possible success/failure label."""

    return "[PASS]" if passed else "[FAIL]"
