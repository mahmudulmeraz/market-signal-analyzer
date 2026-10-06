"""Bollinger Bands: SMA ± k * population-or-sample std of close. No look-ahead."""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple


def bollinger(
    closes: Sequence[float], period: int = 20, k: float = 2.0
) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    n = len(closes)
    mid: List[Optional[float]] = [None] * n
    up: List[Optional[float]] = [None] * n
    lo: List[Optional[float]] = [None] * n
    if n < period or period < 1:
        return mid, up, lo
    window_sum = sum(closes[:period])
    for i in range(period - 1, n):
        if i >= period:
            window_sum += closes[i] - closes[i - period]
        m = window_sum / period
        start = i - period + 1
        var = sum((closes[j] - m) ** 2 for j in range(start, i + 1)) / period
        sd = math.sqrt(max(0.0, var))
        mid[i] = m
        up[i] = m + k * sd
        lo[i] = m - k * sd
    return mid, up, lo


def bandwidth(upper: Optional[float], lower: Optional[float], middle: Optional[float]) -> Optional[float]:
    if upper is None or lower is None or middle is None or middle == 0:
        return None
    return (upper - lower) / middle


def percent_b(price: float, upper: Optional[float], lower: Optional[float]) -> Optional[float]:
    if upper is None or lower is None:
        return None
    span = upper - lower
    if span == 0:
        return 0.5
    return (price - lower) / span


def interpret_bb(
    price: float,
    prev: Optional[float],
    upper: Optional[float],
    middle: Optional[float],
    lower: Optional[float],
) -> str:
    if upper is None or lower is None or middle is None:
        return "UNAVAILABLE"
    pb = percent_b(price, upper, lower) or 0.5
    if prev is not None and prev <= lower and price > lower:
        return "LOWER_REJECTION"
    if prev is not None and prev >= upper and price < upper:
        return "UPPER_REJECTION"
    if price > upper:
        return "UPPER_BREAKOUT"
    if price < lower:
        return "LOWER_BREAKOUT"
    if pb > 0.8:
        return "NEAR_UPPER"
    if pb < 0.2:
        return "NEAR_LOWER"
    return "MID_RANGE"
