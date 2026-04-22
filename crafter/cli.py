import typer
from crafter.core.config import load_config
from crafter.agent.loop import run_agent
from crafter.evaluator.evaluator import run_tests

app = typer.Typer()

@app.command()
def task():
    cfg = load_config()
    print(f"Goal: {cfg['goal']}")

@app.command()
def run(prompt: str):
    print("[agent] running...")
    run_agent(prompt)

@app.command()
def test():
    print("[test] running...")
    print(run_tests())

@app.command()
def submit():
    res = run_tests()
    print("✅ PASS" if res == "PASS" else "❌ FAIL")

if __name__ == "__main__":
    app()