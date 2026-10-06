from app.data.providers.live_provider import YAHOO_SYMBOLS, parse_chart
from app.config.instruments import PAIRS


def test_yahoo_symbol_map_covers_required_pairs():
    for p in PAIRS:
        assert p in YAHOO_SYMBOLS
        assert YAHOO_SYMBOLS[p].endswith("=X")


def test_parse_chart_skips_null_bars():
    payload = {
        "chart": {
            "result": [
                {
                    "timestamp": [1, 2, 3],
                    "indicators": {
                        "quote": [
                            {
                                "open": [1.0, None, 1.2],
                                "high": [1.1, 1.1, 1.3],
                                "low": [0.9, 0.9, 1.1],
                                "close": [1.05, 1.0, 1.25],
                                "volume": [1, 1, 1],
                            }
                        ]
                    },
                }
            ]
        }
    }
    candles = parse_chart(payload, "EUR/GBP", "5m")
    assert len(candles) == 2
    assert candles[0].close == 1.05
    assert candles[1].close == 1.25
    assert candles[0].timestamp == 1000
