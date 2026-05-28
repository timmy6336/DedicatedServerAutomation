"""
ProgressDialog — modal window shown during install/uninstall.

Shows a progress bar, a running log of status messages, and
a close/cancel button.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPlainTextEdit, QPushButton, QWidget,
)
from PyQt5.QtCore import Qt

from ui import theme

if TYPE_CHECKING:
    from core.game_model import GameModel


class ProgressDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(520, 380)
        self.setStyleSheet(
            theme.DIALOG
            + theme.PROGRESS_BAR
            + theme.LOG_AREA
            + theme.BTN_SECONDARY
            + theme.BTN_PRIMARY
        )
        self._done = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            theme.Layout.MARGIN_LG,
            theme.Layout.MARGIN_LG,
            theme.Layout.MARGIN_LG,
            theme.Layout.MARGIN_MD,
        )
        outer.setSpacing(theme.Layout.SPACING_MD)

        # Title label
        self._title_label = QLabel(title)
        self._title_label.setStyleSheet(
            f"color: {theme.Colors.TEXT_PRIMARY}; "
            f"font-size: {theme.Fonts.SIZE_MD}px; "
            f"font-weight: 700; "
            f"font-family: {theme.Fonts.FAMILY}; "
            "background: transparent;"
        )
        outer.addWidget(self._title_label)

        # Status line
        self._status_label = QLabel("Initialising...")
        self._status_label.setStyleSheet(
            f"color: {theme.Colors.TEXT_SECONDARY}; "
            f"font-size: {theme.Fonts.SIZE_SM}px; "
            f"font-family: {theme.Fonts.FAMILY}; "
            "background: transparent;"
        )
        self._status_label.setWordWrap(True)
        outer.addWidget(self._status_label)

        # Progress bar
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setFixedHeight(8)
        self._bar.setTextVisible(False)
        outer.addWidget(self._bar)

        # Log area
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setStyleSheet(theme.LOG_AREA)
        outer.addWidget(self._log)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn = QPushButton("Cancel")
        self._btn.setStyleSheet(theme.BTN_SECONDARY)
        self._btn.clicked.connect(self._on_btn_clicked)
        btn_row.addWidget(self._btn)
        outer.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Slots (thread-safe via queued signals)
    # ------------------------------------------------------------------

    def update_progress(self, value: int):
        self._bar.setValue(value)

    def update_status(self, message: str):
        self._status_label.setText(message)
        self._log.appendPlainText(message)
        # Scroll to bottom
        sb = self._log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def on_finished(self, success: bool):
        self._done = True
        if success:
            self._bar.setValue(100)
            self._status_label.setText("Completed successfully!")
            self._log.appendPlainText("\n--- Done ---")
            self._btn.setText("Close")
            self._btn.setStyleSheet(theme.BTN_PRIMARY)
        else:
            self._status_label.setText("Operation failed. See log for details.")
            self._log.appendPlainText("\n--- Failed ---")
            self._btn.setText("Close")
            self._btn.setStyleSheet(theme.BTN_DANGER)

    # ------------------------------------------------------------------

    def _on_btn_clicked(self):
        if self._done:
            self.accept()
        else:
            self.reject()
