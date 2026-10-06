from app.core.models import Candle
from app.indicators.bollinger import bollinger
from app.indicators.fractal import detect_fractals
from app.indicators.moving_average import ema, sma
from app.indicators.rsi import rsi_series
from app.indicators.zigzag import zigzag


def _candles(closes):
    out = []
    for i, c in enumerate(closes):
        out.append(
            Candle(
                "EUR/GBP",
                "5m",
                1_700_000_000_000 + i * 300_000,
                c,
                c + 0.0002,
                c - 0.0002,
                c,
                10,
            )
        )
    return out


def test_sma_known():
    v = [1, 2, 3, 4, 5]
    s = sma(v, 3)
    assert s[0] is None and s[1] is None
    assert abs(s[2] - 2.0) < 1e-9
    assert abs(s[4] - 4.0) < 1e-9


def test_ema_seeds_from_sma():
    v = [10.0] * 20
    e = ema(v, 5)
    assert e[4] == 10.0
    assert e[-1] == 10.0


def test_rsi_constant_is_neutral_or_none_early():
    closes = [1.0] * 30
    r = rsi_series(closes, 14)
    assert r[13] is None or r[13] == 50 or r[14] == 50


def test_rsi_uptrend_high():
    closes = [float(i) for i in range(1, 40)]
    r = rsi_series(closes, 14)
    assert r[-1] is not None and r[-1] > 70


def test_bollinger_symmetric_on_flat():
    closes = [5.0] * 30
    mid, up, lo = bollinger(closes, 20, 2)
    assert mid[-1] == 5.0
    assert abs((up[-1] or 0) - 5.0) < 1e-9
    assert abs((lo[-1] or 0) - 5.0) < 1e-9


def test_fractal_requires_wings():
    # constructed bullish fractal at index 4
    lows = [5, 4, 3, 4, 5, 6, 7, 8]
    highs = [x + 1 for x in lows]
    cs = []
    for i, (l, h) in enumerate(zip(lows, highs)):
        mid = (l + h) / 2
        cs.append(Candle("EUR/GBP", "5m", i * 1000, mid, h, l, mid, 1))
    pts = detect_fractals(cs, 2)
    bulls = [p for p in pts if p.kind == "BULLISH" and p.confirmed]
    assert any(p.index == 2 for p in bulls)


def test_zigzag_developing_not_confirmed_last():
    closes = [1, 1.01, 1.02, 0.99, 0.98, 0.97, 1.00, 1.03]
    pts = zigzag(_candles(closes), 1.5)
    assert pts
    assert pts[-1].confirmed is False
    assert all(p.confirmed for p in pts[:-1])
