import os, subprocess
from crafter.core.config import load_config

def run_tests():
    cfg = load_config()

    for c in cfg.get("checks", []):
        if c["type"] == "file_exists":
            if not os.path.exists(c["path"]):
                return "FAIL"

        elif c["type"] == "file_contains":
            with open(c["path"]) as f:
                if c["content"] not in f.read():
                    return "FAIL"

        elif c["type"] == "run_command":
            out = subprocess.getoutput(c["command"])
            if c["expected_output"] not in out:
                return "FAIL"

    return "PASS"