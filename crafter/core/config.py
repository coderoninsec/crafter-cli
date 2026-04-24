import os

import yaml

CONFIG_FILE = "crafter.yml"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        raise ValueError(f"{CONFIG_FILE} not found")

    try:
        with open(CONFIG_FILE) as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {CONFIG_FILE}: {exc}") from exc

    if config is None:
        raise ValueError(f"{CONFIG_FILE} is empty")

    if not isinstance(config, dict):
        raise ValueError(f"{CONFIG_FILE} must contain a YAML object")

    if "stages" not in config:
        raise ValueError(f"{CONFIG_FILE} must define 'stages'")

    if not isinstance(config["stages"], list):
        raise ValueError(f"'stages' in {CONFIG_FILE} must be a list")

    return config
