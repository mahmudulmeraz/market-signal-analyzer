from __future__ import annotations

from typing import List, Optional

from app.config.indicator_config import AppConfig
from app.core.models import Candle, Signal
from app.signals.engine import SignalEngine
from app.utils.time import utc_now_ms


class SignalService:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.engine = SignalEngine(cfg)
        self.history: List[Signal] = []
        self.current: Optional[Signal] = None

    def on_candles(self, candles: List[Candle]) -> Signal:
        sig = self.engine.evaluate(candles)
        now = candles[-1].timestamp if candles else utc_now_ms()
        if self.current and now > self.current.valid_until:
            self.current.state = self.current.state  # type: ignore
            self.current.outcome = self.current.outcome or "EXPIRED"
        if self.current is None or sig.timestamp != self.current.timestamp or sig.direction != self.current.direction:
            self.history.append(sig)
            if len(self.history) > 500:
                self.history = self.history[-400:]
        self.current = sig
        return sig
