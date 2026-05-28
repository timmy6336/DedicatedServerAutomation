"""
MainWindow — the top-level application window.

Layout:
  ┌──────────────────────────────────────────┐
  │  Title bar (app name + version)          │
  ├───────────┬──────────────────────────────┤
  │  Sidebar  │  Details panel               │
  │ (GameCard │                              │
  │  list)    │                              │
  └───────────┴──────────────────────────────┘
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import List, TYPE_CHECKING

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QSplitter,
)
from PyQt5.QtCore import Qt

from ui import theme
from ui.components.game_sidebar import GameSidebar
from ui.components.details_panel import DetailsPanel
import core.game_registry as game_registry

if TYPE_CHECKING:
    from core.game_model import GameModel

_APP_NAME    = "Dedicated Server Manager"
_APP_VERSION = "2.0"

# Absolute path to the src/ directory — used to resolve image paths
_SRC_DIR = Path(__file__).parent.parent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_APP_NAME)
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)
        self.setStyleSheet(theme.GLOBAL)

        games = game_registry.load_all()
        images_dir = str(_SRC_DIR)

        # Central widget
        central = QWidget()
        central.setStyleSheet(f"background: {theme.Colors.BG_BASE};")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Title bar
        title_bar = self._make_title_bar()
        root_layout.addWidget(title_bar)

        # Body (sidebar + details)
        body = QSplitter(Qt.Horizontal)
        body.setHandleWidth(1)
        body.setStyleSheet(
            f"QSplitter::handle {{ background: {theme.Colors.DIVIDER}; }}"
        )

        self._sidebar = GameSidebar(games, images_dir)
        self._details = DetailsPanel(images_dir)

        body.addWidget(self._sidebar)
        body.addWidget(self._details)
        body.setStretchFactor(0, 0)
        body.setStretchFactor(1, 1)
        body.setSizes([theme.Layout.SIDEBAR_W + 24, 900])

        root_layout.addWidget(body)

        # Wire sidebar → details
        self._sidebar.game_selected.connect(self._details.show_game)

        # Auto-select first game
        if games:
            self._sidebar.select_first()

    # ------------------------------------------------------------------

    def _make_title_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(48)
        bar.setStyleSheet(
            f"background-color: {theme.Colors.BG_SURFACE}; "
            f"border-bottom: 1px solid {theme.Colors.DIVIDER};"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(
            theme.Layout.MARGIN_LG, 0, theme.Layout.MARGIN_LG, 0
        )
        layout.setSpacing(theme.Layout.SPACING_MD)

        dot = QLabel()
        dot.setFixedSize(10, 10)
        dot.setStyleSheet(
            f"background-color: {theme.Colors.ACCENT}; "
            "border-radius: 5px;"
        )
        layout.addWidget(dot)

        title = QLabel(_APP_NAME)
        title.setStyleSheet(
            f"color: {theme.Colors.TEXT_PRIMARY}; "
            f"font-size: {theme.Fonts.SIZE_MD}px; "
            f"font-weight: 700; "
            f"font-family: {theme.Fonts.FAMILY}; "
            "background: transparent;"
        )
        layout.addWidget(title)
        layout.addStretch()

        ver = QLabel(f"v{_APP_VERSION}")
        ver.setStyleSheet(
            f"color: {theme.Colors.TEXT_DISABLED}; "
            f"font-size: {theme.Fonts.SIZE_XS}px; "
            f"font-family: {theme.Fonts.FAMILY}; "
            "background: transparent;"
        )
        layout.addWidget(ver)
        return bar
