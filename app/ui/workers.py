from __future__ import annotations

from typing import Callable, List

from PySide6.QtCore import QObject, QThread, Qt, Signal

from app.backtesting.engine import BacktestEngine
from app.backtesting.validation import train_validate_test
from app.backtesting.walk_forward import walk_forward
from app.config.indicator_config import AppConfig
from app.core.models import Candle


class BacktestWorker(QObject):
    finished = Signal(str, object)
    failed = Signal(str)

    def __init__(self, cfg: AppConfig, candles: List[Candle], mode: str):
        super().__init__()
        self.cfg = cfg
        self.candles = candles
        self.mode = mode

    def run(self) -> None:
        try:
            if self.mode == "full":
                res = BacktestEngine(self.cfg).run(self.candles, split="FULL")
                self.finished.emit("Historical backtest (full sample)", res["metrics"])
            elif self.mode == "oos":
                splits = train_validate_test(self.candles, self.cfg)
                text = {
                    "train": splits["train"]["metrics"],
                    "validation": splits["validation"]["metrics"],
                    "out_of_sample": splits["out_of_sample"]["metrics"],
                }
                self.finished.emit("Train / validation / out-of-sample", text)
            else:
                wf = walk_forward(self.candles, self.cfg)
                self.finished.emit("Walk-forward aggregate", wf["aggregate"])
        except Exception as exc:
            self.failed.emit(str(exc))


def start_backtest(
    cfg: AppConfig,
    candles: List[Candle],
    mode: str,
    on_done: Callable,
    on_fail: Callable,
) -> QThread:
    thread = QThread()
    worker = BacktestWorker(cfg, candles, mode)
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.finished.connect(on_done, Qt.QueuedConnection)
    worker.failed.connect(on_fail, Qt.QueuedConnection)
    worker.finished.connect(thread.quit)
    worker.failed.connect(thread.quit)
    thread.start()
    thread.worker = worker
    return thread
