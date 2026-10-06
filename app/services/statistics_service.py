from __future__ import annotations

from typing import List, Optional

from app.core.models import PaperTrade, Signal


def summarize(signals: List[Signal], trades: List[PaperTrade], min_sample: int = 20) -> dict:
    buys = sum(1 for s in signals if s.direction.value == "BUY")
    sells = sum(1 for s in signals if s.direction.value == "SELL")
    waits = sum(1 for s in signals if s.direction.value == "WAIT")
    closed = [t for t in trades if t.status == "CLOSED"]
    n = len(closed)
    wr: Optional[float] = None
    if n >= min_sample:
        wr = sum(1 for t in closed if t.pnl > 0) / n
    scores = [s.score for s in signals]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    pnl = sum(t.pnl for t in closed)
    return {
        "total_signals": len(signals),
        "buy": buys,
        "sell": sells,
        "wait": waits,
        "win_rate": wr,
        "avg_score": avg_score,
        "paper_pnl": pnl,
        "closed_trades": n,
        "insufficient": n < min_sample,
    }
