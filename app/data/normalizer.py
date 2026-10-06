from __future__ import annotations

from typing import List

from app.core.models import Candle


def normalize_timestamps(candles: List[Candle], tf_seconds: int) -> List[Candle]:
    tf_ms = tf_seconds * 1000
    out: List[Candle] = []
    for c in candles:
        bucket = (c.timestamp // tf_ms) * tf_ms
        out.append(
            Candle(
                symbol=c.symbol,
                timeframe=c.timeframe,
                timestamp=bucket,
                open=c.open,
                high=c.high,
                low=c.low,
                close=c.close,
                volume=c.volume,
                is_closed=c.is_closed,
            )
        )
    return out
