from __future__ import annotations

from typing import List, Tuple

from app.config.indicator_config import SignalConfig
from app.core.enums import TrendState
from app.core.models import IndicatorSnapshot
from app.utils.helpers import clamp


def score_snapshot(snap: IndicatorSnapshot, cfg: SignalConfig) -> Tuple[float, List[str], List[str]]:
    """Deterministic weighted score in [-100, 100]."""
    w = cfg.weights
    total = 0.0
    reasons: List[str] = []
    conflicts: List[str] = []

    rsi_w = w.get("rsi", 20)
    rsi_c = 0.0
    st = snap.rsi_state
    if st == "RECOVERING_OVERSOLD":
        rsi_c = rsi_w
        reasons.append("RSI recovering from oversold")
    elif st == "OVERSOLD":
        rsi_c = rsi_w * 0.45
        reasons.append("RSI in oversold region (not a standalone buy)")
    elif st == "FADING_OVERBOUGHT":
        rsi_c = -rsi_w
        reasons.append("RSI fading from overbought")
    elif st == "OVERBOUGHT":
        rsi_c = -rsi_w * 0.45
        reasons.append("RSI in overbought region (not a standalone sell)")
    elif st == "RISING":
        rsi_c = rsi_w * 0.25
    elif st == "FALLING":
        rsi_c = -rsi_w * 0.25
    elif st == "UNAVAILABLE":
        conflicts.append("RSI unavailable (insufficient bars)")
    total += rsi_c

    bb_w = w.get("bollinger", 20)
    bb_c = 0.0
    if snap.bb_state == "LOWER_REJECTION":
        bb_c = bb_w
        reasons.append("Bollinger: rejection from lower band")
    elif snap.bb_state == "UPPER_REJECTION":
        bb_c = -bb_w
        reasons.append("Bollinger: rejection from upper band")
    elif snap.bb_state == "UPPER_BREAKOUT":
        bb_c = bb_w * 0.5
        reasons.append("Bollinger: close above upper band")
    elif snap.bb_state == "LOWER_BREAKOUT":
        bb_c = -bb_w * 0.5
        reasons.append("Bollinger: close below lower band")
    elif snap.bb_state == "NEAR_LOWER":
        bb_c = bb_w * 0.2
    elif snap.bb_state == "NEAR_UPPER":
        bb_c = -bb_w * 0.2
    elif snap.bb_state == "UNAVAILABLE":
        conflicts.append("Bollinger unavailable")
    if snap.bb_width is not None and snap.bb_width < 0.01:
        conflicts.append("Low volatility (band contraction)")
        bb_c *= 0.7
    total += bb_c

    ma_w = w.get("moving_average", 20)
    ma_c = 0.0
    if snap.trend == TrendState.BULLISH:
        ma_c = ma_w
        reasons.append("Price above MA with non-negative slope (bullish context)")
    elif snap.trend == TrendState.BEARISH:
        ma_c = -ma_w
        reasons.append("Price below MA with non-positive slope (bearish context)")
    elif snap.trend == TrendState.SIDEWAYS:
        conflicts.append("Moving average: sideways / no clear trend")
    else:
        conflicts.append("Moving average trend unclear")
    total += ma_c

    fr_w = w.get("fractal", 20)
    if snap.fractal_confirmed and snap.fractal == "BULLISH":
        total += fr_w
        reasons.append("Confirmed bullish fractal")
    elif snap.fractal_confirmed and snap.fractal == "BEARISH":
        total -= fr_w
        reasons.append("Confirmed bearish fractal")
    else:
        conflicts.append("No confirmed fractal in current window")

    zz_w = w.get("zigzag", 20)
    if snap.zigzag_confirmed and snap.zigzag == "BULLISH":
        total += zz_w
        reasons.append("Confirmed ZigZag swing low supports upside structure")
    elif snap.zigzag_confirmed and snap.zigzag == "BEARISH":
        total -= zz_w
        reasons.append("Confirmed ZigZag swing high supports downside structure")
    else:
        conflicts.append("No confirmed ZigZag pivot yet")

    return clamp(total, -100.0, 100.0), reasons, conflicts
