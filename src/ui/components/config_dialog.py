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
    QPushButton, QFrame, QScrollArea, QWidget, QSizePolicy, QTabWidget,
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
import os
import platform

from ui import theme

if TYPE_CHECKING:
    from core.game_model import GameModel, SettingDef

_TAB_STYLE = f"""
    QTabWidget::pane {{
        background: {theme.Colors.BG_SURFACE};
        border: none;
    }}
    QTabBar::tab {{
        background: {theme.Colors.BG_BASE};
        color: {theme.Colors.TEXT_SECONDARY};
        padding: 8px 24px;
        border: none;
        font-size: {theme.Fonts.SIZE_SM}px;
        font-family: {theme.Fonts.FAMILY};
    }}
    QTabBar::tab:selected {{
        color: {theme.Colors.TEXT_PRIMARY};
        border-bottom: 2px solid {theme.Colors.ACCENT};
        background: {theme.Colors.BG_SURFACE};
    }}
    QTabBar::tab:hover:!selected {{
        color: {theme.Colors.TEXT_PRIMARY};
        background: {theme.Colors.BG_ELEVATED};
    }}
"""


class WorldPickerWidget(QWidget):
    """
    Combo + optional text input for selecting or naming a Valheim world.
    Shows worlds found on disk; selecting "New World..." reveals a name field.
    """
    _NEW = "New World..."

    def __init__(self, setting: "SettingDef", current_value: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._combo = QComboBox()
        worlds = self._scan(setting)
        for w in worlds:
            self._combo.addItem(w)
        self._combo.addItem(self._NEW)
        layout.addWidget(self._combo)

        self._new_edit = QLineEdit()
        self._new_edit.setPlaceholderText("Enter new world name…")
        layout.addWidget(self._new_edit)

        # Restore previous value
        idx = self._combo.findText(current_value)
        if idx >= 0:
            self._combo.setCurrentIndex(idx)
        else:
            # Value not in list — pre-fill new-world field
            self._combo.setCurrentText(self._NEW)
            if current_value:
                self._new_edit.setText(current_value)

        self._combo.currentTextChanged.connect(self._sync_visibility)
        self._sync_visibility(self._combo.currentText())

    def _sync_visibility(self, text: str) -> None:
        self._new_edit.setVisible(text == self._NEW)

    def _scan(self, setting: "SettingDef") -> list[str]:
        if platform.system().lower() == "windows":
            raw = setting.worlds_path_windows
            path = os.path.expandvars(raw) if raw else ""
        else:
            raw = setting.worlds_path_linux
            path = os.path.expanduser(raw) if raw else ""

        if not path or not os.path.isdir(path):
            return []
        try:
            names = [f[:-4] for f in os.listdir(path) if f.endswith(".fwl")]
            return sorted(names)
        except OSError:
            return []

    def get_value(self) -> str:
        if self._combo.currentText() == self._NEW:
            return self._new_edit.text().strip()
        return self._combo.currentText()

    def setToolTip(self, tip: str) -> None:
        super().setToolTip(tip)
        self._combo.setToolTip(tip)


class ConfigDialog(QDialog):
    def __init__(self, game: "GameModel", current_config: dict, parent=None):
        super().__init__(parent)
        self._game = game
        self._widgets: Dict[str, Any] = {}

        self.setWindowTitle(f"{game.name} — Server Configuration")
        self.setMinimumWidth(540)
        self.setMinimumHeight(400)
        self.setAcceptDrops(True)
        self.setStyleSheet(
            theme.DIALOG + theme.INPUT + theme.CHECKBOX
            + theme.BTN_PRIMARY + theme.BTN_SECONDARY + _TAB_STYLE
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Tab widget
        tabs = QTabWidget()
        tabs.addTab(self._make_settings_tab(game, current_config), "Settings")
        if game.mod_support:
            if game.mod_support.framework == "steam_workshop":
                from ui.components.dst_mods_widget import DSTModsWidget
                tabs.addTab(DSTModsWidget(game), "Mods")
            else:
                from ui.components.mods_widget import ModsWidget
                tabs.addTab(ModsWidget(game), "Mods")
        outer.addWidget(tabs)

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

    def _make_settings_tab(self, game: "GameModel", current_config: dict) -> QWidget:
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

            form_layout.addRow(label, self._wrap_with_link(widget, setting))

        scroll.setWidget(content)
        return scroll

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

        elif s.type == "world_picker":
            return WorldPickerWidget(s, str(value))

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

    def _read_widget_value(self, setting: "SettingDef", w: Any) -> Any:
        if setting.type in ("string", "password"):
            return w.text()
        if setting.type == "int":
            return w.value()
        if setting.type == "bool":
            return w.isChecked()
        if setting.type in ("choice",):
            return w.currentText()
        if setting.type == "world_picker":
            return w.get_value()
        return setting.default

    def _validate(self, config: dict) -> str | None:
        """Return an (title, message) pair if invalid, else None."""
        from PyQt5.QtWidgets import QMessageBox
        for setting in self._game.server_settings:
            val = config.get(setting.key, "")
            if setting.required and not val:
                QMessageBox.warning(self, "Required field", f'"{setting.label}" is required.')
                return "invalid"
            if setting.type in ("string", "password") and setting.min_length:
                if len(str(val)) < setting.min_length:
                    QMessageBox.warning(
                        self, "Field too short",
                        f'"{setting.label}" must be at least {setting.min_length} characters.',
                    )
                    return "invalid"
        return None

    def _on_save(self):
        config = {}
        for setting in self._game.server_settings:
            w = self._widgets.get(setting.key)
            config[setting.key] = (
                self._read_widget_value(setting, w) if w is not None else setting.default
            )

        if self._validate(config) is not None:
            return

        self._result_config = config
        self.accept()

    def get_config(self) -> dict:
        """Call after exec_() returns QDialog.Accepted."""
        return self._result_config
