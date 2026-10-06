from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.config.indicator_config import AppConfig
from app.ui.theme import MUTED


class SettingsView(QWidget):
    provider_changed = Signal(str)

    def __init__(self, cfg: AppConfig, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        layout = QVBoxLayout(self)
        note = QLabel(
            "Live mode uses Yahoo Finance public FX charts (no login). "
            "If a pair cannot be fetched, the app shows DATA UNAVAILABLE — it will not invent prices. "
            "Simulated mode is research-only and is labeled SIMULATED DATA."
        )
        note.setStyleSheet(f"color:{MUTED};")
        note.setWordWrap(True)
        layout.addWidget(note)
        form = QFormLayout()
        self.provider = QComboBox()
        self.provider.addItem("Live — Yahoo Finance (public)", "LIVE")
        self.provider.addItem("Simulated (research only)", "SIMULATED")
        idx = 0 if cfg.data_mode == "LIVE" else 1
        self.provider.setCurrentIndex(idx)
        self.rsi_p = QSpinBox()
        self.rsi_p.setRange(2, 100)
        self.rsi_p.setValue(cfg.indicators.rsi_period)
        self.rsi_ob = QDoubleSpinBox()
        self.rsi_ob.setRange(50, 99)
        self.rsi_ob.setValue(cfg.indicators.rsi_overbought)
        self.rsi_os = QDoubleSpinBox()
        self.rsi_os.setRange(1, 50)
        self.rsi_os.setValue(cfg.indicators.rsi_oversold)
        self.bb_p = QSpinBox()
        self.bb_p.setRange(5, 100)
        self.bb_p.setValue(cfg.indicators.bb_period)
        self.bb_k = QDoubleSpinBox()
        self.bb_k.setRange(0.5, 5)
        self.bb_k.setSingleStep(0.1)
        self.bb_k.setValue(cfg.indicators.bb_std)
        self.ma_t = QComboBox()
        self.ma_t.addItems(["EMA", "SMA"])
        self.ma_t.setCurrentText(cfg.indicators.ma_type)
        self.ma_p = QSpinBox()
        self.ma_p.setRange(2, 200)
        self.ma_p.setValue(cfg.indicators.ma_period)
        self.zz = QDoubleSpinBox()
        self.zz.setRange(0.1, 5)
        self.zz.setSingleStep(0.1)
        self.zz.setValue(cfg.indicators.zigzag_deviation)
        self.buy_th = QDoubleSpinBox()
        self.buy_th.setRange(10, 100)
        self.buy_th.setValue(cfg.signal.buy_threshold)
        self.sell_th = QDoubleSpinBox()
        self.sell_th.setRange(-100, -10)
        self.sell_th.setValue(cfg.signal.sell_threshold)
        self.hold = QSpinBox()
        self.hold.setRange(1, 50)
        self.hold.setValue(cfg.paper.holding_bars)
        form.addRow("Data source", self.provider)
        form.addRow("RSI period", self.rsi_p)
        form.addRow("RSI overbought", self.rsi_ob)
        form.addRow("RSI oversold", self.rsi_os)
        form.addRow("Bollinger period", self.bb_p)
        form.addRow("Bollinger std", self.bb_k)
        form.addRow("MA type", self.ma_t)
        form.addRow("MA period", self.ma_p)
        form.addRow("ZigZag deviation %", self.zz)
        form.addRow("Buy threshold", self.buy_th)
        form.addRow("Sell threshold", self.sell_th)
        form.addRow("Paper holding bars", self.hold)
        layout.addLayout(form)
        layout.addStretch()
        for w in (
            self.rsi_p,
            self.rsi_ob,
            self.rsi_os,
            self.bb_p,
            self.bb_k,
            self.ma_t,
            self.ma_p,
            self.zz,
            self.buy_th,
            self.sell_th,
            self.hold,
        ):
            if hasattr(w, "valueChanged"):
                w.valueChanged.connect(self._apply)
            if hasattr(w, "currentTextChanged"):
                w.currentTextChanged.connect(self._apply)
        self.provider.currentIndexChanged.connect(self._on_provider)

    def _on_provider(self, *_args) -> None:
        mode = self.provider.currentData()
        self.cfg.data_mode = mode
        self.provider_changed.emit(mode)

    def _apply(self, *_args) -> None:
        self.cfg.indicators.rsi_period = self.rsi_p.value()
        self.cfg.indicators.rsi_overbought = self.rsi_ob.value()
        self.cfg.indicators.rsi_oversold = self.rsi_os.value()
        self.cfg.indicators.bb_period = self.bb_p.value()
        self.cfg.indicators.bb_std = self.bb_k.value()
        self.cfg.indicators.ma_type = self.ma_t.currentText()
        self.cfg.indicators.ma_period = self.ma_p.value()
        self.cfg.indicators.zigzag_deviation = self.zz.value()
        self.cfg.signal.buy_threshold = self.buy_th.value()
        self.cfg.signal.sell_threshold = self.sell_th.value()
        self.cfg.paper.holding_bars = self.hold.value()
