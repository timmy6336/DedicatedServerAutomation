"""
StatusWorker — background QThread for server status checks.

Two-stage approach:
  1. Fast check (no public IP) — emits immediately
  2. Full check (with public IP) — emits when done
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt5.QtCore import QThread, pyqtSignal

from core import server_detection

if TYPE_CHECKING:
    from core.game_model import GameModel
    from core.server_detection import ServerStatus


class StatusWorker(QThread):
    status_ready = pyqtSignal(object)   # emits ServerStatus

    def __init__(self, game: "GameModel", skip_public_ip: bool = False, parent=None):
        super().__init__(parent)
        self._game = game
        self._skip_public_ip = skip_public_ip
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        if self._cancelled:
            return
        status = server_detection.get_status(self._game, skip_public_ip=self._skip_public_ip)
        if not self._cancelled:
            self.status_ready.emit(status)
