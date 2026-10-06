from __future__ import annotations

import queue
from typing import List, Optional

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.config.indicator_config import AppConfig
from app.config.instruments import PAIRS, TIMEFRAMES
from app.config.settings import APP_NAME, APP_VERSION
from app.core.models import Candle
from app.database.connection import connect
from app.database.repositories import Repositories
from app.database.schema import init_schema
from app.indicators.bollinger import bollinger
from app.indicators.moving_average import ma_series
from app.paper_trading.engine import PaperTrader
from app.services.market_service import MarketService
from app.services.signal_service import SignalService
from app.services.statistics_service import summarize
from app.ui.chart import ChartWidget
from app.ui.dashboard import BacktestView, HistoryTable, LogsView, PaperView, StatsView
from app.ui.market_watch import MarketWatch
from app.ui.overlay import OverlayWindow
from app.ui.settings_view import SettingsView
from app.ui.signal_panel import SignalPanel
from app.ui.theme import ACCENT, MUTED, WARN
from app.ui.workers import start_backtest
from app.utils.logging import logger
from app.utils.time import format_clock


class MainWindow(QMainWindow):
    """All widget updates run on the Qt GUI thread. Market ticks are queued."""

    backtest_finished = Signal(str, object)
    backtest_failed = Signal(str)

    def __init__(self, cfg: AppConfig):
        super().__init__()
        self.cfg = cfg
        self.setWindowTitle(f"{APP_NAME}  {APP_VERSION}")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 700)

        self.market = MarketService(mode=cfg.data_mode)
        self.signals = SignalService(cfg)
        self.paper = PaperTrader(cfg.paper)
        conn = connect()
        init_schema(conn)
        self.repo = Repositories(conn)

        self.pair = cfg.default_pair
        self.tf = cfg.default_timeframe
        self.candles: List[Candle] = []
        self._bt_thread = None
        self._candle_q: queue.Queue = queue.Queue()
        self._alive = True

        self._build()
        self.overlay = OverlayWindow()

        self.backtest_finished.connect(self._on_backtest_finished, Qt.QueuedConnection)
        self.backtest_failed.connect(self._on_backtest_failed, Qt.QueuedConnection)

        self.market.start()
        self._reload_series()
        self.market.subscribe(self.pair, self.tf, self._enqueue_candle)

        self.clock = QTimer(self)
        self.clock.timeout.connect(self._tick_clock)
        self.clock.start(1000)
        self._tick_clock()

        self._pump = QTimer(self)
        self._pump.timeout.connect(self._drain_candles)
        self._pump.start(50)

        self._log(f"Application started. Trading mode: PAPER / RESEARCH. Data mode: {self.cfg.data_mode}.")

    def _enqueue_candle(self, candle: Candle) -> None:
        if self._alive:
            self._candle_q.put(candle)

    def _drain_candles(self) -> None:
        latest: Optional[Candle] = None
        try:
            while True:
                latest = self._candle_q.get_nowait()
        except queue.Empty:
            pass
        if latest is not None:
            self._on_live_candle(latest)

    def _build(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(8)
        v.addLayout(self._topbar())

        split = QSplitter(Qt.Horizontal)
        self.watch = MarketWatch()
        self.watch.pair_selected.connect(self._on_pair)
        self.chart = ChartWidget()
        self.panel = SignalPanel()
        self.watch.setMinimumWidth(220)
        self.panel.setMinimumWidth(280)
        split.addWidget(self.watch)
        split.addWidget(self.chart)
        split.addWidget(self.panel)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        split.setStretchFactor(2, 0)
        v.addWidget(split, 1)

        self.tabs = QTabWidget()
        self.history = HistoryTable()
        self.bt_view = BacktestView()
        self.paper_view = PaperView()
        self.stats_view = StatsView()
        self.logs_view = LogsView()
        self.settings_view = SettingsView(self.cfg)
        self.settings_view.provider_changed.connect(self._switch_provider)
        self.tabs.addTab(self.history, "Signals")
        self.tabs.addTab(self.bt_view, "Backtest")
        self.tabs.addTab(self.paper_view, "Paper trading")
        self.tabs.addTab(self.stats_view, "Statistics")
        self.tabs.addTab(self.logs_view, "Logs")
        self.tabs.addTab(self.settings_view, "Settings")
        v.addWidget(self.tabs, 0)
        self.tabs.setMinimumHeight(220)

        self.bt_view.btn_run.clicked.connect(lambda: self._run_bt("full"))
        self.bt_view.btn_oos.clicked.connect(lambda: self._run_bt("oos"))
        self.bt_view.btn_wf.clicked.connect(lambda: self._run_bt("wf"))

        sb = QStatusBar()
        self.setStatusBar(sb)
        sb.showMessage("Research + paper trading  ·  no unofficial broker automation")

    def _topbar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        title = QLabel(APP_NAME)
        title.setStyleSheet(f"font-size:16px; font-weight:700; letter-spacing:0.12em; color:{ACCENT};")
        self.status_lbl = QLabel("SIMULATED DATA")
        self.status_lbl.setStyleSheet(f"color:{WARN}; font-weight:600;")
        self.mode_lbl = QLabel("PAPER TRADING — NO REAL MONEY")
        self.mode_lbl.setStyleSheet(f"color:{WARN};")
        self.time_lbl = QLabel("")
        self.time_lbl.setStyleSheet(f"color:{MUTED}; font-family: Consolas, monospace;")
        self.pair_box = QComboBox()
        self.pair_box.addItems(PAIRS)
        self.pair_box.setCurrentText(self.pair)
        self.pair_box.currentTextChanged.connect(self._on_pair)
        self.tf_box = QComboBox()
        self.tf_box.addItems(list(TIMEFRAMES.keys()))
        self.tf_box.setCurrentText(self.tf)
        self.tf_box.currentTextChanged.connect(self._on_tf)
        overlay_btn = QPushButton("Overlay")
        overlay_btn.clicked.connect(self._toggle_overlay)
        bar.addWidget(title)
        bar.addSpacing(16)
        bar.addWidget(self.status_lbl)
        bar.addWidget(self.mode_lbl)
        bar.addStretch()
        bar.addWidget(QLabel("Pair"))
        bar.addWidget(self.pair_box)
        bar.addWidget(QLabel("Timeframe"))
        bar.addWidget(self.tf_box)
        bar.addWidget(self.time_lbl)
        bar.addWidget(overlay_btn)
        return bar

    def _reload_series(self) -> None:
        self.candles = self.market.load(self.pair, self.tf, 400)
        if not self.candles:
            self.chart.render([], pair=self.pair, tf=self.tf)
            self.chart.set_title(
                f"DATA UNAVAILABLE — {self.pair} {self.tf}  |  Provider does not currently support this symbol."
            )
            self.panel.show_signal(None)
        else:
            self._recompute()
        for p in PAIRS:
            px = self.market.provider.get_latest_price(p)
            self.watch.update_row(p, px, "—")
        self._refresh_status()

    def _on_pair(self, pair: str) -> None:
        if pair == self.pair:
            return
        self.market.provider.unsubscribe(self.pair, self.tf)
        self.pair = pair
        self.pair_box.blockSignals(True)
        self.pair_box.setCurrentText(pair)
        self.pair_box.blockSignals(False)
        self._reload_series()
        self.market.subscribe(self.pair, self.tf, self._enqueue_candle)
        self._log(f"Switched pair to {pair}")

    def _on_tf(self, tf: str) -> None:
        if tf == self.tf:
            return
        self.market.provider.unsubscribe(self.pair, self.tf)
        self.tf = tf
        self._reload_series()
        self.market.subscribe(self.pair, self.tf, self._enqueue_candle)
        self._log(f"Switched timeframe to {tf}")

    def _on_live_candle(self, candle: Candle) -> None:
        if candle.symbol != self.pair or candle.timeframe != self.tf:
            return
        self.candles.append(candle)
        if len(self.candles) > 800:
            self.candles = self.candles[-600:]
        try:
            self.repo.save_candles([candle])
        except Exception as exc:
            logger.error("db candle: %s", exc)
        closed = self.paper.on_candle(candle)
        if closed:
            self.repo.save_trade(closed)
        self._recompute()

    def _recompute(self) -> None:
        if not self.candles:
            return
        sig = self.signals.on_candles(self.candles)
        self.panel.show_signal(sig)
        self.history.set_signals(self.signals.history)
        self.overlay.update_signal(sig, self.pair, self.tf)
        if sig.direction.value != "WAIT":
            opened = self.paper.on_signal(sig, self.candles[-1])
            if opened:
                self.repo.save_trade(opened)
            try:
                self.repo.save_signal(sig)
            except Exception as exc:
                logger.error("db signal: %s", exc)
        closes = [c.close for c in self.candles]
        ma = ma_series(closes, self.cfg.indicators.ma_period, self.cfg.indicators.ma_type)
        _m, up, lo = bollinger(closes, self.cfg.indicators.bb_period, self.cfg.indicators.bb_std)
        zz = self.signals.engine.indicators.zigzags(self.candles)
        self.chart.render(self.candles, ma, up, lo, zz, self.pair, self.tf)
        px = self.candles[-1].close
        self.watch.update_row(self.pair, px, sig.direction.value)
        self.paper_view.render(self.paper.stats(), self.paper.portfolio.closed + self.paper.portfolio.open)
        self.stats_view.render(
            summarize(self.signals.history, self.paper.portfolio.closed, self.cfg.min_sample)
        )
        self._refresh_status()

    def _run_bt(self, mode: str) -> None:
        if len(self.candles) < 80:
            QMessageBox.information(self, APP_NAME, "Not enough candles to backtest.")
            return
        self._log(f"Backtest started ({mode}) on {self.pair} {self.tf}")
        self.bt_view.out.setText("CALCULATING… UI remains responsive.")
        self._bt_thread = start_backtest(
            self.cfg,
            list(self.candles),
            mode,
            lambda title, metrics: self.backtest_finished.emit(title, metrics),
            lambda msg: self.backtest_failed.emit(msg),
        )

    def _on_backtest_finished(self, title: str, metrics: object) -> None:
        if isinstance(metrics, dict) and "train" in metrics:
            from app.backtesting.metrics import format_win_rate

            t, v, o = metrics["train"], metrics["validation"], metrics["out_of_sample"]
            self.bt_view.out.setText(
                f"{title}\n"
                f"IN-SAMPLE     {format_win_rate(t)}   trades={t['total_trades']}  pnl={t['net_pnl']:.2f}\n"
                f"VALIDATION    {format_win_rate(v)}   trades={v['total_trades']}  pnl={v['net_pnl']:.2f}\n"
                f"OUT-OF-SAMPLE {format_win_rate(o)}   trades={o['total_trades']}  pnl={o['net_pnl']:.2f}\n"
                "\nThese windows are disjoint. Out-of-sample is not used for threshold fitting."
            )
        elif isinstance(metrics, dict):
            self.bt_view.show_result(title, metrics)
            try:
                self.repo.save_backtest(self.pair, self.tf, title, metrics)
            except Exception:
                pass
        self._log(f"Backtest finished: {title}")

    def _on_backtest_failed(self, msg: str) -> None:
        self.bt_view.out.setText(f"Backtest error: {msg}")
        self._log(f"Backtest error: {msg}")

    def _switch_provider(self, mode: str) -> None:
        self.cfg.data_mode = mode
        try:
            self.market.provider.unsubscribe(self.pair, self.tf)
        except Exception:
            pass
        self.market.stop()
        self.market = MarketService(mode=mode)
        self.market.start()
        self._reload_series()
        self.market.subscribe(self.pair, self.tf, self._enqueue_candle)
        self._log(f"Data source switched to {mode}")

    def _refresh_status(self) -> None:
        msg = self.market.status()
        self.status_lbl.setText(msg)
        if "CONNECTED" in msg and "SIMULATED" not in msg:
            self.status_lbl.setStyleSheet(f"color:{ACCENT}; font-weight:600;")
        else:
            self.status_lbl.setStyleSheet(f"color:{WARN}; font-weight:600;")

    def _toggle_overlay(self) -> None:
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show()

    def _tick_clock(self) -> None:
        self.time_lbl.setText(format_clock())

    def _log(self, msg: str) -> None:
        logger.info(msg)
        self.logs_view.append(f"{format_clock()}  {msg}")
        try:
            self.repo.log_event("INFO", msg)
        except Exception:
            pass

    def closeEvent(self, event) -> None:
        self._alive = False
        self._pump.stop()
        self.market.stop()
        self.overlay.close()
        event.accept()
