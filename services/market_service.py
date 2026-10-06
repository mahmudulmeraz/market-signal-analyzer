from __future__ import annotations

from typing import Callable, Dict, List, Optional

from app.config.instruments import PAIRS, TIMEFRAMES
from app.core.models import Candle
from app.data.candle_builder import SeriesStore
from app.data.providers.base import MarketDataProvider
from app.data.providers.live_provider import YahooLiveProvider
from app.data.providers.simulated import SimulatedProvider
from app.data.validator import dedupe_sort
from app.utils.logging import logger


def make_provider(mode: str) -> MarketDataProvider:
    if (mode or "").upper() == "LIVE":
        return YahooLiveProvider()
    return SimulatedProvider()


class MarketService:
    def __init__(self, provider: Optional[MarketDataProvider] = None, mode: str = "LIVE"):
        self.provider = provider or make_provider(mode)
        self.store = SeriesStore()

    def start(self) -> None:
        ok = self.provider.connect()
        logger.info("Market service start: %s", self.provider.status_message())
        if not ok:
            logger.warning("Live data did not connect. Check internet. Do not treat empty charts as prices.")

    def stop(self) -> None:
        self.provider.disconnect()

    def load(self, symbol: str, timeframe: str, limit: int = 400) -> List[Candle]:
        if symbol not in PAIRS:
            logger.warning("Unknown pair %s", symbol)
            return []
        if timeframe not in TIMEFRAMES:
            logger.warning("Unknown timeframe %s", timeframe)
            return []
        raw = self.provider.get_historical_candles(symbol, timeframe, limit)
        clean, dropped = dedupe_sort(raw)
        if dropped:
            logger.info("Dropped %s invalid/duplicate candles", dropped)
        self.store.set(symbol, timeframe, clean)
        if not clean:
            logger.warning(
                "DATA UNAVAILABLE: Provider does not currently support %s %s (or the request failed).",
                symbol,
                timeframe,
            )
        return clean

    def subscribe(self, symbol: str, timeframe: str, cb: Callable[[Candle], None]) -> None:
        def wrapped(c: Candle) -> None:
            self.store.append(c)
            cb(c)

        self.provider.subscribe(symbol, timeframe, wrapped)

    def prices(self) -> Dict[str, Optional[float]]:
        return {p: self.provider.get_latest_price(p) for p in PAIRS}

    def status(self) -> str:
        return self.provider.status_message()

    def simulated(self) -> bool:
        return self.provider.is_simulated()
