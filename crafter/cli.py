import os
import sys
import typer
import yaml

from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="Crafter CLI - Code Ronin")
console = Console()

CONFIG_FILE = "crafter.yml"


# -----------------------
# ENV CHECK
# -----------------------

def check_environment():
    if sys.prefix == sys.base_prefix:
        console.print("[yellow]⚠ Running outside virtualenv (OK if using pipx)[/yellow]")


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


def load_cfg():
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


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

    cfg = load_cfg()
    stage = get_current_stage(cfg)

    if not stage:
        console.print("[red]✖ Invalid stage config[/red]")
        return

    header("📌 Current Task")

    console.print(f"[cyan]Goal:[/cyan] {cfg.get('goal')}")
    console.print(f"[cyan]Stage:[/cyan] {stage['id']} - {stage['name']}")

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

    header("⚙ Running solution")

    console.print("[yellow]⚠ Simulation mode[/yellow]")
    console.print("[green]✔ Execution completed[/green]")


# -----------------------
# TEST
# -----------------------

@app.command()
def test():
    check_environment()
    ensure_project()

    header("🧪 Validation")

    console.print("[yellow]⚠ Manual validation required[/yellow]")
    console.print("[blue]👉 If correct: crafter complete[/blue]")


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

    with open(CONFIG_FILE) as f:
        cfg = yaml.safe_load(f)

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

    cfg = load_cfg()
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