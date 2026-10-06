from __future__ import annotations

from typing import Dict, List, Optional

from app.core.models import Candle, Tick
from app.data.validator import validate_candle


class CandleBuilder:
    """Aggregates ticks into timeframe candles. Only closed candles are emitted."""

    def __init__(self, timeframe_seconds: int):
        self.tf_ms = timeframe_seconds * 1000
        self._current: Optional[Candle] = None

    def on_tick(self, tick: Tick, symbol: str, timeframe: str) -> Optional[Candle]:
        bucket = (tick.timestamp // self.tf_ms) * self.tf_ms
        if self._current is None or self._current.timestamp != bucket:
            closed = self._current
            self._current = Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=bucket,
                open=tick.last,
                high=tick.last,
                low=tick.last,
                close=tick.last,
                volume=0.0,
                is_closed=False,
            )
            if closed:
                closed.is_closed = True
                validate_candle(closed)
                return closed
            return None
        c = self._current
        c.high = max(c.high, tick.last)
        c.low = min(c.low, tick.last)
        c.close = tick.last
        return None


class SeriesStore:
    def __init__(self) -> None:
        self._data: Dict[str, List[Candle]] = {}

    def key(self, symbol: str, tf: str) -> str:
        return f"{symbol}|{tf}"

    def set(self, symbol: str, tf: str, candles: List[Candle]) -> None:
        self._data[self.key(symbol, tf)] = list(candles)

    def append(self, candle: Candle) -> None:
        k = self.key(candle.symbol, candle.timeframe)
        series = self._data.setdefault(k, [])
        if series and series[-1].timestamp == candle.timestamp:
            series[-1] = candle
            return
        series.append(candle)

    def get(self, symbol: str, tf: str) -> List[Candle]:
        return self._data.get(self.key(symbol, tf), [])
