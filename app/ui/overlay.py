from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSlider, QVBoxLayout, QWidget

from app.core.enums import Direction
from app.core.models import Signal
from app.ui.theme import BG, BORDER, DOWN, MUTED, UP
from app.utils.helpers import fmt_price


class OverlayWindow(QWidget):
    """Always-on-top compact overlay. Same signal engine as the main window."""

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setWindowTitle("SIGNAL TERMINAL overlay")
        self.resize(240, 200)
        self.setStyleSheet(
            f"background:{BG}; color:#dce4ea; border:1px solid {BORDER}; font-family: Segoe UI;"
        )
        layout = QVBoxLayout(self)
        self.pair = QLabel("—")
        self.pair.setStyleSheet(f"color:{MUTED}; font-size:12px;")
        self.dir_lbl = QLabel("WAIT")
        self.dir_lbl.setAlignment(Qt.AlignCenter)
        self.dir_lbl.setStyleSheet("font-size:22px; font-weight:700;")
        self.meta = QLabel("PAPER MODE")
        self.meta.setAlignment(Qt.AlignCenter)
        self.meta.setStyleSheet(f"color:{MUTED}; font-size:11px;")
        layout.addWidget(self.pair)
        layout.addWidget(self.dir_lbl)
        layout.addWidget(self.meta)
        layout.addWidget(QLabel("Opacity"))
        sl = QSlider(Qt.Horizontal)
        sl.setRange(40, 100)
        sl.setValue(92)
        sl.valueChanged.connect(lambda v: self.setWindowOpacity(v / 100.0))
        layout.addWidget(sl)
        self._drag = None
        self.setWindowOpacity(0.92)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag is not None and e.buttons() & Qt.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        self._drag = None

    def update_signal(self, sig: Signal | None, pair: str, tf: str) -> None:
        self.pair.setText(f"{pair}  ·  {tf}")
        if not sig:
            self.dir_lbl.setText("WAIT")
            return
        c = UP if sig.direction == Direction.BUY else DOWN if sig.direction == Direction.SELL else MUTED
        self.dir_lbl.setText(sig.direction.value)
        self.dir_lbl.setStyleSheet(f"font-size:22px; font-weight:700; color:{c};")
        self.meta.setText(
            f"{sig.score:.0f}/100  ·  {fmt_price(sig.price)}\nPAPER MODE — NO REAL MONEY"
        )
