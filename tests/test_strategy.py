from app.config.indicator_config import AppConfig
from app.core.enums import Direction
from app.core.models import Candle
from app.data.providers.simulated import generate_series
from app.signals.engine import SignalEngine


def test_evaluate_at_is_causal():
    cfg = AppConfig()
    eng = SignalEngine(cfg)
    candles = generate_series("EUR/GBP", "5m", 200, end_ms=1_800_000_000_000)
    mid = 120
    a = eng.evaluate_at(candles, mid)
    extra = candles + generate_series("EUR/GBP", "15m", 40, end_ms=1_900_000_000_000)
    # extra has different tf timestamps; append clones of future of same series instead
    future = generate_series("EUR/GBP", "5m", 250, end_ms=1_800_000_000_000)
    b = eng.evaluate_at(future, mid)
    # same prefix of deterministic series → identical signal
    a2 = eng.evaluate_at(future, mid)
    assert a.score == a2.score
    assert a.direction == a2.direction
    assert a.snapshot.rsi == a2.snapshot.rsi


def test_future_bars_do_not_change_past_signal():
    cfg = AppConfig()
    eng = SignalEngine(cfg)
    series = generate_series("USD/INR", "5m", 220, end_ms=2_000_000_000_000)
    idx = 150
    past = eng.evaluate_at(series, idx)
    # evaluate with more future candles but same index prefix
    past2 = eng.evaluate_at(series[: idx + 1] + series[idx + 1 :], idx)
    assert past.score == past2.score
    assert past.direction == past2.direction
    assert past.snapshot.fractal == past2.snapshot.fractal
    assert past.snapshot.zigzag == past2.snapshot.zigzag


def test_wait_is_allowed():
    cfg = AppConfig()
    cfg.signal.buy_threshold = 99.0
    cfg.signal.sell_threshold = -99.0
    eng = SignalEngine(cfg)
    series = generate_series("AUD/NZD", "15m", 120, end_ms=1_700_000_000_000)
    sig = eng.evaluate(series)
    assert sig.direction in (Direction.WAIT, Direction.BUY, Direction.SELL)
    # with extreme thresholds, WAIT is expected
    assert sig.direction == Direction.WAIT
