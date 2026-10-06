from __future__ import annotations

from typing import Iterable, List, Optional


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def last_n(values: List, n: int) -> List:
    if n <= 0:
        return []
    return values[-n:]


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    if b == 0:
        return default
    return a / b


def fmt_price(price: Optional[float], digits: int = 5) -> str:
    if price is None:
        return "—"
    if abs(price) >= 100:
        return f"{price:,.4f}"
    return f"{price:.{digits}f}"


def mean(xs: Iterable[float]) -> float:
    seq = list(xs)
    if not seq:
        return 0.0
    return sum(seq) / len(seq)
