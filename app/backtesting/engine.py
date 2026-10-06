"""Event-driven backtest. At bar i, only candles[0:i+1] are visible.

Entries fill at the NEXT bar's open to avoid using the same-bar close as a
fill after a close-based signal (no look-ahead).
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from app.config.indicator_config import AppConfig
from app.core.enums import Direction
from app.core.models import Candle, PaperTrade, Signal
from app.backtesting.metrics import compute_metrics
from app.signals.engine import SignalEngine


class BacktestEngine:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.signals = SignalEngine(cfg)

    def run(
        self,
        candles: List[Candle],
        start_index: int = 50,
        end_index: Optional[int] = None,
        split: str = "FULL",
    ) -> dict:
        end_index = end_index if end_index is not None else len(candles) - 1
        end_index = min(end_index, len(candles) - 1)
        warmup = max(start_index, self.cfg.indicators.bb_period + 5)
        equity = [self.cfg.paper.starting_balance]
        cash = self.cfg.paper.starting_balance
        size = self.cfg.paper.position_size
        hold = self.cfg.paper.holding_bars
        spread = self.cfg.paper.spread_bps / 10_000.0
        trades: List[PaperTrade] = []
        sigs: List[Signal] = []
        wait_bars = 0
        open_trade: Optional[PaperTrade] = None
        pending: Optional[Signal] = None

        i = warmup
        while i <= end_index:
            window = candles[: i + 1]
            bar = candles[i]

            if open_trade is not None:
                open_trade.bars_held += 1
                if open_trade.bars_held >= hold or i == end_index:
                    px = bar.open
                    if open_trade.direction == "BUY":
                        px *= 1 - spread
                        pnl = (px - open_trade.entry_price) / open_trade.entry_price * size
                    else:
                        px *= 1 + spread
                        pnl = (open_trade.entry_price - px) / open_trade.entry_price * size
                    open_trade.exit_time = bar.timestamp
                    open_trade.exit_price = px
                    open_trade.pnl = pnl
                    open_trade.status = "CLOSED"
                    cash += pnl
                    equity.append(cash)
                    trades.append(open_trade)
                    open_trade = None

            if pending is not None and open_trade is None:
                fill = bar.open
                if pending.direction == Direction.BUY:
                    fill *= 1 + spread
                else:
                    fill *= 1 - spread
                open_trade = PaperTrade(
                    id=str(uuid.uuid4()),
                    signal_id=pending.id,
                    symbol=bar.symbol,
                    timeframe=bar.timeframe,
                    direction=pending.direction.value,
                    entry_time=bar.timestamp,
                    entry_price=fill,
                    bars_held=0,
                    status="OPEN",
                )
                pending.outcome = "OPEN"
                pending = None

            sig = self.signals.evaluate(window)
            if sig.direction == Direction.WAIT:
                wait_bars += 1
            else:
                sigs.append(sig)
                if open_trade is None and pending is None:
                    pending = sig
            i += 1

        if open_trade is not None:
            last = candles[end_index]
            px = last.close
            if open_trade.direction == "BUY":
                pnl = (px - open_trade.entry_price) / open_trade.entry_price * size
            else:
                pnl = (open_trade.entry_price - px) / open_trade.entry_price * size
            open_trade.exit_time = last.timestamp
            open_trade.exit_price = px
            open_trade.pnl = pnl
            open_trade.status = "CLOSED"
            cash += pnl
            equity.append(cash)
            trades.append(open_trade)

        metrics = compute_metrics(trades, sigs, equity, wait_bars, self.cfg.min_sample)
        return {
            "split": split,
            "symbol": candles[0].symbol if candles else "",
            "timeframe": candles[0].timeframe if candles else "",
            "start": candles[warmup].timestamp if warmup < len(candles) else 0,
            "end": candles[end_index].timestamp if candles else 0,
            "metrics": metrics,
            "equity": equity,
            "trades": trades,
            "signals": sigs,
        }
