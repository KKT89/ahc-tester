import os
import tomllib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_NAME = "config.toml"
CONFIG_FILE = os.path.join(SCRIPT_DIR, CONFIG_FILE_NAME)


def load_config():
    """Load config.toml placed alongside this module.

    Returns the parsed dict or None if missing (compat with existing callers).
    """
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} was not found. Please run setup.py first.")
        return None
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)


def config_path() -> str:
    return CONFIG_FILE

