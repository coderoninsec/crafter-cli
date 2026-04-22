import os, yaml

def load_config():
    if not os.path.exists("crafter.yml"):
        raise Exception("crafter.yml not found")

    with open("crafter.yml") as f:
        return yaml.safe_load(f)