from __future__ import annotations

import uuid
from typing import Optional

from app.config.indicator_config import PaperConfig
from app.core.enums import Direction
from app.core.models import Candle, PaperTrade, Signal
from app.paper_trading.portfolio import Portfolio
from app.utils.logging import logger


class PaperTrader:
    """Simulated account. PAPER TRADING — NO REAL MONEY."""

    def __init__(self, cfg: PaperConfig):
        self.cfg = cfg
        self.portfolio = Portfolio(cfg.starting_balance)
        self.enabled = True

    def on_signal(self, signal: Signal, candle: Candle) -> Optional[PaperTrade]:
        if not self.enabled:
            return None
        if signal.direction == Direction.WAIT:
            return None
        if self.portfolio.open:
            return None
        spread = self.cfg.spread_bps / 10_000.0
        fill = candle.close * (1 + spread if signal.direction == Direction.BUY else 1 - spread)
        trade = PaperTrade(
            id=str(uuid.uuid4()),
            signal_id=signal.id,
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            direction=signal.direction.value,
            entry_time=candle.timestamp,
            entry_price=fill,
            bars_held=0,
            status="OPEN",
        )
        self.portfolio.open.append(trade)
        logger.info("PAPER entry %s %s @ %s", trade.direction, trade.symbol, fill)
        return trade

    def on_candle(self, candle: Candle) -> Optional[PaperTrade]:
        if not self.portfolio.open:
            return None
        trade = self.portfolio.open[0]
        if trade.symbol != candle.symbol or trade.timeframe != candle.timeframe:
            return None
        trade.bars_held += 1
        if trade.bars_held < self.cfg.holding_bars:
            return None
        spread = self.cfg.spread_bps / 10_000.0
        px = candle.close * (1 - spread if trade.direction == "BUY" else 1 + spread)
        size = self.cfg.position_size
        if trade.direction == "BUY":
            pnl = (px - trade.entry_price) / trade.entry_price * size
        else:
            pnl = (trade.entry_price - px) / trade.entry_price * size
        trade.exit_time = candle.timestamp
        trade.exit_price = px
        trade.pnl = pnl
        trade.status = "CLOSED"
        self.portfolio.open.pop(0)
        self.portfolio.closed.append(trade)
        self.portfolio.cash += pnl
        self.portfolio.record_equity()
        logger.info("PAPER exit %s pnl=%.2f", trade.symbol, pnl)
        return trade

    def stats(self) -> dict:
        closed = self.portfolio.closed
        n = len(closed)
        wins = sum(1 for t in closed if t.pnl > 0)
        return {
            "mode": "PAPER TRADING — NO REAL MONEY",
            "balance": self.portfolio.cash,
            "starting": self.portfolio.starting,
            "open": len(self.portfolio.open),
            "closed": n,
            "win_rate": (wins / n) if n else None,
            "pnl": self.portfolio.cash - self.portfolio.starting,
            "drawdown": self.portfolio.drawdown(),
            "insufficient": n < 20,
        }
