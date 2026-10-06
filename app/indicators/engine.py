from __future__ import annotations

from typing import List, Optional, Sequence

from app.config.indicator_config import IndicatorConfig
from app.core.enums import TrendState
from app.core.models import Candle, IndicatorSnapshot
from app.indicators.bollinger import bandwidth, bollinger, interpret_bb, percent_b
from app.indicators.fractal import detect_fractals, last_confirmed
from app.indicators.moving_average import ma_series, trend_from_ma
from app.indicators.rsi import interpret_rsi, rsi_series
from app.indicators.zigzag import last_confirmed_zz, zigzag


class IndicatorEngine:
    def __init__(self, cfg: IndicatorConfig):
        self.cfg = cfg

    def snapshot(self, candles: Sequence[Candle]) -> IndicatorSnapshot:
        """Compute indicators on candles[:]. Last bar is the evaluation bar. No future bars exist here."""
        if not candles:
            return IndicatorSnapshot()
        closes = [c.close for c in candles]
        rsi_s = rsi_series(closes, self.cfg.rsi_period)
        rsi = rsi_s[-1]
        rsi_prev = rsi_s[-2] if len(rsi_s) >= 2 else None
        rsi_state = interpret_rsi(rsi, rsi_prev, self.cfg.rsi_overbought, self.cfg.rsi_oversold)

        mid, up, lo = bollinger(closes, self.cfg.bb_period, self.cfg.bb_std)
        prev_close = closes[-2] if len(closes) >= 2 else None
        bb_state = interpret_bb(closes[-1], prev_close, up[-1], mid[-1], lo[-1])

        ma_s = ma_series(closes, self.cfg.ma_period, self.cfg.ma_type)
        ma = ma_s[-1]
        ma_prev = ma_s[-2] if len(ma_s) >= 2 else None
        slope = None
        if ma is not None and ma_prev is not None:
            slope = ma - ma_prev
        trend = trend_from_ma(closes[-1], ma, ma_prev)

        fr = detect_fractals(list(candles), self.cfg.fractal_wings)
        last_fr = last_confirmed(fr)
        fractal_kind = last_fr.kind if last_fr else "NONE"

        zz = zigzag(list(candles), self.cfg.zigzag_deviation)
        last_zz = last_confirmed_zz(zz)
        zz_kind = "NONE"
        if last_zz:
            zz_kind = "BEARISH" if last_zz.kind == "HIGH" else "BULLISH"

        return IndicatorSnapshot(
            rsi=rsi,
            rsi_state=rsi_state,
            bb_upper=up[-1],
            bb_middle=mid[-1],
            bb_lower=lo[-1],
            bb_width=bandwidth(up[-1], lo[-1], mid[-1]),
            bb_position=percent_b(closes[-1], up[-1], lo[-1]),
            bb_state=bb_state,
            ma=ma,
            ma_slope=slope,
            trend=trend,
            fractal=fractal_kind,
            fractal_confirmed=last_fr is not None,
            zigzag=zz_kind,
            zigzag_confirmed=last_zz is not None,
        )

    def fractals(self, candles: Sequence[Candle]):
        return detect_fractals(list(candles), self.cfg.fractal_wings)

    def zigzags(self, candles: Sequence[Candle]):
        return zigzag(list(candles), self.cfg.zigzag_deviation)
