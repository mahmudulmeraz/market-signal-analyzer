from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, List, Optional

from app.core.models import Candle


class MarketDataProvider(ABC):
    """Provider-independent interface. Strategy never imports a concrete provider."""

    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def is_simulated(self) -> bool: ...

    @abstractmethod
    def connect(self) -> bool: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def supported_symbols(self) -> List[str]: ...

    @abstractmethod
    def supported_timeframes(self) -> List[str]: ...

    @abstractmethod
    def get_historical_candles(self, symbol: str, timeframe: str, limit: int = 400) -> List[Candle]: ...

    @abstractmethod
    def get_latest_price(self, symbol: str) -> Optional[float]: ...

    @abstractmethod
    def subscribe(self, symbol: str, timeframe: str, callback: Callable[[Candle], None]) -> None: ...

    @abstractmethod
    def unsubscribe(self, symbol: str, timeframe: str) -> None: ...

    @abstractmethod
    def status_message(self) -> str: ...

    @abstractmethod
    def is_stale(self) -> bool: ...
