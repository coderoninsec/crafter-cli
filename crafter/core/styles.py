"""Small style primitives for Crafter's terminal output.

These values keep the CLI consistent without introducing a heavyweight theming
system. Future contributors can extend the module with more labels if the
terminal UX grows.
"""

from __future__ import annotations


DEFAULT_WIDTH = 60


def rule(width: int = DEFAULT_WIDTH, char: str = "=") -> str:
    """Return a plain divider line for section headers."""

    return char * max(1, width)


def status_label(passed: bool) -> str:
    """Return the smallest possible success/failure label."""

    return "[PASS]" if passed else "[FAIL]"

