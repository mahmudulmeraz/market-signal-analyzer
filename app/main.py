from __future__ import annotations

import sys
import traceback

from app.config.settings import APP_NAME, default_config, ensure_dirs
from app.utils.logging import logger


def main() -> int:
    ensure_dirs()
    try:
        from PySide6.QtWidgets import QApplication

        from app.ui.main_window import MainWindow
        from app.ui.theme import apply_theme
    except ImportError as exc:
        logger.error("PySide6 is required for the desktop UI: %s", exc)
        print("Install dependencies:  pip install -r requirements.txt")
        print("Then run:  python run.py")
        return 1

    cfg = default_config()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    apply_theme(app)
    try:
        win = MainWindow(cfg)
        win.show()
    except Exception:
        logger.error("startup failure\n%s", traceback.format_exc())
        raise
    logger.info("%s started (research + paper trading)", APP_NAME)
    return app.exec()
