import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (one level up from backend/)
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_env_path)


def get_google_api_key() -> str:
    key = os.getenv("GOOGLE_API_KEY", "")
    if not key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. "
            "Add it to the .env file at the project root."
        )
    return key


# Expose for convenient import
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

# Model — override via GEMINI_MODEL in .env if needed
# e.g. GEMINI_MODEL=gemini-2.0-flash-lite
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Local CORS origins — frontend Vite dev server
CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
