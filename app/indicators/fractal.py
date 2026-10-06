from __future__ import annotations

"""Williams fractals.

A 5-bar fractal (wings=2) at center index i is CONFIRMED only after bars
i+1 and i+2 have closed. At series end index t, the latest confirmable
center is t - wings. Unconfirmed centers are never used as historical truth.
"""

from typing import List, Optional, Sequence

from app.core.models import Candle, FractalPoint


def detect_fractals(candles: Sequence[Candle], wings: int = 2) -> List[FractalPoint]:
    n = len(candles)
    points: List[FractalPoint] = []
    if n < 2 * wings + 1 or wings < 1:
        return points
    last_confirmable = n - 1 - wings
    for i in range(wings, n - wings):
        lows = [candles[i + d].low for d in range(-wings, wings + 1) if d != 0]
        highs = [candles[i + d].high for d in range(-wings, wings + 1) if d != 0]
        is_bull = candles[i].low < min(lows)
        is_bear = candles[i].high > max(highs)
        confirmed = i <= last_confirmable
        if is_bull:
            points.append(
                FractalPoint(
                    index=i,
                    timestamp=candles[i].timestamp,
                    price=candles[i].low,
                    kind="BULLISH",
                    confirmed=confirmed,
                )
            )
        if is_bear:
            points.append(
                FractalPoint(
                    index=i,
                    timestamp=candles[i].timestamp,
                    price=candles[i].high,
                    kind="BEARISH",
                    confirmed=confirmed,
                )
            )
    return points


def last_confirmed(points: Sequence[FractalPoint], kind: Optional[str] = None) -> Optional[FractalPoint]:
    for p in reversed(points):
        if not p.confirmed:
            continue
        if kind is None or p.kind == kind:
            return p
    return None
