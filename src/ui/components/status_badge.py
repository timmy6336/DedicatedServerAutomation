"""
StatusBadge — a small colored dot + label widget indicating server state.

States: "running", "stopped", "installing", "unknown"
"""

from __future__ import annotations
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from ui import theme


_DOT_COLORS = {
    "running":    theme.Colors.SUCCESS,
    "stopped":    theme.Colors.ERROR,
    "installing": theme.Colors.WARNING,
    "unknown":    theme.Colors.MUTED,
}

_LABELS = {
    "running":    "Running",
    "stopped":    "Not Running",
    "installing": "Installing...",
    "unknown":    "Unknown",
}


class StatusBadge(QWidget):
    def __init__(self, state: str = "unknown", parent=None):
        super().__init__(parent)
        self._state = state

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._dot = QLabel()
        self._dot.setFixedSize(10, 10)

        self._text = QLabel()
        self._text.setStyleSheet(
            f"color: {theme.Colors.TEXT_SECONDARY}; "
            f"font-size: {theme.Fonts.SIZE_SM}px; "
            f"font-family: {theme.Fonts.FAMILY}; "
            "background: transparent;"
        )

        layout.addWidget(self._dot)
        layout.addWidget(self._text)
        layout.addStretch()

        self.set_state(state)

    def set_state(self, state: str):
        self._state = state
        color = _DOT_COLORS.get(state, theme.Colors.MUTED)
        label = _LABELS.get(state, state.title())

        self._dot.setStyleSheet(
            f"background-color: {color}; "
            "border-radius: 5px;"
        )
        self._text.setText(label)
        self._text.setStyleSheet(
            f"color: {color}; "
            f"font-size: {theme.Fonts.SIZE_SM}px; "
            f"font-family: {theme.Fonts.FAMILY}; "
            "font-weight: 600; "
            "background: transparent;"
        )
