from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from app.config.settings import DB_PATH, ensure_dirs


def connect(path: Optional[Path] = None) -> sqlite3.Connection:
    ensure_dirs()
    p = path or DB_PATH
    conn = sqlite3.connect(str(p), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
