"""
DSTModsWidget — Steam Workshop mod manager for Don't Starve Together.

Layout (single scrollable page):
  1. Add Mod      — paste a Workshop URL or numeric ID
  2. Browse       — search Steam Workshop, see results, click to install
  3. Installed    — list of added mods with enable/disable, configure, remove
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt, QThread, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QFormLayout,
)

from ui import theme

if TYPE_CHECKING:
    from core.game_model import GameModel


# ── Background threads ─────────────────────────────────────────────────────────

class _DetailsThread(QThread):
    """Fetch Steam Workshop metadata for a list of IDs."""
    done = pyqtSignal(list)

    def __init__(self, workshop_ids: list[str]):
        super().__init__()
        self._ids = workshop_ids

    def run(self):
        from server import dst_mod_manager
        self.done.emit(dst_mod_manager.get_workshop_details(self._ids))


class _SearchThread(QThread):
    """Search Steam Workshop for DST mods."""
    done = pyqtSignal(list)

    def __init__(self, query: str, page: int = 1):
        super().__init__()
        self._query = query
        self._page = page

    def run(self):
        from server import dst_mod_manager
        self.done.emit(dst_mod_manager.search_workshop(self._query, page=self._page))


# ── Per-mod configuration dialog ───────────────────────────────────────────────

class _ModConfigDialog(QDialog):
    """
    Dialog for configuring a single DST mod's options.

    Options are discovered by parsing the mod's modinfo.lua, which is only
    available once the DST server has downloaded the mod on first run.
    """

    def __init__(
        self,
        mod_name: str,
        config_options: list[dict],
        current_config: dict,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(f"Configure: {mod_name}")
        self.setMinimumWidth(460)
        self.setStyleSheet(
            theme.DIALOG + theme.INPUT + theme.CHECKBOX
            + theme.BTN_PRIMARY + theme.BTN_SECONDARY
        )

        self._options = config_options
        self._widgets: dict = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        content = QWidget()
        content.setStyleSheet(f"background: {theme.Colors.BG_SURFACE};")

        if config_options:
            form = QFormLayout(content)
            form.setContentsMargins(24, 20, 24, 20)
            form.setSpacing(12)
            form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

            for opt in config_options:
                key = opt["name"]
                val = current_config.get(key, opt.get("default"))
                w = self._make_option_widget(opt, val)
                self._widgets[key] = (w, opt)

                lbl = QLabel(opt["label"])
                lbl.setStyleSheet(
                    f"color: {theme.Colors.TEXT_PRIMARY}; "
                    f"font-size: {theme.Fonts.SIZE_SM}px; "
                    f"font-family: {theme.Fonts.FAMILY}; "
                    "background: transparent;"
                )
                if opt.get("hover"):
                    lbl.setToolTip(opt["hover"])
                    w.setToolTip(opt["hover"])
                form.addRow(lbl, w)
        else:
            note = QLabel(
                "This mod has no configurable options, or the mod files haven't been\n"
                "downloaded yet. Run the server once so DST downloads the mod, then\n"
                "re-open Configure to see options."
            )
            note.setAlignment(Qt.AlignCenter)
            note.setWordWrap(True)
            note.setStyleSheet(
                f"color: {theme.Colors.TEXT_SECONDARY}; "
                f"font-size: {theme.Fonts.SIZE_SM}px; "
                f"font-family: {theme.Fonts.FAMILY}; "
                "background: transparent; padding: 32px;"
            )
            vl = QVBoxLayout(content)
            vl.addWidget(note)

        scroll.setWidget(content)
        outer.addWidget(scroll)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {theme.Colors.DIVIDER};")
        outer.addWidget(sep)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(24, 12, 24, 12)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(theme.BTN_SECONDARY)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(theme.BTN_PRIMARY)
        save_btn.clicked.connect(self.accept)
        save_btn.setDefault(True)
        save_btn.setEnabled(bool(config_options))

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        btn_container = QWidget()
        btn_container.setStyleSheet(f"background: {theme.Colors.BG_SURFACE};")
        btn_container.setLayout(btn_row)
        outer.addWidget(btn_container)

    def _make_option_widget(self, opt: dict, value) -> QWidget:
        opt_type = opt.get("type", "string")
        choices = opt.get("options", [])

        if opt_type == "choice" and choices:
            w = QComboBox()
            for c in choices:
                w.addItem(c["description"], userData=c["data"])
            for i in range(w.count()):
                if w.itemData(i) == value:
                    w.setCurrentIndex(i)
                    break
            w.setStyleSheet(theme.INPUT)
            return w

        if opt_type == "bool":
            w = QCheckBox()
            w.setChecked(bool(value) if value is not None else bool(opt.get("default")))
            w.setStyleSheet(theme.CHECKBOX)
            return w

        if opt_type == "number":
            default = opt.get("default", 0)
            if isinstance(default, float) or isinstance(value, float):
                w = QDoubleSpinBox()
                w.setDecimals(3)
                w.setRange(-1e9, 1e9)
                w.setValue(float(value) if value is not None else float(default))
            else:
                w = QSpinBox()
                w.setRange(-2147483648, 2147483647)
                w.setValue(int(value) if value is not None else int(default))
            w.setStyleSheet(theme.INPUT)
            return w

        w = QLineEdit()
        w.setText(str(value) if value is not None else str(opt.get("default", "")))
        w.setStyleSheet(theme.INPUT)
        return w

    def get_config(self) -> dict:
        """Return {option_name: data_value} after the dialog is accepted."""
        result: dict = {}
        for key, (w, opt) in self._widgets.items():
            opt_type = opt.get("type", "string")
            choices = opt.get("options", [])
            if opt_type == "choice" and choices and isinstance(w, QComboBox):
                result[key] = w.currentData()
            elif opt_type == "bool" and isinstance(w, QCheckBox):
                result[key] = w.isChecked()
            elif opt_type == "number":
                result[key] = w.value()
            else:
                result[key] = w.text()
        return result


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _card() -> QFrame:
    f = QFrame()
    f.setStyleSheet(
        f"QFrame {{ background: {theme.Colors.BG_SURFACE}; "
        f"border-radius: {theme.Layout.RADIUS_MD}px; border: none; }}"
    )
    return f


def _lbl(text: str, color=None, bold=False, size=None) -> QLabel:
    lbl = QLabel(text)
    c = color or theme.Colors.TEXT_PRIMARY
    s = size or theme.Fonts.SIZE_SM
    w = "700" if bold else "400"
    lbl.setStyleSheet(
        f"color: {c}; font-size: {s}px; font-weight: {w}; "
        f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
    )
    return lbl


# ── Main widget ────────────────────────────────────────────────────────────────

class DSTModsWidget(QWidget):
    """
    Steam Workshop mod manager for Don't Starve Together.
    Lets users add, browse, configure, enable/disable, and remove mods.
    """

    def __init__(self, game: "GameModel", parent=None):
        super().__init__(parent)
        self._game = game
        self._details: dict[str, dict] = {}        # workshop_id → Steam API data
        self._config_opts: dict[str, list] = {}    # workshop_id → parsed modinfo options
        self._last_search: list[dict] = []

        self._details_thread: _DetailsThread | None = None
        self._search_thread: _SearchThread | None = None

        self.setStyleSheet(f"background: {theme.Colors.BG_BASE};")

        outer_scroll = QScrollArea(self)
        outer_scroll.setWidgetResizable(True)
        outer_scroll.setFrameShape(QFrame.NoFrame)
        outer_scroll.setStyleSheet("background: transparent; border: none;")

        inner = QWidget()
        inner.setStyleSheet(f"background: {theme.Colors.BG_BASE};")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(
            theme.Layout.MARGIN_LG, theme.Layout.MARGIN_LG,
            theme.Layout.MARGIN_LG, theme.Layout.MARGIN_LG,
        )
        layout.setSpacing(theme.Layout.SPACING_LG)

        layout.addWidget(self._build_add_section())
        layout.addWidget(self._build_search_section())
        layout.addWidget(self._build_installed_section())
        layout.addStretch()

        outer_scroll.setWidget(inner)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(outer_scroll)

        self._refresh_installed()
        self._prefetch_details()

    # ── Add section ────────────────────────────────────────────────────────────

    def _build_add_section(self) -> QWidget:
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
        )
        layout.setSpacing(theme.Layout.SPACING_SM)

        layout.addWidget(_lbl("Add Mod by Workshop URL or ID", bold=True))

        row = QHBoxLayout()
        self._add_input = QLineEdit()
        self._add_input.setPlaceholderText(
            "Steam Workshop URL  or  numeric ID  (e.g. 375859599)"
        )
        self._add_input.setStyleSheet(theme.INPUT)
        self._add_input.returnPressed.connect(self._on_add)
        row.addWidget(self._add_input)

        add_btn = QPushButton("Add Mod")
        add_btn.setStyleSheet(theme.BTN_PRIMARY)
        add_btn.setFixedWidth(100)
        add_btn.clicked.connect(self._on_add)
        row.addWidget(add_btn)
        layout.addLayout(row)

        self._add_status = _lbl("", color=theme.Colors.TEXT_SECONDARY, size=theme.Fonts.SIZE_XS)
        layout.addWidget(self._add_status)

        return card

    def _on_add(self):
        from server import dst_mod_manager
        raw = self._add_input.text().strip()
        if not raw:
            return

        wid = dst_mod_manager.extract_workshop_id(raw)
        if not wid:
            self._set_add_status("Invalid URL or ID — enter a numeric ID or a Steam Workshop URL.", error=True)
            return

        added = dst_mod_manager.add_mod(self._game, wid)
        if not added:
            self._set_add_status(f"workshop-{wid} is already in your mod list.", warning=True)
            return

        self._add_input.clear()
        self._set_add_status(f"Added workshop-{wid}. Fetching mod details…")
        self._refresh_installed()

        # Fetch Steam details for the new mod
        t = _DetailsThread([wid])
        t.done.connect(self._on_details_received)
        t.start()
        # Keep reference so it isn't GC'd
        self._pending_threads = getattr(self, "_pending_threads", [])
        self._pending_threads.append(t)

    def _set_add_status(self, msg: str, error=False, warning=False):
        color = (
            theme.Colors.ERROR if error
            else theme.Colors.WARNING if warning
            else theme.Colors.TEXT_SECONDARY
        )
        self._add_status.setStyleSheet(
            f"color: {color}; font-size: {theme.Fonts.SIZE_XS}px; "
            f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
        )
        self._add_status.setText(msg)

    # ── Search section ─────────────────────────────────────────────────────────

    def _build_search_section(self) -> QWidget:
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
        )
        layout.setSpacing(theme.Layout.SPACING_SM)

        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("Browse Steam Workshop", bold=True))
        hdr.addStretch()
        browse_btn = QPushButton("Open in Browser ↗")
        browse_btn.setStyleSheet(theme.BTN_SECONDARY)
        browse_btn.setFixedHeight(28)
        browse_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://steamcommunity.com/app/322330/workshop/"))
        )
        hdr.addWidget(browse_btn)
        layout.addLayout(hdr)

        search_row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search Don't Starve Together mods…")
        self._search_input.setStyleSheet(theme.INPUT)
        self._search_input.returnPressed.connect(self._on_search)
        search_row.addWidget(self._search_input)

        search_btn = QPushButton("Search")
        search_btn.setStyleSheet(theme.BTN_PRIMARY)
        search_btn.setFixedWidth(80)
        search_btn.clicked.connect(self._on_search)
        search_row.addWidget(search_btn)
        layout.addLayout(search_row)

        self._search_status = _lbl("", color=theme.Colors.TEXT_SECONDARY, size=theme.Fonts.SIZE_XS)
        layout.addWidget(self._search_status)

        self._results_container = QWidget()
        self._results_container.setStyleSheet("background: transparent;")
        self._results_layout = QVBoxLayout(self._results_container)
        self._results_layout.setContentsMargins(0, 4, 0, 0)
        self._results_layout.setSpacing(6)
        self._results_container.setVisible(False)
        layout.addWidget(self._results_container)

        return card

    def _on_search(self):
        query = self._search_input.text().strip()
        if not query:
            return
        self._search_status.setText("Searching…")
        self._results_container.setVisible(False)

        if self._search_thread and self._search_thread.isRunning():
            self._search_thread.quit()
        self._search_thread = _SearchThread(query)
        self._search_thread.done.connect(self._on_search_done)
        self._search_thread.start()

    def _on_search_done(self, results: list[dict]):
        self._last_search = results
        if not results:
            self._search_status.setText(
                "No results. Try different keywords or use 'Open in Browser ↗'."
            )
            self._results_container.setVisible(False)
            return

        self._search_status.setText(f"{len(results)} result(s)")
        self._rebuild_search_results()

    def _rebuild_search_results(self):
        while self._results_layout.count():
            item = self._results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        installed = set(self._get_installed_ids())
        for mod in self._last_search:
            self._results_layout.addWidget(
                self._make_search_row(mod, mod["workshop_id"] in installed)
            )
        self._results_container.setVisible(bool(self._last_search))

    def _make_search_row(self, mod: dict, already_installed: bool) -> QWidget:
        row = QFrame()
        row.setStyleSheet(
            f"QFrame {{ background: {theme.Colors.BG_ELEVATED}; "
            f"border-radius: {theme.Layout.RADIUS_SM}px; border: none; }}"
        )
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        title = mod.get("title") or f"workshop-{mod['workshop_id']}"
        text_col.addWidget(_lbl(title, bold=True))

        desc = (mod.get("description") or "").strip().replace("\n", " ")
        if desc:
            if len(desc) > 120:
                desc = desc[:120] + "…"
            text_col.addWidget(_lbl(desc, color=theme.Colors.TEXT_SECONDARY, size=theme.Fonts.SIZE_XS))

        subs = mod.get("subscriptions", 0)
        if subs:
            text_col.addWidget(
                _lbl(f"{subs:,} subscribers", color=theme.Colors.TEXT_DISABLED, size=theme.Fonts.SIZE_XS)
            )

        layout.addLayout(text_col, stretch=1)

        if already_installed:
            layout.addWidget(_lbl("Added ✓", color=theme.Colors.SUCCESS))
        else:
            btn = QPushButton("+ Add")
            btn.setStyleSheet(theme.BTN_PRIMARY)
            btn.setFixedWidth(70)
            btn.clicked.connect(lambda _, m=dict(mod): self._on_add_from_search(m))
            layout.addWidget(btn)

        return row

    def _on_add_from_search(self, mod: dict):
        from server import dst_mod_manager
        wid = mod["workshop_id"]
        if dst_mod_manager.add_mod(self._game, wid):
            self._details[wid] = mod
            self._refresh_installed()
            self._rebuild_search_results()

    # ── Installed mods section ─────────────────────────────────────────────────

    def _build_installed_section(self) -> QWidget:
        self._installed_card = _card()
        self._installed_card_layout = QVBoxLayout(self._installed_card)
        self._installed_card_layout.setContentsMargins(
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
        )
        self._installed_card_layout.setSpacing(theme.Layout.SPACING_SM)

        self._installed_header = _lbl("Installed Mods", bold=True)
        self._installed_card_layout.addWidget(self._installed_header)

        self._installed_list = QVBoxLayout()
        self._installed_list.setSpacing(4)
        self._installed_card_layout.addLayout(self._installed_list)

        return self._installed_card

    def _get_installed_ids(self) -> list[str]:
        from server import dst_mod_manager
        return dst_mod_manager.load_installed_workshop_ids(self._game)

    def _refresh_installed(self):
        from server import dst_mod_manager

        while self._installed_list.count():
            item = self._installed_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        ids = dst_mod_manager.load_installed_workshop_ids(self._game)
        overrides = dst_mod_manager.load_mod_overrides(self._game)

        self._installed_header.setText(
            f"Installed Mods ({len(ids)})" if ids else "Installed Mods"
        )

        if not ids:
            self._installed_list.addWidget(
                _lbl("No mods installed — add mods using the sections above.",
                     color=theme.Colors.TEXT_DISABLED)
            )
            return

        for wid in ids:
            entry = overrides.get(wid, {"enabled": True, "config": {}})
            name = self._details.get(wid, {}).get("title") or f"workshop-{wid}"
            opts = self._config_opts.get(wid, [])
            self._installed_list.addWidget(self._make_installed_row(wid, name, entry, opts))

    def _make_installed_row(self, wid: str, name: str, entry: dict, opts: list) -> QWidget:
        row = QFrame()
        row.setStyleSheet(
            f"QFrame {{ background: {theme.Colors.BG_ELEVATED}; "
            f"border-radius: {theme.Layout.RADIUS_SM}px; border: none; }}"
        )
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        cb = QCheckBox()
        cb.setChecked(entry.get("enabled", True))
        cb.setStyleSheet(theme.CHECKBOX)
        cb.toggled.connect(lambda checked, w=wid: self._on_toggle(w, checked))
        layout.addWidget(cb)

        text_col = QVBoxLayout()
        text_col.setSpacing(0)
        text_col.addWidget(_lbl(name))
        text_col.addWidget(_lbl(f"workshop-{wid}", color=theme.Colors.TEXT_DISABLED, size=theme.Fonts.SIZE_XS))
        layout.addLayout(text_col, stretch=1)

        cfg_btn = QPushButton("Configure")
        cfg_btn.setStyleSheet(theme.BTN_SECONDARY)
        cfg_btn.setFixedWidth(90)
        if not opts:
            cfg_btn.setToolTip("Run the server once to download the mod, then re-open to configure.")
        cfg_btn.clicked.connect(lambda _, w=wid: self._on_configure(w))
        layout.addWidget(cfg_btn)

        rm_btn = QPushButton("Remove")
        rm_btn.setStyleSheet(theme.BTN_DANGER)
        rm_btn.setFixedWidth(72)
        rm_btn.clicked.connect(lambda _, w=wid, n=name: self._on_remove(w, n))
        layout.addWidget(rm_btn)

        return row

    def _on_toggle(self, wid: str, enabled: bool):
        from server import dst_mod_manager
        dst_mod_manager.toggle_mod(self._game, wid, enabled)

    def _on_configure(self, wid: str):
        from server import dst_mod_manager

        if wid not in self._config_opts:
            self._config_opts[wid] = dst_mod_manager.parse_mod_config_options(self._game, wid)
        opts = self._config_opts[wid]

        overrides = dst_mod_manager.load_mod_overrides(self._game)
        current_cfg = overrides.get(wid, {}).get("config", {})
        name = self._details.get(wid, {}).get("title") or f"workshop-{wid}"

        dlg = _ModConfigDialog(name, opts, current_cfg, parent=self.window())
        if dlg.exec_() == QDialog.Accepted:
            dst_mod_manager.set_mod_config(self._game, wid, dlg.get_config())

    def _on_remove(self, wid: str, name: str):
        reply = QMessageBox.question(
            self.window(),
            "Remove Mod",
            f"Remove \"{name}\" from the server?\n\n"
            "This removes it from the mod list and config files.\n"
            "Downloaded mod files (if any) are left on disk.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            from server import dst_mod_manager
            dst_mod_manager.remove_mod(self._game, wid)
            self._details.pop(wid, None)
            self._config_opts.pop(wid, None)
            self._refresh_installed()
            self._rebuild_search_results()

    # ── Detail prefetching ─────────────────────────────────────────────────────

    def _prefetch_details(self):
        """On load: fetch Steam metadata and parse modinfo.lua for installed mods."""
        ids = self._get_installed_ids()
        unfetched = [i for i in ids if i not in self._details]

        # Parse modinfo.lua synchronously (fast, local disk read)
        for wid in ids:
            if wid not in self._config_opts:
                from server import dst_mod_manager
                opts = dst_mod_manager.parse_mod_config_options(self._game, wid)
                if opts:
                    self._config_opts[wid] = opts

        if unfetched:
            if self._details_thread and self._details_thread.isRunning():
                self._details_thread.quit()
            self._details_thread = _DetailsThread(unfetched)
            self._details_thread.done.connect(self._on_details_received)
            self._details_thread.start()

    def _on_details_received(self, details: list[dict]):
        for d in details:
            wid = d.get("workshop_id", "")
            if wid:
                self._details[wid] = d
        self._refresh_installed()
        self._set_add_status("")
