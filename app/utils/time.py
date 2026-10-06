from datetime import datetime, timezone
from typing import Optional


def utc_now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def format_clock(ms: Optional[int] = None) -> str:
    if ms is None:
        dt = datetime.now()
    else:
        dt = datetime.fromtimestamp(ms / 1000.0)
    return dt.strftime("%H:%M:%S")


def format_dt(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
