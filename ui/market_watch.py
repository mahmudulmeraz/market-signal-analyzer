from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from app.config.instruments import PAIRS
from app.ui.theme import MUTED
from app.utils.helpers import fmt_price


class MarketWatch(QWidget):
    pair_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        h = QLabel("MARKET WATCH")
        h.setStyleSheet(f"color:{MUTED}; font-size:11px; font-weight:600; letter-spacing:0.08em; padding:10px 8px 4px;")
        layout.addWidget(h)
        self.list = QListWidget()
        self.list.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.list)
        self._prices: Dict[str, float] = {}
        self._signals: Dict[str, str] = {}
        for p in PAIRS:
            item = QListWidgetItem(self._row(p, None, "—"))
            item.setData(Qt.UserRole, p)
            self.list.addItem(item)
        self.list.currentItemChanged.connect(self._sel)
        if self.list.count():
            self.list.setCurrentRow(0)

    def _row(self, pair: str, price: Optional[float], sig: str) -> str:
        return f"{pair:<10}  {fmt_price(price):>12}   {sig}"

    def update_row(self, pair: str, price: Optional[float], sig: str = "—") -> None:
        if price is not None:
            self._prices[pair] = price
        self._signals[pair] = sig
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it.data(Qt.UserRole) == pair:
                it.setText(self._row(pair, self._prices.get(pair), self._signals.get(pair, "—")))
                break

    def _sel(self, cur, _prev) -> None:
        if cur:
            self.pair_selected.emit(cur.data(Qt.UserRole))
