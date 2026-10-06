from __future__ import annotations

from typing import List

from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.backtesting.metrics import format_win_rate
from app.core.models import PaperTrade, Signal
from app.ui.theme import MUTED
from app.utils.helpers import fmt_price
from app.utils.time import format_dt


class HistoryTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            ["Time", "Pair", "TF", "Signal", "Score", "Strength", "Price", "State"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def set_signals(self, signals: List[Signal]) -> None:
        rows = list(reversed(signals[-200:]))
        self.table.setRowCount(len(rows))
        for i, s in enumerate(rows):
            vals = [
                format_dt(s.timestamp),
                s.symbol,
                s.timeframe,
                s.direction.value,
                f"{s.score:.1f}",
                s.strength.value,
                fmt_price(s.price),
                s.state.value,
            ]
            for j, v in enumerate(vals):
                self.table.setItem(i, j, QTableWidgetItem(v))


class BacktestView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        hint = QLabel(
            "Backtests process candles in time order. Fractals and ZigZag use only confirmed "
            "information available at each bar. Training, validation, and out-of-sample are separate."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color:{MUTED};")
        layout.addWidget(hint)
        row = QHBoxLayout()
        self.btn_run = QPushButton("Run backtest (current pair)")
        self.btn_oos = QPushButton("Train / Validate / OOS")
        self.btn_wf = QPushButton("Walk-forward")
        row.addWidget(self.btn_run)
        row.addWidget(self.btn_oos)
        row.addWidget(self.btn_wf)
        row.addStretch()
        layout.addLayout(row)
        self.out = QLabel("No run yet.")
        self.out.setStyleSheet("font-family: Consolas, monospace; font-size:12px;")
        self.out.setWordWrap(True)
        layout.addWidget(self.out)
        layout.addStretch()

    def show_result(self, title: str, metrics: dict) -> None:
        wr = format_win_rate(metrics)
        pf = metrics.get("profit_factor")
        pf_s = "—" if pf is None else ("∞" if pf == float("inf") else f"{pf:.2f}")
        wr_note = wr
        text = (
            f"{title}\n"
            f"Trades        {metrics.get('total_trades')}\n"
            f"Wins/Losses   {metrics.get('wins')} / {metrics.get('losses')}\n"
            f"Win rate      {wr_note}\n"
            f"Net P/L       {metrics.get('net_pnl'):.2f}  (paper units)\n"
            f"Profit factor {pf_s}\n"
            f"Max drawdown  {metrics.get('max_drawdown', 0)*100:.2f}%\n"
            f"Avg trade     {metrics.get('average_trade'):.2f}\n"
            f"BUY / SELL    {metrics.get('buy_signals')} / {metrics.get('sell_signals')}\n"
            f"WAIT bars     {metrics.get('wait_bars')}\n"
            "\nThese are measured results on simulated research data.\n"
            "They are not a promise of future performance and not 97% accuracy."
        )
        self.out.setText(text)


class PaperView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        banner = QLabel("PAPER TRADING — NO REAL MONEY")
        banner.setStyleSheet("color:#d4a017; font-weight:700; letter-spacing:0.06em;")
        layout.addWidget(banner)
        self.stats = QLabel("")
        self.stats.setStyleSheet("font-family: Consolas, monospace;")
        layout.addWidget(self.stats)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["Pair", "Dir", "Entry", "Exit", "P/L", "Status", "Bars"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def render(self, stats: dict, trades: List[PaperTrade]) -> None:
        wr = "INSUFFICIENT SAMPLE SIZE" if stats.get("insufficient") or stats.get("win_rate") is None else f"{stats['win_rate']*100:.1f}%"
        self.stats.setText(
            f"Balance  {stats['balance']:.2f}   P/L {stats['pnl']:.2f}   "
            f"Open {stats['open']}  Closed {stats['closed']}  Win rate {wr}  "
            f"Drawdown {stats['drawdown']*100:.2f}%"
        )
        rows = list(reversed(trades[-100:]))
        self.table.setRowCount(len(rows))
        for i, t in enumerate(rows):
            vals = [
                t.symbol,
                t.direction,
                fmt_price(t.entry_price),
                fmt_price(t.exit_price) if t.exit_price else "—",
                f"{t.pnl:.2f}",
                t.status,
                str(t.bars_held),
            ]
            for j, v in enumerate(vals):
                self.table.setItem(i, j, QTableWidgetItem(v))


class StatsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.lbl = QLabel("No statistics yet.")
        self.lbl.setStyleSheet("font-family: Consolas, monospace;")
        layout.addWidget(self.lbl)
        layout.addStretch()

    def render(self, summary: dict) -> None:
        wr = (
            "INSUFFICIENT SAMPLE SIZE"
            if summary.get("insufficient") or summary.get("win_rate") is None
            else f"{summary['win_rate']*100:.1f}%"
        )
        self.lbl.setText(
            f"Total signals   {summary.get('total_signals')}\n"
            f"BUY / SELL / WAIT  {summary.get('buy')} / {summary.get('sell')} / {summary.get('wait')}\n"
            f"Average score   {summary.get('avg_score'):.1f}\n"
            f"Paper P/L       {summary.get('paper_pnl'):.2f}\n"
            f"Closed trades   {summary.get('closed_trades')}\n"
            f"Win rate        {wr}\n"
            "\nPaper, backtest, out-of-sample, and live sample are never mixed."
        )


class LogsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        from PySide6.QtWidgets import QPlainTextEdit

        layout = QVBoxLayout(self)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

    def append(self, line: str) -> None:
        self.text.appendPlainText(line)
