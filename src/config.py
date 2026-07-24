"""
config.py - Centralized configuration loader.

Single responsibility: read environment variables (from a local .env file
or the shell environment) and expose them as importable constants. No other
module should call os.environ directly.
"""

import os
from dotenv import load_dotenv

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(_BASE_DIR, ".env"))  # no-op if absent

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")

DATA_DIR = os.path.join(_BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "roastbot.db")
STATE_FILE = os.path.join(DATA_DIR, "state.json")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

REQUIRED_VARS = {
    "GITHUB_TOKEN": GITHUB_TOKEN,
    "GROQ_API_KEY": GROQ_API_KEY,
    "GITHUB_USERNAME": GITHUB_USERNAME,
}


def validate_config():
    """Raise a clear error if any required environment variable is missing."""
    missing = [name for name, value in REQUIRED_VARS.items() if not value]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Copy .env.example to .env and fill in real values."
        )