"""
Entry point for the Dedicated Server Manager.

Run with:
    python src/main.py
"""

import sys
import os

# Ensure src/ is on the Python path so that `import core`, `import ui`,
# `import server` all resolve correctly regardless of CWD.
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# These MUST be set as class attributes before QApplication is instantiated.
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

from ui.main_window import MainWindow
from ui import theme
from core.logging_utils import cleanup_old_logs


def main():
    # Rotate old log files
    try:
        cleanup_old_logs()
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName("Dedicated Server Manager")
    app.setApplicationVersion("2.0")

    # Default font
    font = QFont(theme.Fonts.FAMILY, theme.Fonts.SIZE_BASE)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
