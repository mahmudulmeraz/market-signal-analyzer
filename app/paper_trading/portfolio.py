from __future__ import annotations

from typing import List

from app.core.models import PaperTrade


class Portfolio:
    def __init__(self, starting_balance: float):
        self.starting = starting_balance
        self.cash = starting_balance
        self.open: List[PaperTrade] = []
        self.closed: List[PaperTrade] = []
        self.equity_curve: List[float] = [starting_balance]
        self.peak = starting_balance

    def equity(self) -> float:
        return self.cash

    def drawdown(self) -> float:
        if self.peak <= 0:
            return 0.0
        return (self.peak - self.cash) / self.peak

    def record_equity(self) -> None:
        self.equity_curve.append(self.cash)
        self.peak = max(self.peak, self.cash)
