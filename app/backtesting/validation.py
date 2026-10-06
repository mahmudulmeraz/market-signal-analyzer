from __future__ import annotations

from typing import List

from app.config.indicator_config import AppConfig
from app.core.models import Candle
from app.backtesting.engine import BacktestEngine


def train_validate_test(
    candles: List[Candle],
    cfg: AppConfig,
    train_frac: float = 0.6,
    val_frac: float = 0.2,
) -> dict:
    """Hold out a final test window. Never tune on the test set."""
    n = len(candles)
    a = int(n * train_frac)
    b = int(n * (train_frac + val_frac))
    engine = BacktestEngine(cfg)
    train = engine.run(candles, start_index=50, end_index=a - 1, split="IN_SAMPLE")
    val = engine.run(candles, start_index=a, end_index=b - 1, split="VALIDATION")
    test = engine.run(candles, start_index=b, end_index=n - 1, split="OUT_OF_SAMPLE")
    return {"train": train, "validation": val, "out_of_sample": test}
