"""Shared project contract helpers for Crafter.

Crafter treats the learner project as part of the academy path, so the project
shape needs to be consistent across the doctor, evaluator, and roadmap. This
module keeps that shared contract in one small place.
"""

from __future__ import annotations

from pathlib import Path


REQUIRED_PROJECT_FILES = ("app/agent.py", "crafter.yml")


def project_structure_issues(project_root: Path) -> list[str]:
    """Return missing project files for the academy scaffold contract.

    Local setup is one milestone in the academy, so the evaluator and doctor
    both ask the same question: does the project have the files Crafter needs?
    """

    project_root = project_root.expanduser().resolve()
    issues: list[str] = []

    app_dir = project_root / "app"
    if not app_dir.exists():
        issues.append("app/ directory is missing")

    for relative_path in REQUIRED_PROJECT_FILES:
        path = project_root / relative_path
        if not path.exists():
            issues.append(relative_path)

    return issues


def project_structure_is_valid(project_root: Path) -> bool:
    """Return whether the learner project satisfies the scaffold contract."""

    return not project_structure_issues(project_root)
