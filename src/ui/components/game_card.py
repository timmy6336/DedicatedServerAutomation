"""
GameCard — a clickable sidebar card showing the game thumbnail + name + status.
"""

from __future__ import annotations
import os
from typing import Callable, Optional, TYPE_CHECKING

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import Qt, pyqtSignal

from ui import theme
from ui.components.status_badge import StatusBadge

if TYPE_CHECKING:
    from core.game_model import GameModel

_THUMB_W = 180
_THUMB_H = 100


class GameCard(QFrame):
    clicked = pyqtSignal(object)   # emits GameModel

    def __init__(self, game: "GameModel", images_base_dir: str, parent=None):
        super().__init__(parent)
        self._game = game
        self._selected = False

        self.setFixedWidth(theme.Layout.SIDEBAR_W)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(theme.GAME_CARD_NORMAL)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme.Layout.MARGIN_SM,
            theme.Layout.MARGIN_SM,
            theme.Layout.MARGIN_SM,
            theme.Layout.MARGIN_SM,
        )
        layout.setSpacing(theme.Layout.SPACING_SM)

        # --- thumbnail ---
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignCenter)
        self._image_label.setFixedHeight(_THUMB_H)
        self._image_label.setStyleSheet(
            "background: transparent; border: none;"
        )
        self._load_image(game.image, images_base_dir)
        layout.addWidget(self._image_label)

        # --- game name ---
        name_label = QLabel(game.name)
        name_label.setStyleSheet(
            f"color: {theme.Colors.TEXT_PRIMARY}; "
            f"font-size: {theme.Fonts.SIZE_SM}px; "
            f"font-weight: 600; "
            f"font-family: {theme.Fonts.FAMILY}; "
            "background: transparent; border: none;"
        )
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        # --- status badge ---
        self._badge = StatusBadge("unknown")
        layout.addWidget(self._badge)

    # ------------------------------------------------------------------

    def _load_image(self, rel_path: str, base_dir: str):
        if not rel_path:
            self._image_label.setText(self._game.name[0])
            return

        full_path = os.path.join(base_dir, rel_path)
        if not os.path.exists(full_path):
            self._image_label.setText(self._game.name[0])
            return

        pix = QPixmap(full_path)
        if pix.isNull():
            self._image_label.setText(self._game.name[0])
            return

        scaled = pix.scaled(
            _THUMB_W, _THUMB_H,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._image_label.setPixmap(scaled)

    def set_status(self, state: str):
        self._badge.set_state(state)

    def set_selected(self, selected: bool):
        self._selected = selected
        self.setStyleSheet(
            theme.GAME_CARD_SELECTED if selected else theme.GAME_CARD_NORMAL
        )

    # ------------------------------------------------------------------
    # Mouse events
    # ------------------------------------------------------------------

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._game)
        super().mousePressEvent(event)
