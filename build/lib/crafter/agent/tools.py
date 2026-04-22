import os, subprocess

def read(path):
    with open(path) as f:
        return f.read()

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

def bash(cmd):
    return subprocess.getoutput(cmd)