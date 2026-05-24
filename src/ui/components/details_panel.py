"""
DetailsPanel — the right-hand panel showing one game's full details.

Sections:
  1. Hero image + game name + genre
  2. Server status row (badge + IP info)
  3. Action buttons (Install / Start / Stop / Configure / Uninstall)
  4. Install progress (shown only during install)
  5. Log area (always visible while installing)
"""

from __future__ import annotations
import os
from typing import Optional, TYPE_CHECKING

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QMessageBox,
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSlot

from ui import theme
from ui.components.status_badge import StatusBadge
from ui.components.progress_dialog import ProgressDialog
from ui.components.config_dialog import ConfigDialog
from ui.workers.status_worker import StatusWorker
from ui.workers.install_worker import InstallWorker, UninstallWorker
from core import server_detection, server_manager
from core.config_manager import config_manager

if TYPE_CHECKING:
    from core.game_model import GameModel
    from core.server_detection import ServerStatus

_HERO_H = 200
_REFRESH_INTERVAL_MS = 10_000   # 10 seconds


class DetailsPanel(QWidget):
    def __init__(self, images_base_dir: str, parent=None):
        super().__init__(parent)
        self._images_base = images_base_dir
        self._game: Optional["GameModel"] = None
        self._status_worker: Optional[StatusWorker] = None
        # Keeps Python references to workers that are cancelled but still
        # running their OS thread.  Without this, Python's GC destroys the
        # object before the thread finishes, causing Qt's warning.
        self._live_workers: list = []
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_status)

        self.setStyleSheet(f"background-color: {theme.Colors.BG_BASE};")

        # Main layout with scroll
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # We want the scroll to fill the panel
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll)

        self._content = QWidget()
        self._content.setStyleSheet(f"background: {theme.Colors.BG_BASE};")
        scroll.setWidget(self._content)

        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addStretch()

        self._build_placeholder()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show_game(self, game: "GameModel"):
        self._game = game
        self._stop_status_worker()
        self._refresh_timer.stop()
        self._rebuild_ui()
        self._refresh_status_fast()   # immediate local-only refresh
        self._refresh_status()        # full refresh (public IP)
        self._refresh_timer.start(_REFRESH_INTERVAL_MS)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _rebuild_ui(self):
        """Tear down and rebuild the details panel for the current game."""
        # Remove all widgets except the stretch at the end
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        game = self._game
        if game is None:
            return

        # 1. Hero image
        hero = self._make_hero(game)
        self._layout.insertWidget(0, hero)

        # 2. Info section
        info = self._make_info(game)
        self._layout.insertWidget(1, info)

    def _build_placeholder(self):
        label = QLabel("Select a game from the sidebar")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            f"color: {theme.Colors.TEXT_DISABLED}; "
            f"font-size: {theme.Fonts.SIZE_MD}px; "
            f"font-family: {theme.Fonts.FAMILY}; "
            "background: transparent;"
        )
        self._layout.insertWidget(0, label)

    def _make_hero(self, game: "GameModel") -> QWidget:
        frame = QFrame()
        frame.setStyleSheet(f"background: {theme.Colors.BG_SURFACE};")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Image
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setFixedHeight(_HERO_H)
        img_label.setStyleSheet(f"background: {theme.Colors.BG_ELEVATED};")

        if game.image:
            full = os.path.join(self._images_base, game.image)
            pix = QPixmap(full)
            if not pix.isNull():
                scaled = pix.scaled(
                    1200, _HERO_H,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation,
                )
                img_label.setPixmap(scaled)

        layout.addWidget(img_label)

        # Title bar below hero
        title_bar = QWidget()
        title_bar.setStyleSheet(f"background: {theme.Colors.BG_SURFACE};")
        tbl = QHBoxLayout(title_bar)
        tbl.setContentsMargins(
            theme.Layout.MARGIN_LG, theme.Layout.MARGIN_MD,
            theme.Layout.MARGIN_LG, theme.Layout.MARGIN_MD,
        )
        tbl.setSpacing(theme.Layout.SPACING_MD)

        name_label = QLabel(game.name)
        name_label.setStyleSheet(
            f"color: {theme.Colors.TEXT_PRIMARY}; "
            f"font-size: {theme.Fonts.SIZE_XL}px; "
            f"font-weight: 700; "
            f"font-family: {theme.Fonts.FAMILY}; "
            "background: transparent;"
        )
        tbl.addWidget(name_label)
        tbl.addStretch()

        genre_label = QLabel(game.genre)
        genre_label.setStyleSheet(
            f"color: {theme.Colors.TEXT_SECONDARY}; "
            f"font-size: {theme.Fonts.SIZE_SM}px; "
            f"font-family: {theme.Fonts.FAMILY}; "
            "background: transparent;"
        )
        tbl.addWidget(genre_label)
        layout.addWidget(title_bar)

        return frame

    def _make_info(self, game: "GameModel") -> QWidget:
        container = QWidget()
        container.setStyleSheet(f"background: {theme.Colors.BG_BASE};")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(
            theme.Layout.MARGIN_LG, theme.Layout.MARGIN_LG,
            theme.Layout.MARGIN_LG, theme.Layout.MARGIN_LG,
        )
        layout.setSpacing(theme.Layout.SPACING_LG)

        # Status row
        status_row = QHBoxLayout()
        status_row.setSpacing(theme.Layout.SPACING_LG)

        self._badge = StatusBadge("unknown")
        status_row.addWidget(self._badge)
        status_row.addStretch()
        layout.addLayout(status_row)

        # IP info card
        self._ip_card = self._make_ip_card()
        layout.addWidget(self._ip_card)

        # Firewall warning
        self._fw_warning = QLabel("⚠  Port not open. Ensure you are running as administrator.")
        self._fw_warning.setWordWrap(True)
        self._fw_warning.setStyleSheet(
            f"color: {theme.Colors.WARNING}; "
            f"font-size: {theme.Fonts.SIZE_SM}px; "
            f"font-family: {theme.Fonts.FAMILY}; "
            "background: transparent;"
        )
        self._fw_warning.setVisible(False)
        layout.addWidget(self._fw_warning)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color: {theme.Colors.DIVIDER}; max-height:1px;")
        layout.addWidget(div)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(theme.Layout.SPACING_MD)

        self._install_btn = QPushButton("Install Server")
        self._install_btn.setStyleSheet(theme.BTN_PRIMARY)
        self._install_btn.clicked.connect(self._on_install)

        self._start_btn = QPushButton("Start Server")
        self._start_btn.setStyleSheet(theme.BTN_SUCCESS)
        self._start_btn.clicked.connect(self._on_start)

        self._stop_btn = QPushButton("Stop Server")
        self._stop_btn.setStyleSheet(theme.BTN_DANGER)
        self._stop_btn.clicked.connect(self._on_stop)

        self._close_ports_btn = QPushButton("Close Ports")
        self._close_ports_btn.setStyleSheet(theme.BTN_SECONDARY)
        self._close_ports_btn.setToolTip("Remove firewall rules and UPnP mappings for this server")
        self._close_ports_btn.clicked.connect(self._on_close_ports)

        self._config_btn = QPushButton("Configure")
        self._config_btn.setStyleSheet(theme.BTN_SECONDARY)
        self._config_btn.clicked.connect(self._on_configure)

        self._uninstall_btn = QPushButton("Uninstall")
        self._uninstall_btn.setStyleSheet(theme.BTN_DANGER)
        self._uninstall_btn.clicked.connect(self._on_uninstall)

        btn_row.addWidget(self._install_btn)
        btn_row.addWidget(self._start_btn)
        btn_row.addWidget(self._stop_btn)
        btn_row.addWidget(self._close_ports_btn)
        btn_row.addWidget(self._config_btn)
        btn_row.addStretch()
        btn_row.addWidget(self._uninstall_btn)
        layout.addLayout(btn_row)

        # Description
        if game.description:
            desc = QLabel(game.description)
            desc.setWordWrap(True)
            desc.setStyleSheet(
                f"color: {theme.Colors.TEXT_SECONDARY}; "
                f"font-size: {theme.Fonts.SIZE_SM}px; "
                f"font-family: {theme.Fonts.FAMILY}; "
                "background: transparent;"
            )
            layout.addWidget(desc)

        layout.addStretch()

        # Apply initial installed state
        self._update_buttons(installed=game.is_installed(), running=False)
        return container

    def _make_ip_card(self) -> QWidget:
        card = QFrame()
        card.setStyleSheet(
            f"background: {theme.Colors.BG_SURFACE}; "
            f"border-radius: {theme.Layout.RADIUS_MD}px; "
            "border: none;"
        )
        layout = QHBoxLayout(card)
        layout.setContentsMargins(
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
        )
        layout.setSpacing(theme.Layout.SPACING_LG)

        def _kv(key: str, val: str = "—"):
            col = QVBoxLayout()
            col.setSpacing(4)
            k_lbl = QLabel(key)
            k_lbl.setStyleSheet(
                f"color: {theme.Colors.TEXT_DISABLED}; "
                f"font-size: {theme.Fonts.SIZE_XS}px; "
                f"font-family: {theme.Fonts.FAMILY}; "
                "font-weight: 700; text-transform: uppercase; background: transparent;"
            )
            v_lbl = QLabel(val)
            v_lbl.setStyleSheet(
                f"color: {theme.Colors.TEXT_PRIMARY}; "
                f"font-size: {theme.Fonts.SIZE_SM}px; "
                f"font-family: {theme.Fonts.FAMILY}; "
                "font-weight: 600; background: transparent;"
            )
            v_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            col.addWidget(k_lbl)
            col.addWidget(v_lbl)
            return col, v_lbl

        local_col,  self._local_ip_lbl  = _kv("Local IP")
        public_col, self._public_ip_lbl = _kv("Public IP")
        port_col,   self._port_lbl      = _kv("Port")
        conn_col,   self._conn_lbl      = _kv("Connect (LAN)")

        layout.addLayout(local_col)
        layout.addLayout(public_col)
        layout.addLayout(port_col)
        layout.addLayout(conn_col)
        layout.addStretch()
        return card

    # ------------------------------------------------------------------
    # Status refresh
    # ------------------------------------------------------------------

    def _refresh_status_fast(self):
        self._start_status_worker(skip_public_ip=True)

    def _refresh_status(self):
        self._start_status_worker(skip_public_ip=False)

    def _start_status_worker(self, skip_public_ip: bool):
        if self._game is None:
            return
        self._stop_status_worker()
        worker = StatusWorker(self._game, skip_public_ip=skip_public_ip)
        worker.status_ready.connect(self._on_status_ready)
        self._status_worker = worker
        self._live_workers.append(worker)
        # Once the thread finishes, remove from the live list so GC can collect it.
        worker.finished.connect(lambda w=worker: self._live_workers.remove(w)
                                if w in self._live_workers else None)
        worker.start()

    def _stop_status_worker(self):
        if self._status_worker:
            self._status_worker.cancel()
            # Disconnect our result slot — the worker stays in _live_workers
            # (holding the Python reference) until its thread actually finishes.
            try:
                self._status_worker.status_ready.disconnect(self._on_status_ready)
            except TypeError:
                pass
            self._status_worker = None

    @pyqtSlot(object)
    def _on_status_ready(self, status: "ServerStatus"):
        if not hasattr(self, "_badge"):
            return

        state = "running" if status.is_running else "stopped"
        self._badge.set_state(state)

        self._local_ip_lbl.setText(status.local_ip)
        if status.public_ip and status.public_ip != "Unable to determine":
            self._public_ip_lbl.setText(status.public_ip)
        if status.port:
            self._port_lbl.setText(str(status.port))
        if status.connection_string:
            self._conn_lbl.setText(status.connection_string)

        if hasattr(self, "_fw_warning"):
            self._fw_warning.setVisible(status.is_running and not status.firewall_ok)

        self._update_buttons(
            installed=self._game.is_installed() if self._game else False,
            running=status.is_running,
        )

    # ------------------------------------------------------------------
    # Button state management
    # ------------------------------------------------------------------

    def _update_buttons(self, installed: bool, running: bool):
        if not hasattr(self, "_install_btn"):
            return
        self._install_btn.setVisible(not installed)
        self._start_btn.setVisible(installed and not running)
        self._stop_btn.setVisible(installed and running)
        self._close_ports_btn.setVisible(installed)
        self._config_btn.setVisible(installed)
        self._uninstall_btn.setVisible(installed)

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------

    def _on_install(self):
        if not self._game:
            return
        dlg = ProgressDialog(f"Installing {self._game.name}", parent=self)
        worker = InstallWorker(self._game)
        worker.progress.connect(dlg.update_progress)
        worker.status.connect(dlg.update_status)
        worker.finished.connect(dlg.on_finished)
        worker.finished.connect(self._on_install_finished)
        worker.start()
        dlg.exec_()

    def _on_install_finished(self, success: bool):
        if success:
            self._refresh_status_fast()

    def _on_start(self):
        if not self._game:
            return
        saved = config_manager.load(self._game.id)

        # Prompt to configure if: no config saved yet, or any required field is blank
        needs_config = saved is None
        if not needs_config and self._game.server_settings:
            for setting in self._game.server_settings:
                if setting.required:
                    val = (saved or {}).get(setting.key, "")
                    if not val:
                        needs_config = True
                        break

        if needs_config and self._game.server_settings:
            self._on_configure()
            saved = config_manager.load(self._game.id)
            if saved is None:
                return

        ok = server_manager.start(self._game, saved or {})
        if ok:
            self._badge.set_state("installing")
            QTimer.singleShot(3000, self._refresh_status_fast)
        else:
            QMessageBox.critical(self, "Launch Failed", f"Could not start {self._game.name}.")

    def _on_stop(self):
        if not self._game:
            return
        reply = QMessageBox.question(
            self, "Stop Server",
            f"Stop the {self._game.name} server?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            config = config_manager.load(self._game.id) or {}
            server_manager.stop(self._game, config)
            QTimer.singleShot(2000, self._refresh_status_fast)

    def _on_close_ports(self):
        if not self._game:
            return
        config = config_manager.load(self._game.id) or {}
        server_manager.close_ports(self._game, config)
        QMessageBox.information(
            self, "Ports Closed",
            f"Firewall rules and UPnP mappings for {self._game.name} have been removed.",
        )

    def _on_configure(self):
        if not self._game:
            return
        saved = config_manager.load(self._game.id) or self._game.get_default_config()
        dlg = ConfigDialog(self._game, saved, parent=self)
        if dlg.exec_() == ConfigDialog.Accepted:
            new_config = dlg.get_config()
            config_manager.save(self._game.id, new_config)

    def _on_uninstall(self):
        if not self._game:
            return
        reply = QMessageBox.warning(
            self,
            "Uninstall Server",
            f"Uninstall the {self._game.name} dedicated server?\n\n"
            "This will delete all server files and world data.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        dlg = ProgressDialog(f"Uninstalling {self._game.name}", parent=self)
        worker = UninstallWorker(self._game)
        worker.status.connect(dlg.update_status)
        worker.finished.connect(dlg.on_finished)
        worker.finished.connect(self._on_uninstall_finished)
        worker.start()
        dlg.exec_()

    def _on_uninstall_finished(self, success: bool):
        if success:
            self._update_buttons(installed=False, running=False)
            self._badge.set_state("stopped")
