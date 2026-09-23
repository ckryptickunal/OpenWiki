"""Environment loading. Reads variable NAMES only; never logs values."""

from __future__ import annotations

import os
from pathlib import Path

PLACEHOLDER_KEYS = {
    "",
    "your-gemini-api-key-here",
    "your-youtube-data-api-key-here",
}


def load_dotenv_file(path: Path | None = None) -> None:
    """Load a .env if python-dotenv is installed. Missing file is a no-op."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        _load_dotenv_manual(path)
        return
    if path:
        load_dotenv(path)
    else:
        load_dotenv()


def _load_dotenv_manual(path: Path | None) -> None:
    candidate = path or Path.cwd() / ".env"
    if not candidate.exists():
        return
    for raw in candidate.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def env_value(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    stripped = value.strip()
    if stripped in PLACEHOLDER_KEYS:
        return None
    return stripped


def require_env(name: str, why: str) -> str:
    value = env_value(name)
    if not value:
        raise RuntimeError(f"Set {name} in .env or the environment. Needed for: {why}")
    return value
