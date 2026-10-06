from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

BG = "#07090c"
SURFACE = "#0e1318"
RAISED = "#151c24"
BORDER = "#1c262f"
FG = "#dce4ea"
MUTED = "#7a8894"
ACCENT = "#3d9cf0"
UP = "#3dcc8a"
DOWN = "#e85d5d"
WARN = "#d4a017"


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(BG))
    pal.setColor(QPalette.WindowText, QColor(FG))
    pal.setColor(QPalette.Base, QColor(SURFACE))
    pal.setColor(QPalette.AlternateBase, QColor(RAISED))
    pal.setColor(QPalette.Text, QColor(FG))
    pal.setColor(QPalette.Button, QColor(RAISED))
    pal.setColor(QPalette.ButtonText, QColor(FG))
    pal.setColor(QPalette.Highlight, QColor(ACCENT))
    pal.setColor(QPalette.HighlightedText, QColor(BG))
    pal.setColor(QPalette.ToolTipBase, QColor(RAISED))
    pal.setColor(QPalette.ToolTipText, QColor(FG))
    app.setPalette(pal)
    app.setStyleSheet(
        f"""
        QWidget {{ background: {BG}; color: {FG}; font-family: 'Segoe UI', 'IBM Plex Sans', sans-serif; font-size: 13px; }}
        QMainWindow {{ background: {BG}; }}
        QLabel {{ color: {FG}; }}
        QPushButton {{
            background: {RAISED}; border: 1px solid {BORDER}; border-radius: 4px;
            padding: 6px 12px; color: {FG};
        }}
        QPushButton:hover {{ border-color: {ACCENT}; }}
        QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {{
            background: {RAISED}; border: 1px solid {BORDER}; padding: 4px 8px; color: {FG};
        }}
        QTabWidget::pane {{ border: 1px solid {BORDER}; background: {SURFACE}; }}
        QTabBar::tab {{
            background: {RAISED}; color: {MUTED}; padding: 8px 14px; border: 1px solid {BORDER};
        }}
        QTabBar::tab:selected {{ color: {FG}; border-bottom: 2px solid {ACCENT}; }}
        QHeaderView::section {{ background: {RAISED}; color: {MUTED}; border: none; padding: 6px; }}
        QTableWidget {{ gridline-color: {BORDER}; background: {SURFACE}; }}
        QListWidget {{ background: {SURFACE}; border: none; }}
        QListWidget::item {{ padding: 8px 10px; border-bottom: 1px solid {BORDER}; }}
        QListWidget::item:selected {{ background: #1a2a3a; border-left: 3px solid {ACCENT}; }}
        QStatusBar {{ background: {SURFACE}; color: {MUTED}; border-top: 1px solid {BORDER}; }}
        QGroupBox {{ border: 1px solid {BORDER}; margin-top: 12px; padding: 8px; }}
        QScrollBar:vertical {{ background: {SURFACE}; width: 10px; }}
        QScrollBar::handle:vertical {{ background: {BORDER}; min-height: 24px; }}
        """
    )


def mono(size: int = 12, bold: bool = False) -> QFont:
    f = QFont("Consolas", size)
    f.setBold(bold)
    return f
