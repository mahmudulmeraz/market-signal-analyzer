from __future__ import annotations

from typing import List, Optional, Sequence

from app.core.enums import TrendState


def sma(values: Sequence[float], period: int) -> List[Optional[float]]:
    n = len(values)
    out: List[Optional[float]] = [None] * n
    if period < 1 or n < period:
        return out
    s = sum(values[:period])
    out[period - 1] = s / period
    for i in range(period, n):
        s += values[i] - values[i - period]
        out[i] = s / period
    return out


def ema(values: Sequence[float], period: int) -> List[Optional[float]]:
    n = len(values)
    out: List[Optional[float]] = [None] * n
    if period < 1 or n < period:
        return out
    k = 2.0 / (period + 1)
    seed = sum(values[:period]) / period
    out[period - 1] = seed
    prev = seed
    for i in range(period, n):
        prev = values[i] * k + prev * (1 - k)
        out[i] = prev
    return out


def ma_series(values: Sequence[float], period: int, kind: str = "EMA") -> List[Optional[float]]:
    if kind.upper() == "SMA":
        return sma(values, period)
    return ema(values, period)


def trend_from_ma(price: float, ma_val: Optional[float], prev_ma: Optional[float], band: float = 0.0004) -> TrendState:
    if ma_val is None:
        return TrendState.UNCLEAR
    slope = 0.0 if prev_ma is None else (ma_val - prev_ma) / ma_val if ma_val else 0.0
    if abs(slope) < band and abs(price - ma_val) / ma_val < band * 4:
        return TrendState.SIDEWAYS
    if price > ma_val and slope >= 0:
        return TrendState.BULLISH
    if price < ma_val and slope <= 0:
        return TrendState.BEARISH
    return TrendState.UNCLEAR
