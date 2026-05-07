"""Project and environment validation for Crafter CLI.

The doctor command is intentionally educational: it reports all problems in a
single pass, explains why each check matters, and suggests how to fix it.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from crafter.agent.loader import AgentLoadError, load_agent


@dataclass(frozen=True)
class DoctorCheck:
    """A single validation result."""

    label: str
    passed: bool
    reason: str
    fix: str


def _pass(label: str, reason: str = "", fix: str = "") -> DoctorCheck:
    return DoctorCheck(label=label, passed=True, reason=reason, fix=fix)


def _fail(label: str, reason: str, fix: str) -> DoctorCheck:
    return DoctorCheck(label=label, passed=False, reason=reason, fix=fix)


def _read_pyproject_dependencies(project_root: Path) -> list[str]:
    """Return declared dependency import names from pyproject.toml.

    This stays intentionally lightweight and uses only the standard library.
    """

    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        return []

    try:
        text = pyproject.read_text(encoding="utf-8")
    except OSError:
        return []

    match = re.search(r"dependencies\s*=\s*\[(.*?)\]", text, re.DOTALL)
    if not match:
        return []

    raw_items = match.group(1)
    names: list[str] = []
    for item in re.findall(r'"([^"]+)"', raw_items):
        name = re.split(r"[<>=!~\[]", item, maxsplit=1)[0].strip()
        if name:
            names.append(name)
    return names


def _module_available(module_name: str) -> bool:
    """Return whether a module can be imported in the current environment."""

    try:
        return importlib.util.find_spec(module_name) is not None
    except Exception:
        return False


def _load_agent_module(agent_path: Path):
    """Import app/agent.py so the doctor can inspect the contract directly."""

    module_name = f"crafter_doctor_agent_{uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, agent_path)
    if spec is None or spec.loader is None:
        raise AgentLoadError(f"Could not create an import spec for {agent_path}")

    module = importlib.util.module_from_spec(spec)
    sys_path_entry = str(agent_path.parent.parent)
    sys.path.insert(0, sys_path_entry)
    try:
        spec.loader.exec_module(module)
    finally:
        try:
            sys.path.remove(sys_path_entry)
        except ValueError:
            pass
    return module


def _check_structure(project_root: Path) -> DoctorCheck:
    """Validate the expected project layout."""

    app_dir = project_root / "app"
    if not app_dir.exists():
        return _fail(
            "[FAIL] project structure",
            "The app/ directory is missing, so Crafter cannot load the agent entry point.",
            "Create an app/ directory and place agent.py inside it.",
        )

    required = [app_dir / "agent.py", project_root / "crafter.yml"]
    missing = [path for path in required if not path.exists()]
    if missing:
        missing_names = ", ".join(path.relative_to(project_root).as_posix() for path in missing)
        return _fail(
            "[FAIL] project structure",
            f"Missing required files: {missing_names}.",
            "Create the missing files so the evaluator and loader can find the project contract.",
        )

    return _pass(
        "[PASS] project structure valid",
        "The project has the minimum files Crafter expects.",
        "No action needed.",
    )


def _check_agent_file(project_root: Path) -> DoctorCheck:
    agent_path = project_root / "app" / "agent.py"
    if agent_path.exists():
        return _pass("[PASS] app/agent.py exists")
    return _fail(
        "[FAIL] app/agent.py missing",
        "Crafter loads the agent from app/agent.py by convention.",
        "Create app/agent.py and define class Agent there.",
    )


def _check_crafter_yml(project_root: Path) -> DoctorCheck:
    config_path = project_root / "crafter.yml"
    if config_path.exists():
        return _pass("[PASS] crafter.yml exists")
    return _fail(
        "[FAIL] crafter.yml missing",
        "Crafter uses crafter.yml to track the project metadata and current stage.",
        "Create crafter.yml at the project root with the expected project fields.",
    )


def _check_agent_contract(project_root: Path) -> list[DoctorCheck]:
    """Check that the agent file exposes the required class and method."""

    checks: list[DoctorCheck] = []
    agent_path = project_root / "app" / "agent.py"

    try:
        module = _load_agent_module(agent_path)
    except AgentLoadError as exc:
        checks.append(
            _fail(
                "[FAIL] Agent class found",
                f"Crafter could not inspect app/agent.py: {exc}",
                "Fix the import or syntax error in app/agent.py, then rerun crafter doctor.",
            )
        )
        checks.append(
            _fail(
                "[FAIL] run() method found",
                "Crafter could not inspect the Agent contract because the module failed to load.",
                "Fix the module error in app/agent.py so the doctor can inspect the class definition.",
            )
        )
        checks.append(
            _fail(
                "[FAIL] evaluator can load the agent",
                "Crafter could not inspect the module, so the evaluator is unlikely to load it either.",
                "Fix the issue in app/agent.py and rerun crafter doctor.",
            )
        )
        return checks
    except Exception as exc:  # pragma: no cover - defensive reporting path
        checks.append(
            _fail(
                "[FAIL] Agent class found",
                f"An unexpected error occurred while importing app/agent.py: {exc}",
                "Fix the import or syntax issue in app/agent.py, then rerun crafter doctor.",
            )
        )
        checks.append(
            _fail(
                "[FAIL] run() method found",
                "Crafter could not inspect the Agent contract because the module failed to load.",
                "Fix the module error in app/agent.py so the doctor can inspect the class definition.",
            )
        )
        checks.append(
            _fail(
                "[FAIL] evaluator can load the agent",
                "Crafter could not inspect the module, so the evaluator is unlikely to load it either.",
                "Fix the issue in app/agent.py and rerun crafter doctor.",
            )
        )
        return checks

    agent_cls = getattr(module, "Agent", None)
    if agent_cls is not None:
        checks.append(
            _pass(
                "[PASS] Agent class found",
                "Crafter found the required Agent class.",
                "No action needed.",
            )
        )
    else:
        checks.append(
            _fail(
                "[FAIL] Agent class found",
                "The loaded object is not the expected Agent class.",
                "Define class Agent in app/agent.py.",
            )
        )

    run_method = getattr(agent_cls, "run", None) if agent_cls is not None else None
    if callable(run_method):
        checks.append(
            _pass(
                "[PASS] run() method found",
                "Crafter can call Agent.run(input_text) during evaluation.",
                "No action needed.",
            )
        )
    else:
        checks.append(
            _fail(
                "[FAIL] run() method missing",
                "The Agent class must expose a callable run(self, input_text) method.",
                "Add a run(self, input_text: str) -> dict method to app/agent.py.",
            )
        )

    try:
        load_agent(project_root)
    except AgentLoadError as exc:
        checks.append(
            _fail(
                "[FAIL] evaluator can load the agent",
                f"Crafter could not load the agent: {exc}",
                "Fix the import or contract issue in app/agent.py, then try again.",
            )
        )
    except Exception as exc:  # pragma: no cover - defensive reporting path
        checks.append(
            _fail(
                "[FAIL] evaluator can load the agent",
                f"An unexpected error occurred while loading the agent: {exc}",
                "Fix the exception in app/agent.py and rerun crafter doctor.",
            )
        )
    else:
        checks.append(
            _pass(
                "[PASS] evaluator can load the agent",
                "The loader was able to import and instantiate the Agent class.",
                "No action needed.",
            )
        )

    return checks


def _check_dependencies(project_root: Path) -> DoctorCheck:
    dependencies = _read_pyproject_dependencies(project_root)
    if not dependencies:
        return _pass(
            "[PASS] dependencies installed",
            "No declared runtime dependencies were found to validate.",
            "No action needed.",
        )

    missing = [name for name in dependencies if not _module_available(name)]
    if missing:
        joined = ", ".join(missing)
        return _fail(
            "[FAIL] dependencies installed",
            f"Missing importable dependency modules: {joined}.",
            "Install the missing dependencies in the active environment, then rerun crafter doctor.",
        )

    return _pass(
        "[PASS] dependencies installed",
        "All declared runtime dependencies are importable in the current environment.",
        "No action needed.",
    )


def validate_project(project_root: Path) -> list[DoctorCheck]:
    """Validate the current project and environment.

    The result is a full report; callers should render all checks, not stop on
    the first failure.
    """

    project_root = project_root.expanduser().resolve()
    checks: list[DoctorCheck] = []

    if not project_root.exists():
        checks.append(
            _fail(
                "[FAIL] project root exists",
                "The provided project path does not exist.",
                "Point crafter doctor at an existing project directory.",
            )
        )
        return checks

    checks.append(_check_agent_file(project_root))
    checks.append(_check_crafter_yml(project_root))
    checks.append(_check_structure(project_root))
    checks.extend(_check_agent_contract(project_root))
    checks.append(_check_dependencies(project_root))
    return checks


def summarize_checks(checks: list[DoctorCheck]) -> dict[str, Any]:
    """Return a simple summary for callers that want counts."""

    passed = sum(1 for check in checks if check.passed)
    failed = len(checks) - passed
    return {
        "passed": passed,
        "failed": failed,
        "checks": checks,
    }
