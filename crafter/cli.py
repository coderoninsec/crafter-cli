import os
import subprocess
import sys

import typer
import yaml
from rich.console import Console
from rich.panel import Panel

from crafter.core.config import load_config
from crafter.evaluator.evaluator import evaluate

app = typer.Typer(help="Crafter CLI - Code Ronin")
console = Console()

CONFIG_FILE = "crafter.yml"
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


# -----------------------
# ENV CHECK
# -----------------------


def check_environment():
    if sys.prefix == sys.base_prefix:
        console.print(
            "[yellow]⚠ Running outside virtualenv (OK if using pipx)[/yellow]"
        )


# -----------------------
# HELPERS
# -----------------------


def header(title: str):
    console.print(Panel.fit(title, style="cyan"))


def ensure_project():
    if not os.path.exists(CONFIG_FILE):
        header("✖ Not a Crafter project")
        console.print("[blue]👉 Follow setup instructions from the web[/blue]")
        raise typer.Exit()


def get_current_stage(cfg):
    stage_id = cfg.get("stage", 1)
    for s in cfg.get("stages", []):
        if s["id"] == stage_id:
            return s
    return None


# -----------------------
# ASCII ART
# -----------------------


def show_banner():
    code = r"""
   ██████╗ ██████╗ ██████╗ ███████╗
  ██╔════╝██╔═══██╗██╔══██╗██╔════╝
  ██║     ██║   ██║██║  ██║█████╗
  ██║     ██║   ██║██║  ██║██╔══╝
  ╚██████╗╚██████╔╝██████╔╝███████╗
   ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
    """

    ronin = r"""
  ██████╗  ██████╗ ███╗   ██╗██╗███╗   ██╗
  ██╔══██╗██╔═══██╗████╗  ██║██║████╗  ██║
  ██████╔╝██║   ██║██╔██╗ ██║██║██╔██╗ ██║
  ██╔══██╗██║   ██║██║╚██╗██║██║██║╚██╗██║
  ██║  ██║╚██████╔╝██║ ╚████║██║██║ ╚████║
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝
    """

    console.print(f"[bold green]{code}[/bold green]")
    console.print(f"[bold green]{ronin}[/bold green]")


# -----------------------
# HELP
# -----------------------


@app.command()
def help():
    show_banner()

    header("📘 Crafter CLI")

    console.print("""
[cyan]Commands:[/cyan]

task        → Show current task
run         → Execute your solution
test        → Validate
complete    → Mark task as completed
next        → Move to next stage
status      → Show progress
doctor      → Check system
uninstall   → Remove Crafter CLI

[cyan]Flow:[/cyan]

crafter task
crafter run
crafter test
crafter complete
crafter next
""")


# -----------------------
# TASK
# -----------------------


@app.command()
def task():
    check_environment()
    ensure_project()

    try:
        cfg = load_config()
    except ValueError as exc:
        console.print(f"[red]✖ {exc}[/red]")
        raise typer.Exit(code=1)
    stage = get_current_stage(cfg)

    if not stage:
        console.print("[red]✖ Invalid stage config[/red]")
        return

    console.print(f"🎯 Stage: {stage['id']} - {stage['name']}")
    console.print(f"📌 Goal: {stage.get('description') or cfg.get('goal') or ''}")

    if "description" in stage:
        console.print(f"\n{stage['description']}")

    if "hint" in stage:
        console.print(f"\n[yellow]Hint:[/yellow] {stage['hint']}")

    console.print("\n[blue]👉 Flow:[/blue]")
    console.print("crafter run")
    console.print("crafter test")
    console.print("crafter complete")
    console.print("crafter next")


# -----------------------
# RUN
# -----------------------


@app.command()
def run():
    check_environment()
    ensure_project()

    run_script = os.path.abspath("run.sh")
    if not os.path.exists(run_script):
        raise typer.BadParameter("run.sh not found")

    try:
        result = subprocess.run(
            [run_script],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise typer.Exit(code=1) from exc

    output = result.stdout or ""
    if output:
        console.print(output, end="")

    if result.returncode != 0:
        raise typer.Exit(code=result.returncode)


# -----------------------
# TEST
# -----------------------


@app.command()
def test():
    check_environment()
    ensure_project()

    try:
        cfg = load_config()
    except ValueError as exc:
        console.print(f"[red]✖ {exc}[/red]")
        raise typer.Exit(code=1)

    stage = get_current_stage(cfg)

    if not stage:
        console.print("[red]✖ Invalid stage config[/red]")
        raise typer.Exit(code=1)

    run_script = os.path.abspath("run.sh")

    if not os.path.exists(run_script):
        console.print("[red]✘ FAIL[/red]")
        console.print("→ run.sh not found")
        raise typer.Exit(code=1)

    result = subprocess.run(
        ["bash", run_script, "test123"],
        capture_output=True,
        text=True,
    )

    output = result.stdout or ""
    checks = stage.get("checks", [])

    passed, error_message = evaluate(checks, output)

    header("🧪 Validation")

    if passed:
        console.print("[green]✔ PASS[/green]")
        return

    console.print("[red]✘ FAIL[/red]")
    if error_message:
        console.print(f"→ {error_message}")

    raise typer.Exit(code=1)


# -----------------------
# COMPLETE (MODIFICADO)
# -----------------------


@app.command()
def complete():
    check_environment()
    ensure_project()

    header("✅ Task Completed")

    console.print("[green]✔ Task completed locally[/green]")

    console.print("""
[yellow]⚠ Progress not synced[/yellow]

[cyan]Next step:[/cyan]

1. Open the platform
2. Mark this task as completed
3. Unlock the next stage

[blue]👉 https://securitycoder.vercel.app/crafter[/blue]
""")


# -----------------------
# NEXT
# -----------------------


@app.command()
def next():
    check_environment()
    ensure_project()

    try:
        cfg = load_config()
    except ValueError as exc:
        console.print(f"[red]✖ {exc}[/red]")
        raise typer.Exit(code=1)

    current = cfg.get("stage", 1)
    total = len(cfg.get("stages", []))

    if current >= total:
        header("🏁 Finished")
        console.print("[green]All stages completed[/green]")
        return

    cfg["stage"] = current + 1

    with open(CONFIG_FILE, "w") as f:
        yaml.dump(cfg, f)

    header("🎉 Stage Unlocked")
    console.print(f"[cyan]Progress:[/cyan] {cfg['stage']} / {total}")
    console.print("[blue]👉 Run: crafter task[/blue]")


# -----------------------
# STATUS
# -----------------------


@app.command()
def status():
    check_environment()
    ensure_project()

    try:
        cfg = load_config()
    except ValueError as exc:
        console.print(f"[red]✖ {exc}[/red]")
        raise typer.Exit(code=1)
    current = cfg.get("stage", 1)
    total = len(cfg.get("stages", []))

    header("📊 Progress")

    percent = int((current / total) * 100) if total else 0

    console.print(f"[cyan]Stage:[/cyan] {current}/{total}")
    console.print(f"[green]Progress:[/green] {percent}%")


# -----------------------
# DOCTOR
# -----------------------


@app.command()
def doctor():
    check_environment()

    header("🩺 System Check")

    if os.path.exists(CONFIG_FILE):
        console.print("[green]✔ crafter.yml found[/green]")
    else:
        console.print("[red]✖ Not inside project[/red]")

    console.print("[green]✔ CLI working[/green]")


# -----------------------
# UNINSTALL
# -----------------------


@app.command()
def uninstall():
    import subprocess

    header("🗑 Uninstalling Crafter")

    confirm = typer.confirm("Are you sure you want to uninstall Crafter?")
    if not confirm:
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit()

    try:
        subprocess.run(["pipx", "uninstall", "crafter"], check=True)
        console.print("[green]✔ Crafter removed successfully[/green]")
    except Exception as e:
        console.print("[red]✖ Failed to uninstall[/red]")
        console.print(str(e))


# -----------------------

if __name__ == "__main__":
    app()
