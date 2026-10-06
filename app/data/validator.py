from __future__ import annotations

from typing import List, Tuple

from app.core.exceptions import DataValidationError
from app.core.models import Candle


def validate_candle(c: Candle) -> None:
    if c.high < c.low:
        raise DataValidationError("high < low")
    if c.high < max(c.open, c.close) or c.low > min(c.open, c.close):
        raise DataValidationError("OHLC envelope invalid")
    if c.timestamp <= 0:
        raise DataValidationError("invalid timestamp")
    if c.close <= 0 or c.open <= 0:
        raise DataValidationError("non-positive price")


def dedupe_sort(candles: List[Candle]) -> Tuple[List[Candle], int]:
    """Drop duplicates by timestamp, sort ascending. Returns (clean, dropped)."""
    seen = {}
    dropped = 0
    for c in candles:
        try:
            validate_candle(c)
        except DataValidationError:
            dropped += 1
            continue
        key = c.timestamp
        if key in seen:
            dropped += 1
            continue
        seen[key] = c
    ordered = [seen[k] for k in sorted(seen)]
    return ordered, dropped
