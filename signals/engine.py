from __future__ import annotations

import uuid
from typing import List, Sequence

from app.config.indicator_config import AppConfig
from app.core.enums import Direction, SignalState, Strength
from app.core.models import Candle, Signal
from app.indicators.engine import IndicatorEngine
from app.signals.scorer import score_snapshot
from app.config.instruments import TIMEFRAMES


class SignalEngine:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.indicators = IndicatorEngine(cfg.indicators)

    def evaluate(self, candles: Sequence[Candle]) -> Signal:
        """Evaluate using only the provided candles (last bar = now)."""
        if not candles:
            raise ValueError("no candles")
        last = candles[-1]
        snap = self.indicators.snapshot(candles)
        score, reasons, conflicts = score_snapshot(snap, self.cfg.signal)
        direction = Direction.WAIT
        if score >= self.cfg.signal.buy_threshold:
            direction = Direction.BUY
        elif score <= self.cfg.signal.sell_threshold:
            direction = Direction.SELL
        strength = _strength(score, direction)
        tf_s = TIMEFRAMES.get(last.timeframe, 60)
        valid = last.timestamp + self.cfg.signal.validity_bars * tf_s * 1000
        state = SignalState.CONFIRMED if direction != Direction.WAIT else SignalState.DEVELOPING
        return Signal(
            id=str(uuid.uuid4()),
            symbol=last.symbol,
            timeframe=last.timeframe,
            timestamp=last.timestamp,
            direction=direction,
            strength=strength,
            score=score,
            reasons=reasons,
            conflicts=conflicts,
            snapshot=snap,
            state=state,
            price=last.close,
            valid_until=valid,
        )

    def evaluate_at(self, candles: List[Candle], index: int) -> Signal:
        """Causal evaluation at `index` using candles[0:index+1] only."""
        if index < 0 or index >= len(candles):
            raise IndexError("index out of range")
        return self.evaluate(candles[: index + 1])


def _strength(score: float, direction: Direction) -> Strength:
    if direction == Direction.WAIT:
        return Strength.NONE
    a = abs(score)
    if a >= 85:
        return Strength.STRONG
    if a >= 70:
        return Strength.MODERATE
    return Strength.WEAK
