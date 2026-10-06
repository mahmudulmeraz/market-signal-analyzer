from dataclasses import dataclass, field
from typing import Dict


@dataclass
class IndicatorConfig:
    rsi_period: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0
    bb_period: int = 20
    bb_std: float = 2.0
    ma_type: str = "EMA"
    ma_period: int = 20
    zigzag_deviation: float = 0.6
    fractal_wings: int = 2


@dataclass
class SignalConfig:
    weights: Dict[str, int] = field(
        default_factory=lambda: {
            "rsi": 20,
            "bollinger": 20,
            "moving_average": 20,
            "fractal": 20,
            "zigzag": 20,
        }
    )
    buy_threshold: float = 55.0
    sell_threshold: float = -55.0
    validity_bars: int = 3


@dataclass
class PaperConfig:
    starting_balance: float = 10_000.0
    position_size: float = 1_000.0
    holding_bars: int = 5
    spread_bps: float = 2.0


@dataclass
class AppConfig:
    indicators: IndicatorConfig = field(default_factory=IndicatorConfig)
    signal: SignalConfig = field(default_factory=SignalConfig)
    paper: PaperConfig = field(default_factory=PaperConfig)
    data_mode: str = "LIVE"
    default_pair: str = "EUR/GBP"
    default_timeframe: str = "5m"
    live_bar_ms: int = 1800
    min_sample: int = 20
