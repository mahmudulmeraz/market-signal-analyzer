from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QTextEdit, QVBoxLayout, QWidget

from app.core.enums import Direction
from app.core.models import Signal
from app.signals.explanation import explain
from app.ui.theme import ACCENT, DOWN, MUTED, SURFACE, UP
from app.utils.helpers import fmt_price


class SignalPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        cap = QLabel("CURRENT SIGNAL")
        cap.setStyleSheet(f"color:{MUTED}; font-size:11px; font-weight:600; letter-spacing:0.08em;")
        layout.addWidget(cap)
        self.dir_lbl = QLabel("WAIT")
        self.dir_lbl.setAlignment(Qt.AlignCenter)
        self.dir_lbl.setStyleSheet(f"font-size:28px; font-weight:700; color:{MUTED}; padding:8px;")
        layout.addWidget(self.dir_lbl)
        self.meta = QLabel("—")
        self.meta.setAlignment(Qt.AlignCenter)
        self.meta.setStyleSheet(f"color:{MUTED};")
        layout.addWidget(self.meta)
        self.grid = QLabel("")
        self.grid.setStyleSheet(f"color:#dce4ea; font-family: Consolas, monospace; font-size:12px;")
        layout.addWidget(self.grid)
        why = QLabel("WHY THIS SIGNAL?")
        why.setStyleSheet(f"color:{MUTED}; font-size:11px; font-weight:600; letter-spacing:0.08em; padding-top:8px;")
        layout.addWidget(why)
        self.why = QTextEdit()
        self.why.setReadOnly(True)
        self.why.setStyleSheet(f"background:{SURFACE}; border:1px solid #1c262f; font-family: Consolas, monospace; font-size:11px;")
        layout.addWidget(self.why)
        note = QLabel("PAPER / RESEARCH  ·  no real money  ·  not a live order")
        note.setStyleSheet(f"color:{MUTED}; font-size:11px;")
        note.setWordWrap(True)
        layout.addWidget(note)

    def show_signal(self, sig: Signal | None) -> None:
        if sig is None:
            self.dir_lbl.setText("WAIT")
            self.why.setPlainText("Waiting for closed candles.")
            return
        color = MUTED
        if sig.direction == Direction.BUY:
            color = UP
        elif sig.direction == Direction.SELL:
            color = DOWN
        self.dir_lbl.setText(sig.direction.value)
        self.dir_lbl.setStyleSheet(f"font-size:28px; font-weight:700; color:{color}; padding:8px;")
        self.meta.setText(
            f"{sig.symbol}  ·  {sig.timeframe}  ·  {sig.score:.0f}/100  ·  {sig.strength.value}"
        )
        s = sig.snapshot
        rsi = f"{s.rsi:.1f}" if s.rsi is not None else "—"
        self.grid.setText(
            f"RSI       {rsi}  {s.rsi_state}\n"
            f"MA        {s.trend.value}\n"
            f"BOLLINGER {s.bb_state}\n"
            f"FRACTAL   {s.fractal}  {'confirmed' if s.fractal_confirmed else 'n/a'}\n"
            f"ZIGZAG    {s.zigzag}  {'confirmed' if s.zigzag_confirmed else 'n/a'}\n"
            f"PRICE     {fmt_price(sig.price)}\n"
            f"STATE     {sig.state.value}"
        )
        self.why.setPlainText(explain(sig))
