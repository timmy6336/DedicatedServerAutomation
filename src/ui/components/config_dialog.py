"""
ConfigDialog — a generic settings form built from GameModel.server_settings.

Renders each SettingDef as the appropriate Qt widget:
  string   → QLineEdit
  password → QLineEdit (echoMode=Password) + optional help URL link
  int      → QSpinBox
  bool     → QCheckBox
  choice   → QComboBox
"""

from __future__ import annotations
from typing import Any, Dict, TYPE_CHECKING

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QCheckBox, QComboBox,
    QPushButton, QFrame, QScrollArea, QWidget, QSizePolicy,
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices

from ui import theme

if TYPE_CHECKING:
    from core.game_model import GameModel, SettingDef


class ConfigDialog(QDialog):
    def __init__(self, game: "GameModel", current_config: dict, parent=None):
        super().__init__(parent)
        self._game = game
        self._widgets: Dict[str, Any] = {}

        self.setWindowTitle(f"{game.name} — Server Configuration")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        self.setStyleSheet(theme.DIALOG + theme.INPUT + theme.CHECKBOX + theme.BTN_PRIMARY + theme.BTN_SECONDARY)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Scrollable form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        content = QWidget()
        content.setStyleSheet(f"background: {theme.Colors.BG_SURFACE};")
        form_layout = QFormLayout(content)
        form_layout.setContentsMargins(
            theme.Layout.MARGIN_LG,
            theme.Layout.MARGIN_LG,
            theme.Layout.MARGIN_LG,
            theme.Layout.MARGIN_MD,
        )
        form_layout.setSpacing(theme.Layout.SPACING_MD)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        for setting in game.server_settings:
            widget = self._make_widget(setting, current_config)
            if widget is None:
                continue
            self._widgets[setting.key] = widget

            label = QLabel(setting.label + ("*" if setting.required else ""))
            label.setStyleSheet(
                f"color: {theme.Colors.TEXT_PRIMARY}; "
                f"font-size: {theme.Fonts.SIZE_SM}px; "
                f"font-family: {theme.Fonts.FAMILY}; "
                "background: transparent;"
            )
            if setting.tooltip:
                label.setToolTip(setting.tooltip)
                widget.setToolTip(setting.tooltip)

            row_widget = self._wrap_with_link(widget, setting)
            form_layout.addRow(label, row_widget)

        scroll.setWidget(content)
        outer.addWidget(scroll)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {theme.Colors.DIVIDER};")
        outer.addWidget(sep)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(
            theme.Layout.MARGIN_LG, theme.Layout.MARGIN_MD,
            theme.Layout.MARGIN_LG, theme.Layout.MARGIN_MD,
        )
        btn_row.setSpacing(theme.Layout.SPACING_MD)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(theme.BTN_SECONDARY)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(theme.BTN_PRIMARY)
        save_btn.clicked.connect(self._on_save)
        save_btn.setDefault(True)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)

        btn_container = QWidget()
        btn_container.setStyleSheet(f"background: {theme.Colors.BG_SURFACE};")
        btn_container.setLayout(btn_row)
        outer.addWidget(btn_container)

        self._result_config: dict = {}

    # ------------------------------------------------------------------
    # Widget factory
    # ------------------------------------------------------------------

    def _make_widget(self, s: "SettingDef", current: dict) -> Any:
        value = current.get(s.key, s.default)

        if s.type == "string":
            w = QLineEdit()
            w.setText(str(value))
            if s.placeholder:
                w.setPlaceholderText(s.placeholder)
            if s.max_length:
                w.setMaxLength(s.max_length)
            return w

        elif s.type == "password":
            w = QLineEdit()
            w.setEchoMode(QLineEdit.Password)
            w.setText(str(value))
            if s.placeholder:
                w.setPlaceholderText(s.placeholder)
            return w

        elif s.type == "int":
            w = QSpinBox()
            w.setMinimum(s.min)
            w.setMaximum(s.max)
            w.setValue(int(value) if value != "" else s.default)
            return w

        elif s.type == "bool":
            w = QCheckBox()
            w.setChecked(bool(value))
            return w

        elif s.type == "choice":
            w = QComboBox()
            for opt in s.options:
                w.addItem(str(opt))
            idx = w.findText(str(value))
            if idx >= 0:
                w.setCurrentIndex(idx)
            return w

        return None

    def _wrap_with_link(self, widget: Any, s: "SettingDef") -> QWidget:
        """If the setting has a help_url, add a clickable link beneath the widget."""
        if not s.help_url:
            return widget

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        vl = QVBoxLayout(container)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(4)
        vl.addWidget(widget)

        link = QLabel(f'<a href="{s.help_url}" style="color: {theme.Colors.ACCENT};">Get token ↗</a>')
        link.setOpenExternalLinks(True)
        link.setStyleSheet(
            f"font-size: {theme.Fonts.SIZE_XS}px; "
            f"font-family: {theme.Fonts.FAMILY}; "
            "background: transparent;"
        )
        vl.addWidget(link)
        return container

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _on_save(self):
        config = {}
        for setting in self._game.server_settings:
            w = self._widgets.get(setting.key)
            if w is None:
                config[setting.key] = setting.default
                continue

            if setting.type in ("string", "password"):
                config[setting.key] = w.text()
            elif setting.type == "int":
                config[setting.key] = w.value()
            elif setting.type == "bool":
                config[setting.key] = w.isChecked()
            elif setting.type == "choice":
                config[setting.key] = w.currentText()
            else:
                config[setting.key] = setting.default

        # Basic validation
        for setting in self._game.server_settings:
            if setting.required:
                val = config.get(setting.key, "")
                if not val:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        self,
                        "Required field",
                        f'"{setting.label}" is required.',
                    )
                    return
            if setting.type in ("string", "password") and setting.min_length:
                val = config.get(setting.key, "")
                if len(str(val)) < setting.min_length:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        self,
                        "Field too short",
                        f'"{setting.label}" must be at least {setting.min_length} characters.',
                    )
                    return

        self._result_config = config
        self.accept()

    def get_config(self) -> dict:
        """Call after exec_() returns QDialog.Accepted."""
        return self._result_config
