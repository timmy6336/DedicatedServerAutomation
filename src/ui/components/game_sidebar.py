"""
GameSidebar — left panel containing a scrollable list of GameCards.
"""

from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal

from ui import theme
from ui.components.game_card import GameCard

if TYPE_CHECKING:
    from core.game_model import GameModel


class GameSidebar(QWidget):
    game_selected = pyqtSignal(object)   # emits GameModel

    def __init__(self, games: List["GameModel"], images_base_dir: str, parent=None):
        super().__init__(parent)
        self.setFixedWidth(theme.Layout.SIDEBAR_W + 24)  # card width + padding
        self.setStyleSheet(
            f"background-color: {theme.Colors.BG_SIDEBAR}; "
            f"border-right: 1px solid {theme.Colors.DIVIDER};"
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header
        header = QLabel("Games")
        header.setStyleSheet(
            f"color: {theme.Colors.TEXT_SECONDARY}; "
            f"font-size: {theme.Fonts.SIZE_XS}px; "
            f"font-weight: 700; "
            f"letter-spacing: 1px; "
            f"font-family: {theme.Fonts.FAMILY}; "
            f"padding: {theme.Layout.MARGIN_MD}px {theme.Layout.MARGIN_MD}px "
            f"{theme.Layout.MARGIN_SM}px {theme.Layout.MARGIN_MD}px; "
            "background: transparent; "
            "text-transform: uppercase;"
        )
        outer.addWidget(header)

        # Scrollable card list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        card_layout = QVBoxLayout(container)
        card_layout.setContentsMargins(
            theme.Layout.MARGIN_SM,
            0,
            theme.Layout.MARGIN_SM,
            theme.Layout.MARGIN_SM,
        )
        card_layout.setSpacing(theme.Layout.SPACING_SM)

        self._cards: Dict[str, GameCard] = {}
        self._selected_id: str = ""

        for game in games:
            card = GameCard(game, images_base_dir)
            card.clicked.connect(self._on_card_clicked)
            self._cards[game.id] = card
            card_layout.addWidget(card)

        card_layout.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

    # ------------------------------------------------------------------

    def _on_card_clicked(self, game: "GameModel"):
        self._select(game.id)
        self.game_selected.emit(game)

    def _select(self, game_id: str):
        if self._selected_id and self._selected_id in self._cards:
            self._cards[self._selected_id].set_selected(False)
        self._selected_id = game_id
        if game_id in self._cards:
            self._cards[game_id].set_selected(True)

    def select_first(self):
        """Select and emit the first game in the list."""
        if self._cards:
            first_id = next(iter(self._cards))
            card = self._cards[first_id]
            self._select(first_id)
            self.game_selected.emit(card._game)

    def set_game_status(self, game_id: str, state: str):
        if game_id in self._cards:
            self._cards[game_id].set_status(state)
