from __future__ import annotations

from typing import List

from app.config.indicator_config import AppConfig
from app.core.models import Candle
from app.backtesting.engine import BacktestEngine
from app.backtesting.metrics import compute_metrics


def walk_forward(
    candles: List[Candle],
    cfg: AppConfig,
    train_size: int = 180,
    test_size: int = 60,
    step: int = 60,
) -> dict:
    """Rolling train→test. Each test window only uses past information."""
    engine = BacktestEngine(cfg)
    n = len(candles)
    windows = []
    start = 50
    while start + train_size + test_size <= n:
        train_end = start + train_size
        test_end = train_end + test_size
        test = engine.run(
            candles,
            start_index=train_end,
            end_index=test_end - 1,
            split="WALK_FORWARD",
        )
        windows.append(test)
        start += step
    all_trades = []
    all_sigs = []
    equity = [cfg.paper.starting_balance]
    cash = cfg.paper.starting_balance
    wait = 0
    for w in windows:
        all_trades.extend(w["trades"])
        all_sigs.extend(w["signals"])
        wait += w["metrics"]["wait_bars"]
        for t in w["trades"]:
            cash += t.pnl
            equity.append(cash)
    metrics = compute_metrics(all_trades, all_sigs, equity, wait, cfg.min_sample)
    return {"windows": windows, "aggregate": metrics, "equity": equity}
