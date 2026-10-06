from __future__ import annotations

"""Percent ZigZag.

A pivot is CONFIRMED only after price reverses by `deviation` percent from
the developing extreme. Until then the swing is DEVELOPING and must not be
treated as historical structure in signals or backtests.
"""

from typing import List, Optional, Sequence

from app.core.models import Candle, ZigZagPoint


def zigzag(candles: Sequence[Candle], deviation_pct: float = 0.6) -> List[ZigZagPoint]:
    n = len(candles)
    if n < 3:
        return []
    dev = deviation_pct / 100.0
    confirmed: List[ZigZagPoint] = []
    ext_idx = 0
    ext_price = candles[0].close
    direction = 0

    for i in range(1, n):
        price = candles[i].close
        if direction >= 0:
            if price > ext_price:
                ext_price = price
                ext_idx = i
            elif ext_price > 0 and (ext_price - price) / ext_price >= dev:
                confirmed.append(
                    ZigZagPoint(
                        index=ext_idx,
                        timestamp=candles[ext_idx].timestamp,
                        price=ext_price,
                        kind="HIGH",
                        confirmed=True,
                    )
                )
                direction = -1
                ext_price = price
                ext_idx = i
                continue
        if direction <= 0:
            if price < ext_price:
                ext_price = price
                ext_idx = i
            elif ext_price > 0 and (price - ext_price) / ext_price >= dev:
                confirmed.append(
                    ZigZagPoint(
                        index=ext_idx,
                        timestamp=candles[ext_idx].timestamp,
                        price=ext_price,
                        kind="LOW",
                        confirmed=True,
                    )
                )
                direction = 1
                ext_price = price
                ext_idx = i

    developing = ZigZagPoint(
        index=ext_idx,
        timestamp=candles[ext_idx].timestamp,
        price=ext_price,
        kind="HIGH" if direction >= 0 else "LOW",
        confirmed=False,
    )
    return confirmed + [developing]


def last_confirmed_zz(points: Sequence[ZigZagPoint]) -> Optional[ZigZagPoint]:
    for p in reversed(points):
        if p.confirmed:
            return p
    return None
