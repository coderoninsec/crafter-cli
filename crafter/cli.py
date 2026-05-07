"""Command-line entry point for Crafter CLI.

The CLI should stay thin: it coordinates commands, loads the agent project,
and hands presentation off to ``crafter.core``. That keeps the user-facing
experience easy to evolve without mixing rendering into evaluation code.
"""

from __future__ import annotations

from pathlib import Path

import typer

from crafter.agent.loader import AgentLoadError, load_agent
from crafter.core.terminal import (
    render_create_help,
    render_create_overview,
    render_doctor_report,
    render_evaluation_report,
    render_explain_report,
    render_home_screen,
    render_hint_report,
    render_next_report,
    render_root_help,
    render_roadmap,
)
from crafter.doctor import summarize_checks, validate_project
from crafter.evaluator.runner import academy_preview_report
from crafter.evaluator.runner import evaluate_agent
from crafter.scaffold import ScaffoldError, create_agent_scaffold
from crafter.stages.definitions import resolve_stage


# ``pipx`` can keep old virtual environments around. If users reinstall a
# broken build, clearing the old environment is often necessary before this
# entry point is re-imported correctly.
app = typer.Typer(
    help=render_root_help(),
    invoke_without_command=True,
    no_args_is_help=False,
)
create_app = typer.Typer(
    help=render_create_help(),
    invoke_without_command=True,
    no_args_is_help=False,
)
app.add_typer(create_app, name="create")


def _load_and_evaluate(path: Path) -> dict:
    """Load the agent from disk and evaluate it against the stage ladder."""

    agent = load_agent(path)
    return evaluate_agent(agent, project_root=path)


@app.callback(invoke_without_command=True)
def _root_command(ctx: typer.Context) -> None:
    """Show the academy landing screen when the CLI is started without a command."""

    if ctx.invoked_subcommand is None and not ctx.resilient_parsing:
        print(render_home_screen())
        raise typer.Exit()


@app.command(help="Test your agent against the current academy stage.")
def test(
    path: Path = typer.Option(
        ...,
        "--path",
        "-p",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the agent project root.",
    ),
) -> None:
    try:
        report = _load_and_evaluate(path)
    except AgentLoadError as exc:
        print(f"Error: {exc}")
        raise typer.Exit(code=1)

    print(render_evaluation_report(report))

    if report["missing_capabilities"]:
        raise typer.Exit(code=1)


@app.command(help="Check your academy progress without failing the command.")
def status(
    path: Path = typer.Option(
        ...,
        "--path",
        "-p",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the agent project root.",
    ),
) -> None:
    try:
        report = _load_and_evaluate(path)
    except AgentLoadError as exc:
        print(f"Error: {exc}")
        raise typer.Exit(code=1)

    print(render_evaluation_report(report))


@app.command(help="View your AI agent learning roadmap.")
def stages(
    path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the learner project root.",
    ),
) -> None:
    try:
        report = _load_and_evaluate(path)
    except AgentLoadError:
        report = academy_preview_report()

    print(render_roadmap(report))


@app.command(help="See the next stage in your learning path.")
def next(
    path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the agent project root.",
    ),
) -> None:
    try:
        report = _load_and_evaluate(path)
    except AgentLoadError as exc:
        print(f"Error: {exc}")
        raise typer.Exit(code=1)

    print(render_next_report(report))


@app.command(help="Learn what a stage means in mentor-friendly language.")
def explain(stage: str = typer.Argument(..., help="Stage name, number, or capability.")) -> None:

    resolved = resolve_stage(stage)
    if resolved is None:
        print(f"Error: unknown stage '{stage}'")
        raise typer.Exit(code=1)

    print(render_explain_report(resolved))


@app.command(help="Check project readiness and local setup.")
def doctor(
    path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the agent project root.",
    ),
) -> None:
    checks = validate_project(path)
    summary = summarize_checks(checks)
    print(render_doctor_report(path, checks, summary))


@app.command(help="Get the next hint for your current academy stage.")
def hint(
    path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the agent project root.",
    ),
) -> None:
    try:
        report = _load_and_evaluate(path)
    except AgentLoadError as exc:
        print(f"Error: {exc}")
        raise typer.Exit(code=1)

    print(render_hint_report(report))


@create_app.callback(invoke_without_command=True)
def _create_root(ctx: typer.Context) -> None:
    """Show scaffold discovery when the user stops at `crafter create`."""

    if ctx.invoked_subcommand is None and not ctx.resilient_parsing:
        print(render_create_overview())
        raise typer.Exit()


@create_app.command("agent", help="Create a new AI agent training project.")
def create_agent(
    name: str = typer.Argument(..., help="Name of the starter agent project."),
) -> None:
    try:
        project_root = create_agent_scaffold(name)
    except ScaffoldError as exc:
        print(f"Error: {exc}")
        raise typer.Exit(code=1)

    print(f"Created starter agent scaffold at {project_root}")
    print("This scaffold is intentionally incomplete so the evaluator can guide")
    print("you through the learning stages.")


def main() -> None:
    """Entry point used by ``python -m`` and the ``crafter`` console script."""

    app()


if __name__ == "__main__":
    main()
