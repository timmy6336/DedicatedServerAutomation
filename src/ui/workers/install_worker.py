"""
InstallWorker — background QThread for install/uninstall operations.

Signals:
    progress(int)   — 0-100
    status(str)     — human-readable line
    finished(bool)  — True=success
"""

from __future__ import annotations
import traceback
from typing import Callable, TYPE_CHECKING

from PyQt5.QtCore import QThread, pyqtSignal

from core import server_manager

if TYPE_CHECKING:
    from core.game_model import GameModel


class InstallWorker(QThread):
    progress = pyqtSignal(int)
    status   = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, game: "GameModel", parent=None):
        super().__init__(parent)
        self._game = game

    def run(self):
        try:
            ok = server_manager.install(
                self._game,
                progress=self.progress.emit,
                status=self.status.emit,
            )
            self.finished.emit(ok)
        except Exception:
            self.status.emit(f"Unexpected error:\n{traceback.format_exc()}")
            self.finished.emit(False)


class UninstallWorker(QThread):
    status   = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, game: "GameModel", parent=None):
        super().__init__(parent)
        self._game = game

    def run(self):
        try:
            self.status.emit(f"Stopping {self._game.name} server...")
            server_manager.stop(self._game)

            self.status.emit(f"Removing {self._game.name} installation...")
            ok = server_manager.uninstall(self._game)
            self.finished.emit(ok)
        except Exception:
            self.status.emit(f"Unexpected error:\n{traceback.format_exc()}")
            self.finished.emit(False)
