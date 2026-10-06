# SIGNAL TERMINAL

Native Windows desktop application for **market research**, **transparent technical signals**, **backtesting**, and **paper trading**.

This is not a broker. It does not place real orders. It does not guarantee profits or a fixed accuracy percentage. Historical results do not imply future results.

## Install (Windows)

Unzip, then **open the folder that contains `requirements.txt`** (same folder as `run.py`).

**Option A — double-click**

1. `install.bat`
2. `run.bat`

**Option B — Command Prompt** (must already be inside this folder)

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

If pip says `No such file or directory: requirements.txt`, you are in the wrong folder. Go one level in until you see `requirements.txt`.

## What it does

- Simulated (and later, legitimate live) market data for ten FX pairs
- Real-time candlestick chart (pyqtgraph)
- RSI, Bollinger Bands, SMA/EMA, confirmed Williams fractals, confirmed ZigZag
- Deterministic multi-factor BUY / SELL / WAIT with written reasons
- SQLite persistence of candles, signals, paper trades, backtests
- In-sample / validation / out-of-sample and walk-forward backtests
- Paper trading account clearly labeled **NO REAL MONEY**
- Always-on-top overlay
- Isolated `BrokerAdapter` for a future **official** API only

## Pairs

USD/BRL, USD/ARS, USD/BDT, USD/PKR, USD/DZD, USD/INR, EUR/GBP, CAD/CHF, AUD/NZD, AUD/CHF

## Requirements

- Windows 10/11 (also runs on macOS/Linux with a display)
- Python 3.10+ (3.11+ recommended), added to PATH
- Dependencies in `requirements.txt`

## Data mode

Default provider: **SIMULATED DATA** (deterministic synthetic OHLC). The UI never labels this as live.

Live feed: `app/data/providers/live_provider.py` reports **LIVE DATA: NOT CONFIGURED** until you plug in a legitimate source behind `MarketDataProvider`.

## Signal methodology

Each family contributes a signed score (default 20 points each, configurable):

1. RSI (Wilder) — recovery from oversold/overbought, never a standalone guarantee
2. Bollinger — rejection / breakout / position; contraction is a conflict, not a trade
3. Moving average — trend context (SMA or EMA)
4. Fractal — **confirmed only** after both right-hand wings have closed
5. ZigZag — **confirmed only** after a reversal of `deviation` percent

Score ≥ buy threshold → BUY; ≤ sell threshold → SELL; otherwise **WAIT**.

WAIT is a first-class output. The engine will not force a low-quality call.

## Backtesting and look-ahead

At bar `i` the engine sees `candles[0:i+1]` only.

- Fractals whose right wing has not closed are ignored
- ZigZag developing extremes are not treated as history
- Signals fire on the **close** of bar `i`
- Fills occur at the **next bar open**, plus configurable spread

Training, validation, out-of-sample, walk-forward, paper, and live samples are stored and displayed separately.

If a sample is too small, the UI shows **INSUFFICIENT SAMPLE SIZE** instead of a fake win rate.

## Paper trading

Virtual balance, position size, holding bars, spread. Same signal engine. Banner: **PAPER TRADING — NO REAL MONEY**.

## Tests

```text
pytest
```

## Packaging (Windows exe)

```text
pip install pyinstaller
pyinstaller signal_terminal.spec
```

Output: `dist/SIGNAL_TERMINAL.exe`

## Security

No passwords, cookies, session tokens, or CAPTCHA bypass. No unofficial Quotex (or similar) automation. A future official adapter can live under `app/broker/adapters/` without changing the rest of the app.

## Limitations

- No licensed live FX feed is bundled. Simulation is for research and UI testing.
- Strategy weights are **not** optimized. They are transparent defaults.
- Measured win rates on simulated paths are not trading advice.


## Build a Windows installer

For a user-friendly Windows installer, see `WINDOWS_BUILD_GUIDE.txt`. On Windows, run `build_windows.bat`, then compile `installer.iss` with Inno Setup 6. The final installer is `Output\SIGNAL_TERMINAL_Setup.exe`. Build on Windows; this ZIP does not contain a prebuilt EXE.
