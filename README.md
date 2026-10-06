# SIGNAL TERMINAL

> **Market Analysis • Technical Indicators • Signal Research**

SIGNAL TERMINAL is a desktop-oriented market analysis application built to explore real-time market data, technical indicators, chart analysis, and rule-based trading signals through a simple visual interface.

The project focuses on combining **market-data processing, technical analysis, visualization, and desktop application development** into a single workflow.

---

## Overview

SIGNAL TERMINAL is designed as a research and analysis tool rather than a conventional trading bot.

The application processes market data, calculates technical indicators, evaluates a signal model, and presents the resulting analysis through a desktop interface.

```text
Market Data
     ↓
Data Processing
     ↓
Candle Construction
     ↓
Technical Indicators
     ↓
Signal Model
     ↓
Visual Analysis
     ↓
User Decision
```

The goal is to make technical market information easier to inspect without requiring the user to work directly with raw data or command-line tools.

---

## Features

### Market Analysis

* Candlestick-based market visualization
* Multiple currency pairs
* Configurable timeframes
* Market-data processing
* Technical indicator calculations
* Signal generation
* Visual market analysis

### Technical Indicators

The current project explores indicators and market-structure concepts including:

* RSI
* Bollinger Bands
* Moving Average
* Fractals
* ZigZag

These indicators are combined within the application's analysis workflow to generate rule-based signal outputs.

---

## Application Workflow

```text
Data Provider
     │
     ▼
Market Data
     │
     ▼
Candle Processing
     │
     ▼
Indicator Engine
     │
     ├── RSI
     ├── Bollinger Bands
     ├── Moving Average
     ├── Fractal
     └── ZigZag
     │
     ▼
Signal Analysis
     │
     ▼
Desktop Interface
```

---

## Supported Market Pairs

The project has been developed with currency-market analysis in mind, including pairs such as:

```text
USD/BRL
USD/ARS
USD/BDT
USD/PKR
USD/DZD
USD/INR
EUR/GBP
CAD/CHF
AUD/NZD
AUD/CHF
```

Availability and data quality depend on the selected market-data provider.

---

## Technology Stack

### Programming

* Python
* HTML/CSS/JavaScript where applicable to the interface
* Batch scripting for Windows automation

### Data & Analysis

* Market-data APIs
* Technical indicator calculations
* Time-series processing
* Signal evaluation

### Application Packaging

* PyInstaller
* Inno Setup
* Windows batch scripts

### Development

* Python virtual environment
* Requirements-based dependency management
* Automated Windows build workflow

---

## Project Structure

```text
SIGNAL_TERMINAL/
│
├── app/
│   └── Application source code
│
├── data/
│   └── Project data
│
├── tests/
│   └── Test files
│
├── docs/
│   └── Additional documentation
│
├── README.md
├── INSTALL.md
├── WINDOWS_BUILD.md
│
├── requirements.txt
├── run.py
├── run.bat
├── install.bat
├── build_windows.bat
├── installer.iss
├── signalterminal.spec
│
└── .gitignore
```

Generated build directories and local environments such as `.venv`, `build`, `dist`, `output`, and runtime logs are intentionally excluded from the source repository.

---

## Installation

### Windows — Source Installation

Clone or download the repository and open the project directory containing:

```text
requirements.txt
run.py
app/
```

The easiest method on Windows is:

```text
1. Double-click install.bat
2. Wait for the installation to complete
3. Double-click run.bat
```

### Manual Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python run.py
```

For detailed instructions, see:

**[INSTALL.md](INSTALL.md)**

---

## Building the Windows Application

The repository contains the scripts and configuration required to build a standalone Windows application.

### Requirements

* Windows
* Python 3.11 x64
* Inno Setup 6 — required for the installer

### Build

Run:

```text
build_windows.bat
```

Then open:

```text
installer.iss
```

with Inno Setup Compiler and compile the installer.

The resulting installer is generated as:

```text
Output\SIGNAL_TERMINAL_Setup.exe
```

For the complete build procedure, see:

**[WINDOWS_BUILD.md](WINDOWS_BUILD.md)**

---

## Data Provider

The current live-data provider uses **Yahoo Finance public FX chart endpoints**.

This is important when interpreting the application's market data.

The provider:

* Is not a licensed broker feed.
* Does not provide Quotex OTC prices.
* May not support every requested symbol.
* May have differences in candle construction or timing.
* May not update every timeframe consistently.

Therefore, the application's market data should **not** be assumed to be identical to another broker or trading platform's chart.

---

## Signal Model

SIGNAL TERMINAL uses technical indicators and market-structure information as inputs to its signal-analysis workflow.

The generated output represents the result of the application's current rules and calculations.

It should be treated as:

```text
Analysis
   ≠
Guaranteed Prediction
```

The project is intended to explore how technical indicators and market data can be combined into a transparent signal-analysis system.

---

## Current Status

**Development / Research**

The application is an ongoing project.

Current development areas include:

* Data-provider reliability
* Candle synchronization
* Indicator calculations
* Signal-model refinement
* Desktop UI improvements
* Windows packaging
* Testing and validation

The system should not be considered a production-grade trading platform.

---

## Limitations

The current implementation has several important limitations.

### Market Data

Different providers can produce different:

* Prices
* Candles
* Timestamps
* Timeframes
* Market sessions

Therefore, signals based on one provider may not match another platform.

### OTC Markets

The current provider does **not** represent Quotex OTC pricing.

The application should therefore not be used to claim that its signals accurately predict Quotex OTC candles.

### Signal Accuracy

No signal model can guarantee future market movements.

The application does not provide guaranteed trading outcomes.

---

## Research & Paper Trading

SIGNAL TERMINAL is intended for:

* Research
* Technical analysis
* Software experimentation
* Market-data analysis
* Paper trading
* Backtesting and model experimentation

The application **does not place real-money trades or execute real orders**.

---

## Security

Do not commit sensitive information to this repository.

Avoid uploading:

```text
.env
API keys
Access tokens
Passwords
Private credentials
Private configuration
```

Local environments and generated files should remain excluded through `.gitignore`.

---

## Development Philosophy

The project follows a simple principle:

> **Make the analysis visible, understandable, and testable.**

Rather than hiding signal generation behind an unexplained "prediction" system, the project is designed around identifiable data-processing and technical-analysis steps.

```text
Data
 ↓
Processing
 ↓
Indicators
 ↓
Rules
 ↓
Signal
 ↓
Visualization
```

This makes the application easier to inspect, improve, and experiment with.

---

## Roadmap

Potential future development includes:

* [ ] Improved real-time data synchronization
* [ ] Additional market-data providers
* [ ] More technical indicators
* [ ] Configurable signal rules
* [ ] Backtesting interface
* [ ] Paper-trading simulation
* [ ] Signal history
* [ ] Performance analytics
* [ ] Improved Windows installer
* [ ] Expanded automated testing
* [ ] Better error handling and logging
* [ ] Improved desktop UI/UX

---

## Disclaimer

SIGNAL TERMINAL is a **research and software-development project**.

It is not financial advice, a broker, or a guaranteed prediction system.

Market data may be delayed, incomplete, inaccurate, or different from other trading platforms.

The application does not guarantee profitable trades or future market movements.

**Do not use generated signals as the sole basis for financial decisions.**

---

## Author

**Mahmudul Meraz**

Frontend Developer • Builder • Student • Technology Explorer

This project is part of my ongoing exploration of software development, data-driven applications, technical analysis, and desktop application engineering.

---

## License

This project is provided for educational, research, and development purposes.

See the repository license for applicable terms.

---

> **BUILD • LEARN • EXPERIMENT**
>
> SIGNAL TERMINAL
