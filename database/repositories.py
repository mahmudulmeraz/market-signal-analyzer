from __future__ import annotations

import json
from typing import Iterable, List, Optional

from app.core.models import Candle, PaperTrade, Signal
from app.utils.time import utc_now_ms


class Repositories:
    def __init__(self, conn):
        self.conn = conn

    def save_candles(self, candles: Iterable[Candle]) -> None:
        rows = [
            (c.symbol, c.timeframe, c.timestamp, c.open, c.high, c.low, c.close, c.volume)
            for c in candles
        ]
        self.conn.executemany(
            "INSERT OR REPLACE INTO candles VALUES (?,?,?,?,?,?,?,?)",
            rows,
        )
        self.conn.commit()

    def save_signal(self, s: Signal) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                s.id,
                s.symbol,
                s.timeframe,
                s.timestamp,
                s.direction.value,
                s.strength.value,
                s.score,
                s.state.value,
                s.price,
                json.dumps(s.reasons),
                json.dumps(
                    {
                        "rsi": s.snapshot.rsi,
                        "rsi_state": s.snapshot.rsi_state,
                        "trend": s.snapshot.trend.value,
                        "bb_state": s.snapshot.bb_state,
                        "fractal": s.snapshot.fractal,
                        "zigzag": s.snapshot.zigzag,
                    }
                ),
                s.outcome,
            ),
        )
        self.conn.commit()

    def recent_signals(self, limit: int = 200) -> List[sqlite_row]:
        cur = self.conn.execute(
            "SELECT * FROM signals ORDER BY timestamp DESC LIMIT ?", (limit,)
        )
        return list(cur.fetchall())

    def save_trade(self, t: PaperTrade) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO paper_trades VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                t.id,
                t.signal_id,
                t.symbol,
                t.timeframe,
                t.direction,
                t.entry_time,
                t.entry_price,
                t.exit_time,
                t.exit_price,
                t.pnl,
                t.status,
            ),
        )
        self.conn.commit()

    def save_backtest(self, symbol: str, timeframe: str, split: str, metrics: dict) -> None:
        self.conn.execute(
            "INSERT INTO backtest_runs (created_at, symbol, timeframe, split, metrics_json) VALUES (?,?,?,?,?)",
            (utc_now_ms(), symbol, timeframe, split, json.dumps(metrics, default=str)),
        )
        self.conn.commit()

    def set_setting(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO settings_kv (key, value) VALUES (?,?)", (key, value)
        )
        self.conn.commit()

    def get_setting(self, key: str) -> Optional[str]:
        row = self.conn.execute("SELECT value FROM settings_kv WHERE key=?", (key,)).fetchone()
        return row[0] if row else None

    def log_event(self, level: str, message: str) -> None:
        self.conn.execute(
            "INSERT INTO events (ts, level, message) VALUES (?,?,?)",
            (utc_now_ms(), level, message),
        )
        self.conn.commit()


# type alias for readability
sqlite_row = object
