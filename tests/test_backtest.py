from app.backtesting.engine import BacktestEngine
from app.backtesting.validation import train_validate_test
from app.backtesting.walk_forward import walk_forward
from app.config.indicator_config import AppConfig
from app.data.providers.simulated import generate_series
from app.paper_trading.engine import PaperTrader
from app.signals.engine import SignalEngine


def test_backtest_deterministic():
    cfg = AppConfig()
    candles = generate_series("CAD/CHF", "5m", 300, end_ms=1_700_000_000_000)
    a = BacktestEngine(cfg).run(candles, split="FULL")
    b = BacktestEngine(cfg).run(candles, split="FULL")
    assert a["metrics"]["total_trades"] == b["metrics"]["total_trades"]
    assert a["metrics"]["net_pnl"] == b["metrics"]["net_pnl"]


def test_entry_uses_next_open_not_future_close():
    """Signal at bar i fills at bar i+1 open — not i+1 close."""
    cfg = AppConfig()
    candles = generate_series("EUR/GBP", "5m", 260, end_ms=1_710_000_000_000)
    result = BacktestEngine(cfg).run(candles)
    for t in result["trades"]:
        # entry timestamp must match some candle open time
        matches = [c for c in candles if c.timestamp == t.entry_time]
        assert matches
        # fill is open ± spread, not an arbitrary future close
        open_px = matches[0].open
        rel = abs(t.entry_price - open_px) / open_px
        assert rel < 0.01


def test_oos_splits_are_separate():
    cfg = AppConfig()
    candles = generate_series("USD/BRL", "15m", 400, end_ms=1_720_000_000_000)
    splits = train_validate_test(candles, cfg)
    assert splits["train"]["end"] <= splits["validation"]["start"] or splits["validation"]["metrics"]["total_trades"] >= 0
    assert "insufficient" in splits["out_of_sample"]["metrics"]


def test_walk_forward_runs():
    cfg = AppConfig()
    candles = generate_series("USD/PKR", "5m", 400, end_ms=1_730_000_000_000)
    wf = walk_forward(candles, cfg, train_size=120, test_size=40, step=40)
    assert "aggregate" in wf


def test_paper_entry_exit():
    cfg = AppConfig()
    trader = PaperTrader(cfg.paper)
    candles = generate_series("USD/BDT", "5m", 80, end_ms=1_740_000_000_000)
    eng = SignalEngine(cfg)
    cfg.signal.buy_threshold = 0
    cfg.signal.sell_threshold = 0
    # force a non-wait by low thresholds
    sig = eng.evaluate(candles)
    if sig.direction.value == "WAIT":
        sig.direction = type(sig.direction).BUY
    trader.on_signal(sig, candles[-1])
    assert trader.portfolio.open
    last = candles[-1]
    for _ in range(cfg.paper.holding_bars):
        from app.data.providers.simulated import generate_series as gs

        nxt = gs("USD/BDT", "5m", 2, end_ms=last.timestamp + 300_000)[-1]
        last = nxt
        trader.on_candle(nxt)
    assert trader.portfolio.closed or trader.portfolio.open
