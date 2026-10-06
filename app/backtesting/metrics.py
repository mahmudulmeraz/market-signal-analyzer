from __future__ import annotations

from typing import List, Sequence

from app.core.models import PaperTrade, Signal
from app.config.indicator_config import AppConfig


def compute_metrics(
    trades: Sequence[PaperTrade],
    signals: Sequence[Signal],
    equity: Sequence[float],
    wait_bars: int,
    min_sample: int,
) -> dict:
    closed = [t for t in trades if t.status == "CLOSED"]
    wins = [t for t in closed if t.pnl > 0]
    losses = [t for t in closed if t.pnl < 0]
    flats = [t for t in closed if t.pnl == 0]
    n = len(closed)
    insufficient = n < min_sample
    win_rate = (len(wins) / n) if n else None
    gp = sum(t.pnl for t in wins)
    gl = abs(sum(t.pnl for t in losses))
    pf = (gp / gl) if gl > 0 else (None if gp == 0 else float("inf"))
    net = sum(t.pnl for t in closed)
    peak = equity[0] if equity else 0.0
    max_dd = 0.0
    for e in equity:
        peak = max(peak, e)
        if peak:
            max_dd = max(max_dd, (peak - e) / peak)
    avg = net / n if n else 0.0
    largest_win = max((t.pnl for t in closed), default=0.0)
    largest_loss = min((t.pnl for t in closed), default=0.0)
    return {
        "total_trades": n,
        "wins": len(wins),
        "losses": len(losses),
        "flats": len(flats),
        "win_rate": win_rate,
        "net_pnl": net,
        "profit_factor": pf,
        "max_drawdown": max_dd,
        "average_trade": avg,
        "largest_win": largest_win if n else 0.0,
        "largest_loss": largest_loss if n else 0.0,
        "expectancy": avg,
        "signal_frequency": n / max(1, n + wait_bars),
        "buy_signals": sum(1 for s in signals if s.direction.value == "BUY"),
        "sell_signals": sum(1 for s in signals if s.direction.value == "SELL"),
        "wait_bars": wait_bars,
        "insufficient": insufficient,
    }


def format_win_rate(m: dict) -> str:
    if m.get("insufficient") or m.get("win_rate") is None:
        return "INSUFFICIENT SAMPLE SIZE"
    return f"{m['win_rate'] * 100:.1f}%"
