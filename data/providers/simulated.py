"""Deterministic simulated OHLC. Always labeled SIMULATED DATA — never presented as live."""

from __future__ import annotations

import math
import threading
import time
from typing import Callable, Dict, List, Optional, Tuple

from app.config.instruments import BASE_PRICES, PAIR_SEEDS, PAIRS, TIMEFRAMES
from app.core.models import Candle
from app.data.providers.base import MarketDataProvider
from app.utils.logging import logger
from app.utils.time import utc_now_ms


def _mulberry(seed: int) -> Callable[[], float]:
    s = seed & 0xFFFFFFFF

    def rnd() -> float:
        nonlocal s
        s = (s + 0x6D2B79F5) & 0xFFFFFFFF
        t = (s ^ (s >> 15)) * (1 | s) & 0xFFFFFFFF
        t = ((t + ((t ^ (t >> 7)) * (61 | t))) ^ t) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0

    return rnd


def _gauss(rnd: Callable[[], float]) -> float:
    u = max(1e-12, rnd())
    v = max(1e-12, rnd())
    return math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * v)


def generate_series(symbol: str, timeframe: str, count: int, end_ms: Optional[int] = None) -> List[Candle]:
    if symbol not in BASE_PRICES:
        return []
    rnd = _mulberry(PAIR_SEEDS[symbol] + ord(timeframe[0]) * 17)
    step_ms = TIMEFRAMES.get(timeframe, 60) * 1000
    end_ms = end_ms or utc_now_ms()
    start = end_ms - count * step_ms
    price = BASE_PRICES[symbol]
    out: List[Candle] = []
    for i in range(count):
        open_p = price
        ret = 0.00002 + 0.0018 * _gauss(rnd)
        close_p = max(open_p * 0.2, open_p * math.exp(ret))
        high_p = max(open_p, close_p) * (1 + abs(_gauss(rnd)) * 0.0009)
        low_p = min(open_p, close_p) * (1 - abs(_gauss(rnd)) * 0.0009)
        out.append(
            Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=start + i * step_ms,
                open=open_p,
                high=high_p,
                low=low_p,
                close=close_p,
                volume=50 + rnd() * 200,
                is_closed=True,
            )
        )
        price = close_p
    return out


class SimulatedProvider(MarketDataProvider):
    def __init__(self, bar_interval_s: float = 1.8):
        self._bar_interval_s = bar_interval_s
        self._connected = False
        self._stale = True
        self._last_ms: Optional[int] = None
        self._prices: Dict[str, float] = dict(BASE_PRICES)
        self._subs: Dict[Tuple[str, str], List[Callable[[Candle], None]]] = {}
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._hist: Dict[Tuple[str, str], List[Candle]] = {}

    def name(self) -> str:
        return "simulated"

    def is_simulated(self) -> bool:
        return True

    def connect(self) -> bool:
        if self._connected:
            return True
        self._stop.clear()
        self._connected = True
        self._stale = False
        self._thread = threading.Thread(target=self._loop, daemon=True, name="sim-market")
        self._thread.start()
        logger.info("Simulated provider connected (SIMULATED DATA)")
        return True

    def disconnect(self) -> None:
        self._stop.set()
        self._connected = False
        self._stale = True
        logger.info("Simulated provider disconnected")

    def supported_symbols(self) -> List[str]:
        return list(PAIRS)

    def supported_timeframes(self) -> List[str]:
        return list(TIMEFRAMES.keys())

    def get_historical_candles(self, symbol: str, timeframe: str, limit: int = 400) -> List[Candle]:
        if symbol not in BASE_PRICES:
            return []
        key = (symbol, timeframe)
        series = generate_series(symbol, timeframe, max(limit, 80))
        with self._lock:
            self._hist[key] = series
            if series:
                self._prices[symbol] = series[-1].close
        return series[-limit:]

    def get_latest_price(self, symbol: str) -> Optional[float]:
        return self._prices.get(symbol)

    def subscribe(self, symbol: str, timeframe: str, callback: Callable[[Candle], None]) -> None:
        with self._lock:
            self._subs.setdefault((symbol, timeframe), []).append(callback)

    def unsubscribe(self, symbol: str, timeframe: str) -> None:
        with self._lock:
            self._subs.pop((symbol, timeframe), None)

    def status_message(self) -> str:
        if not self._connected:
            return "SIMULATED DATA — DISCONNECTED"
        if self._stale:
            return "SIMULATED DATA — STALE"
        return "SIMULATED DATA"

    def is_stale(self) -> bool:
        return self._stale or not self._connected

    def _loop(self) -> None:
        last_emit: Dict[Tuple[str, str], float] = {}
        while not self._stop.is_set():
            now = time.time()
            self._last_ms = utc_now_ms()
            self._stale = False
            with self._lock:
                items = list(self._subs.items())
            for key, cbs in items:
                if now - last_emit.get(key, 0) < self._bar_interval_s:
                    continue
                symbol, tf = key
                series = self._hist.get(key)
                if not series:
                    series = generate_series(symbol, tf, 80)
                    self._hist[key] = series
                prev = series[-1]
                nxt = self._next_from(prev)
                series.append(nxt)
                if len(series) > 800:
                    del series[:200]
                self._prices[symbol] = nxt.close
                for cb in cbs:
                    try:
                        cb(nxt)
                    except Exception as exc:
                        logger.error("Subscriber error: %s", exc)
                last_emit[key] = now
            time.sleep(0.2)

    def _next_from(self, prev: Candle) -> Candle:
        rnd = _mulberry((prev.timestamp ^ 7919) & 0xFFFFFFFF)
        open_p = prev.close
        close_p = max(open_p * 0.2, open_p * math.exp(0.00002 + 0.0018 * _gauss(rnd)))
        high_p = max(open_p, close_p) * (1 + abs(_gauss(rnd)) * 0.0009)
        low_p = min(open_p, close_p) * (1 - abs(_gauss(rnd)) * 0.0009)
        step_ms = TIMEFRAMES.get(prev.timeframe, 60) * 1000
        return Candle(
            symbol=prev.symbol,
            timeframe=prev.timeframe,
            timestamp=prev.timestamp + step_ms,
            open=open_p,
            high=high_p,
            low=low_p,
            close=close_p,
            volume=50 + rnd() * 200,
            is_closed=True,
        )
