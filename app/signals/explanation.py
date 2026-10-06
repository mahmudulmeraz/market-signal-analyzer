from __future__ import annotations

from app.core.enums import Direction
from app.core.models import Signal
from app.utils.helpers import fmt_price
from app.utils.time import format_dt


def explain(signal: Signal) -> str:
    lines = [
        f"PAIR          {signal.symbol}",
        f"TIMEFRAME     {signal.timeframe}",
        f"SIGNAL        {signal.direction.value}",
        f"SCORE         {signal.score:.1f}/100",
        f"STRENGTH      {signal.strength.value}",
        f"STATE         {signal.state.value}",
        f"PRICE         {fmt_price(signal.price)}",
        f"GENERATED     {format_dt(signal.timestamp)}",
        f"VALID UNTIL   {format_dt(signal.valid_until)}",
        "",
        "REASONS",
    ]
    if signal.reasons:
        lines.extend(f"  + {r}" for r in signal.reasons)
    else:
        lines.append("  (no confirming evidence)")
    lines.append("")
    lines.append("CONFLICTS / CAVEATS")
    if signal.conflicts:
        lines.extend(f"  ! {c}" for c in signal.conflicts)
    else:
        lines.append("  (none)")
    snap = signal.snapshot
    lines += [
        "",
        "INDICATOR SNAPSHOT",
        f"  RSI      {snap.rsi if snap.rsi is not None else '—'}  {snap.rsi_state}",
        f"  MA       {fmt_price(snap.ma)}  {snap.trend.value}",
        f"  BB       {snap.bb_state}",
        f"  Fractal  {snap.fractal}  confirmed={snap.fractal_confirmed}",
        f"  ZigZag   {snap.zigzag}  confirmed={snap.zigzag_confirmed}",
        "",
        "STATUS        PAPER / RESEARCH  — not a live order",
    ]
    if signal.direction == Direction.WAIT:
        lines.append("WAIT is a valid output. Low-quality setups are not forced.")
    return "\n".join(lines)
