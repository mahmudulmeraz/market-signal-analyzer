"""Live FX OHLC from Yahoo Finance public chart endpoint.

No login, no broker, no unofficial Quotex API. If a symbol or timeframe
is missing, the provider returns no candles and reports DATA UNAVAILABLE.
Never fabricates prices.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from typing import Callable, Dict, List, Optional, Set, Tuple

from app.config.instruments import PAIRS, TIMEFRAMES
from app.core.models import Candle
from app.data.providers.base import MarketDataProvider
from app.utils.logging import logger

YAHOO_SYMBOLS = {pair: pair.replace("/", "") + "=X" for pair in PAIRS}

YAHOO_INTERVAL = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "60m",
}

YAHOO_RANGE = {
    "1m": "5d",
    "5m": "1mo",
    "15m": "1mo",
    "30m": "1mo",
    "1h": "3mo",
}

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def _http_json(url: str, timeout: float = 12.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)


def parse_chart(payload: dict, pair: str, timeframe: str) -> List[Candle]:
    result = (payload.get("chart") or {}).get("result")
    if not result:
        return []
    block = result[0] or {}
    timestamps = block.get("timestamp") or []
    quote = ((block.get("indicators") or {}).get("quote") or [{}])[0]
    opens = quote.get("open") or []
    highs = quote.get("high") or []
    lows = quote.get("low") or []
    closes = quote.get("close") or []
    volumes = quote.get("volume") or []
    out: List[Candle] = []
    n = min(len(timestamps), len(opens), len(highs), len(lows), len(closes))
    for i in range(n):
        o, h, l, c = opens[i], highs[i], lows[i], closes[i]
        if o is None or h is None or l is None or c is None:
            continue
        if h < l or c <= 0 or o <= 0:
            continue
        vol = 0.0
        if i < len(volumes) and volumes[i] is not None:
            vol = float(volumes[i])
        out.append(
            Candle(
                symbol=pair,
                timeframe=timeframe,
                timestamp=int(timestamps[i]) * 1000,
                open=float(o),
                high=float(h),
                low=float(l),
                close=float(c),
                volume=vol,
                is_closed=True,
            )
        )
    return out


class YahooLiveProvider(MarketDataProvider):
    def __init__(self, poll_seconds: float = 15.0):
        self._poll = poll_seconds
        self._connected = False
        self._stale = True
        self._last_ok = 0.0
        self._error: Optional[str] = None
        self._prices: Dict[str, float] = {}
        self._unsupported: Set[str] = set()
        self._subs: Dict[Tuple[str, str], List[Callable[[Candle], None]]] = {}
        self._last_ts: Dict[Tuple[str, str], int] = {}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def name(self) -> str:
        return "yahoo"

    def is_simulated(self) -> bool:
        return False

    def connect(self) -> bool:
        if self._connected:
            return True
        try:
            self._fetch_pair("EUR/GBP", "5m", 20)
            self._connected = True
            self._stale = False
            self._error = None
        except Exception as exc:
            self._connected = False
            self._stale = True
            self._error = str(exc)
            logger.error("Live provider connect failed: %s", exc)
            return False
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="yahoo-live")
        self._thread.start()
        logger.info("Live provider connected (Yahoo Finance public chart)")
        return True

    def disconnect(self) -> None:
        self._stop.set()
        self._connected = False
        self._stale = True
        logger.info("Live provider disconnected")

    def supported_symbols(self) -> List[str]:
        return [p for p in PAIRS if p not in self._unsupported]

    def supported_timeframes(self) -> List[str]:
        return [tf for tf in TIMEFRAMES if tf in YAHOO_INTERVAL]

    def get_historical_candles(self, symbol: str, timeframe: str, limit: int = 400) -> List[Candle]:
        try:
            candles = self._fetch_pair(symbol, timeframe, limit)
            if not candles:
                self._unsupported.add(symbol)
                logger.warning("DATA UNAVAILABLE for %s %s", symbol, timeframe)
            else:
                self._unsupported.discard(symbol)
                self._prices[symbol] = candles[-1].close
                self._last_ok = time.time()
                self._stale = False
                self._error = None
            return candles[-limit:]
        except Exception as exc:
            self._error = str(exc)
            self._stale = True
            logger.error("Live fetch error %s %s: %s", symbol, timeframe, exc)
            return []

    def get_latest_price(self, symbol: str) -> Optional[float]:
        return self._prices.get(symbol)

    def subscribe(self, symbol: str, timeframe: str, callback: Callable[[Candle], None]) -> None:
        with self._lock:
            self._subs.setdefault((symbol, timeframe), []).append(callback)

    def unsubscribe(self, symbol: str, timeframe: str) -> None:
        with self._lock:
            self._subs.pop((symbol, timeframe), None)

    def status_message(self) -> str:
        if not self._connected:
            if self._error:
                return f"LIVE DATA DISCONNECTED — {self._error[:80]}"
            return "LIVE DATA DISCONNECTED"
        if self._stale:
            return "LIVE DATA STALE"
        return "LIVE DATA CONNECTED · Yahoo Finance (public)"

    def is_stale(self) -> bool:
        if not self._connected:
            return True
        return (time.time() - self._last_ok) > 45.0

    def unavailable_message(self, symbol: str) -> Optional[str]:
        if symbol in self._unsupported:
            return (
                "DATA UNAVAILABLE\n"
                "Provider does not currently support this symbol."
            )
        return None

    def _fetch_pair(self, pair: str, timeframe: str, limit: int) -> List[Candle]:
        ysym = YAHOO_SYMBOLS.get(pair)
        interval = YAHOO_INTERVAL.get(timeframe)
        span = YAHOO_RANGE.get(timeframe, "1mo")
        if not ysym or not interval:
            return []
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/{ysym}"
            f"?range={span}&interval={interval}&includePrePost=false"
        )
        payload = _http_json(url)
        err = (payload.get("chart") or {}).get("error")
        if err:
            logger.warning("Yahoo error for %s: %s", pair, err)
            return []
        candles = parse_chart(payload, pair, timeframe)
        meta = ((payload.get("chart") or {}).get("result") or [{}])[0].get("meta") or {}
        px = meta.get("regularMarketPrice")
        if px is not None:
            self._prices[pair] = float(px)
        return candles[-limit:] if limit else candles

    def _loop(self) -> None:
        rotate = list(PAIRS)
        rot_i = 0
        while not self._stop.is_set():
            with self._lock:
                keys = list(self._subs.keys())
            for key in keys:
                pair, tf = key
                try:
                    series = self._fetch_pair(pair, tf, 80)
                    self._last_ok = time.time()
                    self._stale = False
                    self._error = None
                    self._connected = True
                    last_seen = self._last_ts.get(key, 0)
                    new_bars = [c for c in series if c.timestamp > last_seen]
                    if new_bars:
                        self._last_ts[key] = new_bars[-1].timestamp
                        with self._lock:
                            cbs = list(self._subs.get(key, []))
                        for bar in new_bars:
                            for cb in cbs:
                                try:
                                    cb(bar)
                                except Exception as exc:
                                    logger.error("Live subscriber error: %s", exc)
                except urllib.error.URLError as exc:
                    self._stale = True
                    self._error = str(exc.reason if hasattr(exc, "reason") else exc)
                    logger.error("Live network error: %s", self._error)
                except Exception as exc:
                    self._stale = True
                    self._error = str(exc)
                    logger.error("Live loop error: %s", exc)
            # refresh one extra pair price for the watchlist
            try:
                extra = rotate[rot_i % len(rotate)]
                rot_i += 1
                if extra not in [k[0] for k in keys]:
                    self._fetch_pair(extra, "1h", 5)
            except Exception:
                pass
            self._stop.wait(self._poll)
