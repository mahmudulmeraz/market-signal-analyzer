import pytest

from app.core.exceptions import DataValidationError
from app.core.models import Candle
from app.data.providers.simulated import generate_series
from app.data.validator import dedupe_sort, validate_candle


def test_validate_rejects_inverted_hl():
    c = Candle("EUR/GBP", "5m", 1, 1, 0.5, 2, 1)
    with pytest.raises(DataValidationError):
        validate_candle(c)


def test_dedupe():
    a = Candle("EUR/GBP", "5m", 100, 1, 1.1, 0.9, 1, 1)
    b = Candle("EUR/GBP", "5m", 100, 1, 1.1, 0.9, 1.01, 1)
    c = Candle("EUR/GBP", "5m", 200, 1, 1.1, 0.9, 1, 1)
    clean, dropped = dedupe_sort([c, a, b])
    assert len(clean) == 2
    assert dropped == 1
    assert clean[0].timestamp == 100


def test_simulated_pairs_deterministic():
    a = generate_series("EUR/GBP", "5m", 50, end_ms=1_700_000_000_000)
    b = generate_series("EUR/GBP", "5m", 50, end_ms=1_700_000_000_000)
    assert [x.close for x in a] == [x.close for x in b]
    assert a[0].symbol == "EUR/GBP"
