from pathlib import Path
import os
import sys

from app.config.indicator_config import AppConfig

APP_NAME = "SIGNAL TERMINAL"
APP_VERSION = "1.0.0"

def _writable_root() -> Path:
    # Installed/frozen builds keep the database and logs outside Program Files.
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / APP_NAME.replace(" ", "_")
    return Path(__file__).resolve().parents[2]

PROJECT_ROOT = _writable_root()
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
DB_PATH = DATA_DIR / "signal_terminal.db"

def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def default_config() -> AppConfig:
    return AppConfig()
