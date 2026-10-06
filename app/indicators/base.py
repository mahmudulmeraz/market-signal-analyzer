from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.core.models import Candle


class Indicator(ABC):
    name: str

    @abstractmethod
    def compute(self, candles: List[Candle]) -> Dict[str, Any]:
        """Use only candles passed in. Never look past the last bar."""
