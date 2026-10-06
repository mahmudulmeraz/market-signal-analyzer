"""Required instruments. Do not silently substitute other pairs."""

PAIRS = [
    "USD/BRL",
    "USD/ARS",
    "USD/BDT",
    "USD/PKR",
    "USD/DZD",
    "USD/INR",
    "EUR/GBP",
    "CAD/CHF",
    "AUD/NZD",
    "AUD/CHF",
]

BASE_PRICES = {
    "USD/BRL": 5.15,
    "USD/ARS": 950.0,
    "USD/BDT": 110.0,
    "USD/PKR": 278.0,
    "USD/DZD": 134.0,
    "USD/INR": 83.5,
    "EUR/GBP": 0.845,
    "CAD/CHF": 0.635,
    "AUD/NZD": 1.085,
    "AUD/CHF": 0.575,
}

PAIR_SEEDS = {
    "USD/BRL": 1101,
    "USD/ARS": 2202,
    "USD/BDT": 3303,
    "USD/PKR": 4404,
    "USD/DZD": 5505,
    "USD/INR": 6606,
    "EUR/GBP": 7707,
    "CAD/CHF": 8808,
    "AUD/NZD": 9909,
    "AUD/CHF": 1010,
}

TIMEFRAMES = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
}
