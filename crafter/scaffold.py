"""Project scaffold generation for Crafter CLI.

This module creates starter agent projects that are intentionally incomplete.
The goal is to give learners a runnable baseline that passes the early stages
and fails later ones in a controlled way, so the evaluator can guide progress.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Iterable


class ScaffoldError(RuntimeError):
    """Raised when a project scaffold cannot be created safely."""


@dataclass(frozen=True)
class ScaffoldFile:
    """A file to create inside the generated project."""

    path: Path
    content: str


def _project_name_from_root(root: Path) -> str:
    """Return a stable project name for generated metadata."""

    return root.name


def _agent_py_content(project_name: str) -> str:
    """Return the intentionally incomplete starter agent implementation."""

    return dedent(
        f'''\
        """Training-lab agent for {project_name}.

        This file is intentionally incomplete. It starts with no solved
        capability logic so the evaluator can guide the learner step by step.
        """

        from __future__ import annotations

        class Agent:
            """Minimal agent contract required by Crafter."""

            def __init__(self) -> None:
                # TODO: implement persistent memory.
                # This scaffold intentionally starts with no retained state.
                self.memory: dict[str, str] = {{}}

            def run(self, input_text: str) -> dict:
                """Return the canonical Crafter response schema.

                TODO: implement the first learning stage yourself.
                TODO: add reasoning, tool usage, and durable memory later.
                This agent is intentionally incomplete for learning purposes.
                """

                return {{
                    "output": "",
                    "tools_used": [],
                    "memory": {{}},
                    "error": None,
                }}
        '''
    )


def _tools_py_content(project_name: str) -> str:
    """Return stub tool helpers for the starter project."""

    return dedent(
        f'''\
        """Tool stubs for {project_name}.

        This file is intentionally incomplete. It gives the learner a place to
        add real tools later, but it does not expose any working tool behavior
        yet.
        """

        from __future__ import annotations

        from typing import Any


        def list_tools() -> list[str]:
            """Return the names of tools available to the agent.

            TODO: register real tools here.
            The starter project deliberately returns an empty list so the
            tool stage fails until the learner implements tools.
            """

            return []


        def remember_tool(name: str, payload: Any) -> None:
            """Placeholder for a future tool-backed side effect.

            TODO: implement real persistence, validation, and error handling.
            """

            return None
        '''
    )


def _main_py_content(project_name: str) -> str:
    """Return a tiny executable entry point for the starter agent."""

    return dedent(
        f'''\
        """Command-line entry point for the {project_name} starter agent.

        The script is intentionally small so learners can run the scaffold
        immediately and see how the evaluator interacts with it.
        """

        from __future__ import annotations

        import argparse
        import sys
        from pathlib import Path

        if __package__ in (None, ""):
            sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

        from app.agent import Agent


        def main(argv: list[str] | None = None) -> int:
            """Run the starter agent from the command line."""

            parser = argparse.ArgumentParser(
                prog="{project_name}",
                description="Run the starter Crafter agent scaffold.",
            )
            parser.add_argument(
                "input_text",
                nargs="?",
                default="ping",
                help="Input text to send to the starter agent.",
            )
            args = parser.parse_args(argv)

            result = Agent().run(args.input_text)
            print(result["output"])
            return 0


        if __name__ == "__main__":
            raise SystemExit(main())
        '''
    )


def _readme_content(project_name: str) -> str:
    """Return a beginner-friendly README for the generated project."""

    return dedent(
        f'''\
        # {project_name}

        This project is a Crafter guided training lab.

        It intentionally starts at stage 1 with nothing implemented yet so the
        evaluator can guide you through the learning stages one by one.

        ## What you get

        - `app/agent.py`: the required `Agent` contract
        - `app/tools.py`: a placeholder for tool helpers
        - `app/main.py`: a tiny executable entry point
        - `tests/.gitkeep`: a placeholder test directory
        - `crafter.yml`: the project metadata used by the platform

        ## How to run the evaluator

        From the project root:

        ```bash
        crafter test --path .
        ```

        To inspect the learning ladder:

        ```bash
        crafter stages
        ```

        ## How progression works

        Crafter evaluates your agent in stages. This lab is meant to:

        - start with no completed stages
        - require you to implement `ping` -> `pong`
        - require you to implement reasoning
        - require you to implement tools
        - require you to implement memory

        Nothing is solved yet. The learner must build the agent progressively,
        stage by stage.

        ## Manual execution

        You can also run the starter agent directly:

        ```bash
        python app/main.py ping
        ```

        Try editing `app/agent.py` and `app/tools.py` as you move through the
        evaluator.
        '''
    )


def _license_content(project_name: str) -> str:
    """Return a simple starter license file."""

    return dedent(
        f'''\
        MIT License

        Copyright (c) 2026 {project_name}

        Permission is hereby granted, free of charge, to any person obtaining a
        copy of this software and associated documentation files (the
        "Software"), to deal in the Software without restriction, including
        without limitation the rights to use, copy, modify, merge, publish,
        distribute, sublicense, and/or sell copies of the Software, and to
        permit persons to whom the Software is furnished to do so, subject to
        the following conditions:

        The above copyright notice and this permission notice shall be included
        in all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
        OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
        MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
        IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
        CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
        TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
        SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
        '''
    )


def _crafter_yml_content(project_name: str) -> str:
    """Return the Crafter metadata file contents."""

    return dedent(
        f"""\
        name: {project_name}
        difficulty: beginner
        current_stage: 1
        """
    )


def _iter_scaffold_files(project_name: str) -> Iterable[ScaffoldFile]:
    """Yield the files that make up the starter project."""

    yield ScaffoldFile(Path("app/agent.py"), _agent_py_content(project_name))
    yield ScaffoldFile(Path("app/tools.py"), _tools_py_content(project_name))
    yield ScaffoldFile(Path("app/main.py"), _main_py_content(project_name))
    yield ScaffoldFile(Path("tests/.gitkeep"), "")
    yield ScaffoldFile(Path("crafter.yml"), _crafter_yml_content(project_name))
    yield ScaffoldFile(Path("README.md"), _readme_content(project_name))
    yield ScaffoldFile(Path("LICENSE"), _license_content(project_name))


def create_agent_scaffold(name: str, *, cwd: Path | None = None) -> Path:
    """Create a starter agent project and return its root directory.

    The generator intentionally refuses to overwrite existing paths.
    """

    base_dir = cwd or Path.cwd()
    requested_path = Path(name).expanduser()
    project_root = requested_path if requested_path.is_absolute() else base_dir / requested_path
    project_root = project_root.resolve()

    if project_root.exists():
        raise ScaffoldError(f"Refusing to overwrite existing path: {project_root}")

    project_root.mkdir(parents=True)

    project_name = _project_name_from_root(project_root)
    for scaffold_file in _iter_scaffold_files(project_name):
        file_path = project_root / scaffold_file.path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(scaffold_file.content, encoding="utf-8", newline="\n")

    return project_root
