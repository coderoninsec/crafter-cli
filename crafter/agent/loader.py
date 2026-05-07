"""Dynamic agent loading utilities.

Crafter evaluates external agent projects rather than code that lives inside
this package. The loader is responsible for turning a filesystem path into a
live Python object that implements the required interface.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from uuid import uuid4


class AgentLoadError(RuntimeError):
    """Raised when the target agent project cannot be loaded."""


def _load_module_from_path(module_path: Path) -> ModuleType:
    """Import ``app/agent.py`` from an arbitrary project directory.

    A unique module name is used on each load so repeated evaluations do not
    collide in ``sys.modules`` when users run multiple projects in one session.
    """

    module_name = f"crafter_loaded_agent_{uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise AgentLoadError(f"Could not create an import spec for {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys_path_entry = str(module_path.parent.parent)
    sys.path.insert(0, sys_path_entry)
    try:
        spec.loader.exec_module(module)
    finally:
        try:
            sys.path.remove(sys_path_entry)
        except ValueError:
            pass
    return module


def load_agent(path: str | Path) -> Any:
    """Load and instantiate ``Agent`` from ``<path>/app/agent.py``.

    The contract is intentionally strict so the platform has a single, clear
    integration point:

    ``class Agent:``
    ``    def run(self, input_text: str) -> dict``
    """

    root = Path(path).expanduser().resolve()
    module_path = root / "app" / "agent.py"

    # The platform only trusts one entry point in the user project so the
    # loading contract is obvious and easy to document.
    if not module_path.exists():
        raise AgentLoadError(f"Agent module not found: {module_path}")

    module = _load_module_from_path(module_path)
    agent_cls = getattr(module, "Agent", None)
    if agent_cls is None:
        raise AgentLoadError("The module must expose a class named Agent")

    try:
        agent = agent_cls()
    except Exception as exc:  # pragma: no cover - surfaced directly to the CLI
        raise AgentLoadError(f"Could not instantiate Agent: {exc}") from exc

    # The evaluator always calls ``run`` during diagnostics, so we fail early if
    # the contract is incomplete.
    run_method = getattr(agent, "run", None)
    if not callable(run_method):
        raise AgentLoadError("Agent must define a callable run(self, input_text) method")

    return agent
