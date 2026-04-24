from crafter.agent.tools import write


def run_agent(prompt):
    print(f"[agent] prompt: {prompt}")

    if "hello world" in prompt.lower():
        write("app/main.py", 'print("Hello World")')
        print("[agent] created app/main.py")
