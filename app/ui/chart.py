from __future__ import annotations

from typing import List, Optional

import pyqtgraph as pg
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.core.models import Candle
from app.ui.theme import MUTED, SURFACE


class CandlestickItem(pg.GraphicsObject):
    def __init__(self, candles: List[Candle]):
        super().__init__()
        self.candles = candles
        self.picture = None
        self._regen()

    def _regen(self) -> None:
        self.picture = pg.QtGui.QPicture()
        p = pg.QtGui.QPainter(self.picture)
        w = 0.62
        for i, c in enumerate(self.candles):
            up = c.close >= c.open
            color = "#3dcc8a" if up else "#e85d5d"
            p.setPen(pg.mkPen(color))
            p.setBrush(pg.mkBrush(color))
            p.drawLine(pg.QtCore.QPointF(i, c.low), pg.QtCore.QPointF(i, c.high))
            body = c.close - c.open
            if abs(body) < 1e-12:
                body = (c.high - c.low) * 0.02 or 1e-8
            p.drawRect(pg.QtCore.QRectF(i - w / 2, c.open, w, body))
        p.end()

    def paint(self, painter, *args):
        if self.picture:
            painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        if not self.candles:
            return pg.QtCore.QRectF()
        lows = [c.low for c in self.candles]
        highs = [c.high for c in self.candles]
        return pg.QtCore.QRectF(-1, min(lows), len(self.candles) + 1, max(highs) - min(lows))


class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self.title = QLabel("CHART")
        self.title.setStyleSheet(f"color:{MUTED}; font-size:11px; font-weight:600; letter-spacing:0.08em;")
        layout.addWidget(self.title)
        pg.setConfigOptions(antialias=True, background=SURFACE, foreground="#dce4ea")
        self.plot = pg.PlotWidget()
        self.plot.showGrid(x=True, y=True, alpha=0.12)
        self.plot.setLabel("left", "Price")
        self.plot.setLabel("bottom", "Bar")
        self.plot.addLegend(offset=(8, 8))
        layout.addWidget(self.plot)
        self._item: Optional[CandlestickItem] = None
        self._ma = None
        self._bb_u = None
        self._bb_l = None
        self._zz = None

    def set_title(self, text: str) -> None:
        self.title.setText(text)

    def render(
        self,
        candles: List[Candle],
        ma: Optional[List] = None,
        bb_u: Optional[List] = None,
        bb_l: Optional[List] = None,
        zz_points=None,
        pair: str = "",
        tf: str = "",
    ) -> None:
        self.plot.clear()
        if not candles:
            self.title.setText("CHART  —  no data")
            return
        self._item = CandlestickItem(candles)
        self.plot.addItem(self._item)
        xs = list(range(len(candles)))
        if ma:
            ym = [v for v in ma]
            self.plot.plot(xs, [v if v is not None else float("nan") for v in ym], pen=pg.mkPen("#3d9cf0", width=1.4), name="MA")
        if bb_u:
            self.plot.plot(xs, [v if v is not None else float("nan") for v in bb_u], pen=pg.mkPen("#7a8894", width=1), name="BB U")
        if bb_l:
            self.plot.plot(xs, [v if v is not None else float("nan") for v in bb_l], pen=pg.mkPen("#7a8894", width=1), name="BB L")
        if zz_points:
            confirmed = [p for p in zz_points if p.confirmed]
            if len(confirmed) >= 2:
                self.plot.plot(
                    [p.index for p in confirmed],
                    [p.price for p in confirmed],
                    pen=pg.mkPen("#d4a017", width=1.2),
                    name="ZigZag",
                )
        n = len(candles)
        self.plot.setXRange(max(0, n - 90), n + 2, padding=0)
        self.title.setText(f"CHART  —  {pair}  ·  {tf}  ·  {n} bars")
