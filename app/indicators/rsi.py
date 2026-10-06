"""Wilder RSI. Uses only the provided closed candles (no look-ahead)."""

from __future__ import annotations

from typing import List, Optional, Sequence


def rsi_series(closes: Sequence[float], period: int = 14) -> List[Optional[float]]:
    n = len(closes)
    out: List[Optional[float]] = [None] * n
    if n < period + 1 or period < 1:
        return out
    gains = 0.0
    losses = 0.0
    for i in range(1, period + 1):
        d = closes[i] - closes[i - 1]
        if d >= 0:
            gains += d
        else:
            losses -= d
    avg_g = gains / period
    avg_l = losses / period
    if avg_l == 0:
        out[period] = 100.0 if avg_g > 0 else 50.0
    else:
        rs = avg_g / avg_l
        out[period] = 100.0 - (100.0 / (1.0 + rs))
    for i in range(period + 1, n):
        d = closes[i] - closes[i - 1]
        g = d if d > 0 else 0.0
        l = -d if d < 0 else 0.0
        avg_g = (avg_g * (period - 1) + g) / period
        avg_l = (avg_l * (period - 1) + l) / period
        if avg_l == 0:
            out[i] = 100.0 if avg_g > 0 else 50.0
        else:
            rs = avg_g / avg_l
            out[i] = 100.0 - (100.0 / (1.0 + rs))
    return out


def interpret_rsi(value: Optional[float], prev: Optional[float], ob: float, os: float) -> str:
    if value is None:
        return "UNAVAILABLE"
    if value <= os:
        if prev is not None and value > prev:
            return "RECOVERING_OVERSOLD"
        return "OVERSOLD"
    if value >= ob:
        if prev is not None and value < prev:
            return "FADING_OVERBOUGHT"
        return "OVERBOUGHT"
    if prev is not None and value > prev:
        return "RISING"
    if prev is not None and value < prev:
        return "FALLING"
    return "NEUTRAL"
