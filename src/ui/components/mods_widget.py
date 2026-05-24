"""
ModsWidget — mod manager tab shown inside the ConfigDialog.

Layout:
  1. BepInEx section  — install status + auto/manual install choice
  2. Drop zone        — drag .dll or .zip files to install
  3. Mod list         — checkboxes to enable/disable, remove button per mod
"""

from __future__ import annotations
import os
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QCheckBox, QComboBox, QProgressBar,
    QMessageBox, QFileDialog,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from ui import theme
from server import mod_manager

if TYPE_CHECKING:
    from core.game_model import GameModel


# ---------------------------------------------------------------------------
# Background thread for BepInEx installation
# ---------------------------------------------------------------------------

class _BepInExInstallThread(QThread):
    progress  = pyqtSignal(int)
    status_msg = pyqtSignal(str)
    finished  = pyqtSignal(bool)

    def __init__(self, game: "GameModel"):
        super().__init__()
        self._game = game

    def run(self):
        from server import bepinex
        ok = bepinex.install(self._game, self.progress.emit, self.status_msg.emit)
        self.finished.emit(ok)


# ---------------------------------------------------------------------------
# Drag-and-drop file drop zone
# ---------------------------------------------------------------------------

class _DropZone(QFrame):
    files_dropped = pyqtSignal(list)

    _IDLE_STYLE = (
        f"background: {theme.Colors.BG_ELEVATED}; "
        f"border: 2px dashed {theme.Colors.BORDER}; "
        f"border-radius: {theme.Layout.RADIUS_MD}px;"
    )
    _HOVER_STYLE = (
        f"background: {theme.Colors.BG_ELEVATED}; "
        f"border: 2px dashed {theme.Colors.ACCENT}; "
        f"border-radius: {theme.Layout.RADIUS_MD}px;"
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(72)
        self.setStyleSheet(self._IDLE_STYLE)

        lbl = QLabel("Drop .dll or .zip files here  (drag may not work when running as admin — use Browse instead)")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            f"color: {theme.Colors.TEXT_SECONDARY}; "
            f"font-size: {theme.Fonts.SIZE_SM}px; "
            f"font-family: {theme.Fonts.FAMILY}; "
            "background: transparent; border: none;"
        )
        layout = QVBoxLayout(self)
        layout.addWidget(lbl)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if any(
                u.toLocalFile().lower().endswith((".dll", ".zip"))
                for u in event.mimeData().urls()
            ):
                self.setStyleSheet(self._HOVER_STYLE)
                event.acceptProposedAction()
                return
        event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self._IDLE_STYLE)

    def dropEvent(self, event):
        self.setStyleSheet(self._IDLE_STYLE)
        files = [
            u.toLocalFile()
            for u in event.mimeData().urls()
            if u.toLocalFile().lower().endswith((".dll", ".zip"))
        ]
        if files:
            self.files_dropped.emit(files)


# ---------------------------------------------------------------------------
# Main widget
# ---------------------------------------------------------------------------

class ModsWidget(QWidget):
    def __init__(self, game: "GameModel", parent=None):
        super().__init__(parent)
        self._game = game
        self._install_thread: _BepInExInstallThread | None = None

        self.setAcceptDrops(True)
        self.setStyleSheet(f"background: {theme.Colors.BG_BASE};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            theme.Layout.MARGIN_LG, theme.Layout.MARGIN_LG,
            theme.Layout.MARGIN_LG, theme.Layout.MARGIN_LG,
        )
        outer.setSpacing(theme.Layout.SPACING_LG)

        outer.addWidget(self._make_bepinex_section())

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color: {theme.Colors.DIVIDER}; max-height:1px; border:none;")
        outer.addWidget(div)

        drop = _DropZone()
        drop.files_dropped.connect(self._on_files_dropped)
        outer.addWidget(drop)

        browse_row = QHBoxLayout()
        browse_row.addStretch()
        browse_btn = QPushButton("Browse for Mod Files…")
        browse_btn.setStyleSheet(theme.BTN_SECONDARY)
        browse_btn.clicked.connect(self._on_browse)
        browse_row.addWidget(browse_btn)
        outer.addLayout(browse_row)

        mods_lbl = QLabel("Installed Mods")
        mods_lbl.setStyleSheet(
            f"color: {theme.Colors.TEXT_PRIMARY}; "
            f"font-size: {theme.Fonts.SIZE_SM}px; font-weight: 700; "
            f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
        )
        outer.addWidget(mods_lbl)

        # Scrollable mod list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        self._list_container = QWidget()
        self._list_container.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(4)
        self._list_layout.addStretch()

        scroll.setWidget(self._list_container)
        outer.addWidget(scroll, stretch=1)

        self._refresh_mods()

    # ------------------------------------------------------------------
    # BepInEx section
    # ------------------------------------------------------------------

    def _make_bepinex_section(self) -> QWidget:
        from server import bepinex

        section = QFrame()
        section.setStyleSheet(
            f"background: {theme.Colors.BG_SURFACE}; "
            f"border-radius: {theme.Layout.RADIUS_MD}px; border: none;"
        )
        layout = QVBoxLayout(section)
        layout.setContentsMargins(
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
        )
        layout.setSpacing(theme.Layout.SPACING_SM)

        # Header row
        header = QHBoxLayout()
        title_lbl = QLabel("BepInEx Framework")
        title_lbl.setStyleSheet(
            f"color: {theme.Colors.TEXT_PRIMARY}; "
            f"font-size: {theme.Fonts.SIZE_SM}px; font-weight: 700; "
            f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
        )
        header.addWidget(title_lbl)
        header.addStretch()

        installed = bepinex.is_installed(self._game)
        status_color = theme.Colors.SUCCESS if installed else theme.Colors.WARNING
        status_text  = "Installed ✓" if installed else "Not installed"
        self._bepinex_status_lbl = QLabel(status_text)
        self._bepinex_status_lbl.setStyleSheet(
            f"color: {status_color}; "
            f"font-size: {theme.Fonts.SIZE_SM}px; "
            f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
        )
        header.addWidget(self._bepinex_status_lbl)
        layout.addLayout(header)

        if not installed:
            self._mode_combo = QComboBox()
            self._mode_combo.addItem("Auto-install BepInEx (Recommended)")
            self._mode_combo.addItem("I'll install it myself")
            layout.addWidget(self._mode_combo)

            self._install_btn = QPushButton("Install BepInEx")
            self._install_btn.setStyleSheet(theme.BTN_PRIMARY)
            self._install_btn.clicked.connect(self._on_install_bepinex)
            layout.addWidget(self._install_btn)

            self._bepinex_progress = QProgressBar()
            self._bepinex_progress.setStyleSheet(theme.PROGRESS_BAR)
            self._bepinex_progress.setVisible(False)
            layout.addWidget(self._bepinex_progress)

            self._bepinex_msg_lbl = QLabel("")
            self._bepinex_msg_lbl.setStyleSheet(
                f"color: {theme.Colors.TEXT_SECONDARY}; "
                f"font-size: {theme.Fonts.SIZE_XS}px; "
                f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
            )
            layout.addWidget(self._bepinex_msg_lbl)

            self._mode_combo.currentIndexChanged.connect(
                lambda idx: self._install_btn.setVisible(idx == 0)
            )

        return section

    def _on_install_bepinex(self):
        self._install_btn.setEnabled(False)
        self._bepinex_progress.setValue(0)
        self._bepinex_progress.setVisible(True)

        self._install_thread = _BepInExInstallThread(self._game)
        self._install_thread.progress.connect(self._bepinex_progress.setValue)
        self._install_thread.status_msg.connect(self._bepinex_msg_lbl.setText)
        self._install_thread.finished.connect(self._on_bepinex_done)
        self._install_thread.start()

    def _on_bepinex_done(self, success: bool):
        self._bepinex_progress.setVisible(False)
        if success:
            self._bepinex_status_lbl.setText("Installed ✓")
            self._bepinex_status_lbl.setStyleSheet(
                f"color: {theme.Colors.SUCCESS}; "
                f"font-size: {theme.Fonts.SIZE_SM}px; "
                f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
            )
            self._install_btn.setVisible(False)
            self._mode_combo.setVisible(False)
            self._bepinex_msg_lbl.setText("BepInEx installed successfully!")
        else:
            self._install_btn.setEnabled(True)

    # ------------------------------------------------------------------
    # Mod list
    # ------------------------------------------------------------------

    def _on_browse(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Mod Files",
            "",
            "Mod files (*.dll *.zip);;DLL files (*.dll);;ZIP files (*.zip)",
        )
        if files:
            self._on_files_dropped(files)

    def _on_files_dropped(self, files: list[str]):
        for path in files:
            names = mod_manager.install_mod(self._game, path)
            if not names:
                QMessageBox.warning(
                    self.window(), "Install Failed",
                    f"No mod files found in: {os.path.basename(path)}"
                )
        self._refresh_mods()

    def _refresh_mods(self):
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        mods = mod_manager.list_mods(self._game)

        if not mods:
            empty = QLabel("No mods installed — drop files above to add mods")
            empty.setStyleSheet(
                f"color: {theme.Colors.TEXT_DISABLED}; "
                f"font-size: {theme.Fonts.SIZE_SM}px; "
                f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
            )
            self._list_layout.insertWidget(0, empty)
            return

        for i, mod in enumerate(mods):
            self._list_layout.insertWidget(i, self._make_mod_row(mod))

    def _make_mod_row(self, mod: dict) -> QWidget:
        row = QWidget()
        row.setStyleSheet(
            f"background: {theme.Colors.BG_SURFACE}; "
            f"border-radius: {theme.Layout.RADIUS_SM}px;"
        )
        layout = QHBoxLayout(row)
        layout.setContentsMargins(
            theme.Layout.MARGIN_SM, theme.Layout.SPACING_SM,
            theme.Layout.MARGIN_SM, theme.Layout.SPACING_SM,
        )
        layout.setSpacing(theme.Layout.SPACING_MD)

        cb = QCheckBox(mod["name"])
        cb.setChecked(mod["enabled"])
        cb.setStyleSheet(
            f"color: {theme.Colors.TEXT_PRIMARY}; "
            f"font-size: {theme.Fonts.SIZE_SM}px; "
            f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
        )
        cb.toggled.connect(lambda checked, m=dict(mod): self._on_toggle(m, checked))
        layout.addWidget(cb)
        layout.addStretch()

        remove_btn = QPushButton("Remove")
        remove_btn.setStyleSheet(theme.BTN_DANGER)
        remove_btn.setFixedWidth(75)
        remove_btn.clicked.connect(lambda _, m=dict(mod): self._on_remove(m))
        layout.addWidget(remove_btn)

        return row

    def _on_toggle(self, mod: dict, enabled: bool):
        mod_manager.toggle_mod(mod, enabled)
        self._refresh_mods()

    def _on_remove(self, mod: dict):
        parent = self.window()
        reply = QMessageBox.question(
            parent, "Remove Mod",
            f"Remove \"{mod['name']}\"?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            ok = mod_manager.remove_mod(mod)
            if not ok:
                QMessageBox.warning(
                    parent, "Remove Failed",
                    f"Could not delete \"{mod['name']}\".\n"
                    "The file may already be gone or is in use.",
                )
            self._refresh_mods()
