"""
DSTModsWidget — Steam Workshop mod manager for Don't Starve Together.

Browse section features:
  - Shows popular mods on open (no query needed)
  - Real-time debounced search: results update 600 ms after typing stops
  - Visual mod cards with asynchronously-loaded preview images
  - "Load More" pagination button
  - Clicking a mod title opens its Steam Workshop page

Layout:
  1. Add Mod      — paste a Workshop URL or numeric ID
  2. Browse       — search bar + live results with image cards
  3. Installed    — list of added mods with enable/disable, configure, remove
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt, QThread, QTimer, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QPixmap
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QFormLayout,
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
)

from ui import theme

if TYPE_CHECKING:
    from core.game_model import GameModel

_CARD_IMG_PX = 80          # preview image thumbnail size
_SEARCH_DEBOUNCE_MS = 600  # ms to wait after last keystroke before querying
_PAGE_SIZE = 20

# Module-level pixmap cache so images survive widget re-creation
_IMAGE_CACHE: dict[str, QPixmap] = {}


# ── Background threads ─────────────────────────────────────────────────────────

class _SearchThread(QThread):
    done = pyqtSignal(list)

    def __init__(self, query: str, page: int = 1):
        super().__init__()
        self._query = query
        self._page = page

    def run(self):
        from server import dst_mod_manager
        self.done.emit(dst_mod_manager.search_workshop(self._query, page=self._page))


class _DetailsThread(QThread):
    done = pyqtSignal(list)

    def __init__(self, workshop_ids: list[str]):
        super().__init__()
        self._ids = workshop_ids

    def run(self):
        from server import dst_mod_manager
        self.done.emit(dst_mod_manager.get_workshop_details(self._ids))


class _ImageLoaderThread(QThread):
    """Download preview images for a list of mods; emits (workshop_id, raw_bytes)."""
    image_ready = pyqtSignal(str, bytes)

    def __init__(self, items: list[tuple[str, str]]):
        # items: [(workshop_id, preview_url), ...]
        super().__init__()
        self._items = items
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        import urllib.request
        for wid, url in self._items:
            if self._cancelled or not url:
                continue
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "DedicatedServerAutomation/1.0"},
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = resp.read()
                self.image_ready.emit(wid, data)
            except Exception:
                pass


# ── Mod card widget ────────────────────────────────────────────────────────────

class _ModCard(QFrame):
    """
    Visual card for one Steam Workshop search result.

    Shows a preview image on the left, title / author / subscriber count in
    the middle, and an Add or "Added ✓" indicator on the right.
    Clicking the title opens the mod's Workshop page in the browser.
    """
    add_clicked = pyqtSignal(str)   # emits workshop_id

    _PLACEHOLDER_STYLE = (
        f"background: {theme.Colors.BG_ELEVATED}; "
        f"border-radius: {theme.Layout.RADIUS_SM}px; border: none;"
    )

    def __init__(self, mod: dict, installed: bool, parent=None):
        super().__init__(parent)
        self._wid = mod["workshop_id"]
        self._installed = installed

        self.setStyleSheet(
            f"QFrame {{ background: {theme.Colors.BG_SURFACE}; "
            f"border-radius: {theme.Layout.RADIUS_MD}px; border: none; }}"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        # ── Preview image ──────────────────────────────────────────────────────
        self._img_lbl = QLabel()
        self._img_lbl.setFixedSize(_CARD_IMG_PX, _CARD_IMG_PX)
        self._img_lbl.setStyleSheet(self._PLACEHOLDER_STYLE)
        self._img_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._img_lbl)

        # ── Text column ────────────────────────────────────────────────────────
        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        title = mod.get("title") or f"workshop-{self._wid}"
        workshop_url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={self._wid}"
        title_lbl = QLabel(
            f'<a href="{workshop_url}" style="color:{theme.Colors.TEXT_PRIMARY}; '
            f'text-decoration:none; font-weight:700;">{title}</a>'
        )
        title_lbl.setTextFormat(Qt.RichText)
        title_lbl.setOpenExternalLinks(True)
        title_lbl.setWordWrap(False)
        title_lbl.setStyleSheet(
            f"font-size: {theme.Fonts.SIZE_SM}px; "
            f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
        )
        text_col.addWidget(title_lbl)

        meta_parts = []
        if mod.get("author"):
            meta_parts.append(f"by {mod['author']}")
        subs = mod.get("subscriptions", 0)
        if subs:
            meta_parts.append(f"{subs:,} subscribers")
        if meta_parts:
            meta_lbl = QLabel("  ·  ".join(meta_parts))
            meta_lbl.setStyleSheet(
                f"color: {theme.Colors.TEXT_DISABLED}; "
                f"font-size: {theme.Fonts.SIZE_XS}px; "
                f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
            )
            text_col.addWidget(meta_lbl)

        desc = (mod.get("description") or "").strip().replace("\n", " ")
        if desc:
            if len(desc) > 140:
                desc = desc[:140] + "…"
            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(
                f"color: {theme.Colors.TEXT_SECONDARY}; "
                f"font-size: {theme.Fonts.SIZE_XS}px; "
                f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
            )
            text_col.addWidget(desc_lbl)

        layout.addLayout(text_col, stretch=1)

        # ── Action area ────────────────────────────────────────────────────────
        action_col = QVBoxLayout()
        action_col.setSpacing(4)
        action_col.setAlignment(Qt.AlignCenter)

        self._add_btn = QPushButton("+ Add")
        self._add_btn.setStyleSheet(theme.BTN_PRIMARY)
        self._add_btn.setFixedWidth(72)
        self._add_btn.setVisible(not installed)
        self._add_btn.clicked.connect(lambda: self.add_clicked.emit(self._wid))
        action_col.addWidget(self._add_btn)

        self._added_lbl = QLabel("Added ✓")
        self._added_lbl.setStyleSheet(
            f"color: {theme.Colors.SUCCESS}; "
            f"font-size: {theme.Fonts.SIZE_SM}px; "
            f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
        )
        self._added_lbl.setAlignment(Qt.AlignCenter)
        self._added_lbl.setVisible(installed)
        action_col.addWidget(self._added_lbl)

        layout.addLayout(action_col)

        # Apply cached image if available
        if self._wid in _IMAGE_CACHE:
            self._apply_pixmap(_IMAGE_CACHE[self._wid])

    def set_image(self, pixmap: QPixmap) -> None:
        _IMAGE_CACHE[self._wid] = pixmap
        self._apply_pixmap(pixmap)

    def _apply_pixmap(self, pixmap: QPixmap) -> None:
        scaled = pixmap.scaled(
            _CARD_IMG_PX, _CARD_IMG_PX,
            Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation,
        )
        # Crop to exact square
        x = (scaled.width() - _CARD_IMG_PX) // 2
        y = (scaled.height() - _CARD_IMG_PX) // 2
        cropped = scaled.copy(x, y, _CARD_IMG_PX, _CARD_IMG_PX)
        self._img_lbl.setPixmap(cropped)
        self._img_lbl.setStyleSheet(
            f"border-radius: {theme.Layout.RADIUS_SM}px; border: none;"
        )

    def mark_installed(self) -> None:
        self._installed = True
        self._add_btn.setVisible(False)
        self._added_lbl.setVisible(True)


# ── Per-mod configuration dialog ───────────────────────────────────────────────

class _ModConfigDialog(QDialog):
    """
    Dialog for configuring a single DST mod's options.
    Options are discovered by parsing modinfo.lua, which is present only after
    the DST server has downloaded the mod on its first run.
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
                w = self._make_widget(opt, val)
                self._widgets[key] = (w, opt)
                lbl = QLabel(opt["label"])
                lbl.setStyleSheet(
                    f"color: {theme.Colors.TEXT_PRIMARY}; "
                    f"font-size: {theme.Fonts.SIZE_SM}px; "
                    f"font-family: {theme.Fonts.FAMILY}; background: transparent;"
                )
                if opt.get("hover"):
                    lbl.setToolTip(opt["hover"])
                    w.setToolTip(opt["hover"])
                form.addRow(lbl, w)
        else:
            note = QLabel(
                "This mod has no configurable options, or its files haven't been\n"
                "downloaded yet. Start the server once so DST downloads the mod,\n"
                "then re-open Configure to see its options."
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

    def _make_widget(self, opt: dict, value) -> QWidget:
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

    Opens showing the most-subscribed (popular) mods. As the user types,
    results update in real time after a short debounce. Each result is a
    visual card with a preview image loaded asynchronously.
    """

    def __init__(self, game: "GameModel", parent=None):
        super().__init__(parent)
        self._game = game
        self._details: dict[str, dict] = {}        # workshop_id → API data
        self._config_opts: dict[str, list] = {}    # workshop_id → modinfo options

        # Browse state
        self._current_query = ""
        self._search_page = 1
        self._search_results: list[dict] = []      # all accumulated results
        self._has_more = False
        self._search_cards: dict[str, _ModCard] = {}

        # Threads
        self._search_thread: _SearchThread | None = None
        self._details_thread: _DetailsThread | None = None
        self._img_thread: _ImageLoaderThread | None = None

        # Debounce timer
        self._debounce = QTimer()
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._do_search)

        self.setStyleSheet(f"background: {theme.Colors.BG_BASE};")

        outer_scroll = QScrollArea(self)
        outer_scroll.setWidgetResizable(True)
        outer_scroll.setFrameShape(QFrame.NoFrame)
        outer_scroll.setStyleSheet("background: transparent; border: none;")

        inner = QWidget()
        inner.setStyleSheet(f"background: {theme.Colors.BG_BASE};")
        self._page_layout = QVBoxLayout(inner)
        self._page_layout.setContentsMargins(
            theme.Layout.MARGIN_LG, theme.Layout.MARGIN_LG,
            theme.Layout.MARGIN_LG, theme.Layout.MARGIN_LG,
        )
        self._page_layout.setSpacing(theme.Layout.SPACING_LG)

        self._page_layout.addWidget(self._build_add_section())
        self._page_layout.addWidget(self._build_browse_section())
        self._page_layout.addWidget(self._build_installed_section())
        self._page_layout.addStretch()

        outer_scroll.setWidget(inner)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(outer_scroll)

        self._refresh_installed()
        self._prefetch_details()

        # Load popular mods immediately on open
        self._do_search()

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
            self._set_add_status("Invalid URL or ID — enter a numeric ID or Steam Workshop URL.", error=True)
            return

        added = dst_mod_manager.add_mod(self._game, wid)
        if not added:
            self._set_add_status(f"workshop-{wid} is already in your mod list.", warning=True)
            return

        self._add_input.clear()
        self._set_add_status(f"Added workshop-{wid}. Fetching details…")
        self._refresh_installed()

        # Mark the card as installed if it's visible in search results
        card = self._search_cards.get(wid)
        if card:
            card.mark_installed()

        t = _DetailsThread([wid])
        t.done.connect(self._on_details_received)
        t.start()
        self._stash_thread(t)

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

    # ── Browse section ─────────────────────────────────────────────────────────

    def _build_browse_section(self) -> QWidget:
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
        )
        layout.setSpacing(theme.Layout.SPACING_SM)

        # Header row
        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("Browse Workshop", bold=True))
        hdr.addStretch()
        browse_btn = QPushButton("Open in Browser ↗")
        browse_btn.setStyleSheet(theme.BTN_SECONDARY)
        browse_btn.setFixedHeight(28)
        browse_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://steamcommunity.com/app/322330/workshop/"))
        )
        hdr.addWidget(browse_btn)
        layout.addLayout(hdr)

        # Search bar (typing triggers debounced search)
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search Don't Starve Together mods — or leave blank to browse popular")
        self._search_input.setStyleSheet(theme.INPUT)
        self._search_input.textChanged.connect(
            lambda _: self._debounce.start(_SEARCH_DEBOUNCE_MS)
        )
        self._search_input.returnPressed.connect(
            lambda: (self._debounce.stop(), self._do_search())
        )
        layout.addWidget(self._search_input)

        # Status line (e.g. "Showing popular mods", "Searching…", "12 results")
        self._browse_status = _lbl("", color=theme.Colors.TEXT_SECONDARY, size=theme.Fonts.SIZE_XS)
        layout.addWidget(self._browse_status)

        # Results list
        self._results_widget = QWidget()
        self._results_widget.setStyleSheet("background: transparent;")
        self._results_layout = QVBoxLayout(self._results_widget)
        self._results_layout.setContentsMargins(0, 0, 0, 0)
        self._results_layout.setSpacing(6)
        layout.addWidget(self._results_widget)

        # Load More button (hidden until needed)
        self._load_more_btn = QPushButton("Load More")
        self._load_more_btn.setStyleSheet(theme.BTN_SECONDARY)
        self._load_more_btn.setVisible(False)
        self._load_more_btn.clicked.connect(self._on_load_more)
        layout.addWidget(self._load_more_btn)

        return card

    def _do_search(self):
        """Kick off a fresh search (page 1) for the current query."""
        query = self._search_input.text().strip() if hasattr(self, "_search_input") else ""
        self._current_query = query
        self._search_page = 1
        self._search_results = []
        self._search_cards = {}

        label = "Searching…" if query else "Loading popular mods…"
        self._browse_status.setText(label)
        self._load_more_btn.setVisible(False)
        self._clear_results()

        self._run_search(query, page=1)

    def _on_load_more(self):
        self._search_page += 1
        self._load_more_btn.setEnabled(False)
        self._run_search(self._current_query, page=self._search_page)

    def _run_search(self, query: str, page: int):
        if self._search_thread and self._search_thread.isRunning():
            self._search_thread.quit()
        self._search_thread = _SearchThread(query, page=page)
        self._search_thread.done.connect(self._on_search_done)
        self._search_thread.start()

    def _on_search_done(self, results: list[dict]):
        self._search_results.extend(results)
        self._has_more = len(results) >= _PAGE_SIZE

        if not self._search_results:
            self._browse_status.setText(
                "No results. Try different keywords or click 'Open in Browser ↗'."
            )
            self._load_more_btn.setVisible(False)
            return

        query = self._current_query
        total = len(self._search_results)
        if query:
            self._browse_status.setText(f"{total} result(s) for \"{query}\"")
        else:
            self._browse_status.setText(f"Popular mods — {total} shown")

        # Render only the newly-arrived results (append, don't rebuild everything)
        new_results = results
        installed = set(self._get_installed_ids())
        new_to_load: list[tuple[str, str]] = []

        for mod in new_results:
            wid = mod["workshop_id"]
            if not wid:
                continue
            card = _ModCard(mod, wid in installed)
            card.add_clicked.connect(self._on_add_from_card)
            self._results_layout.addWidget(card)
            self._search_cards[wid] = card
            if wid not in _IMAGE_CACHE and mod.get("preview_url"):
                new_to_load.append((wid, mod["preview_url"]))

        self._load_more_btn.setVisible(self._has_more)
        self._load_more_btn.setEnabled(True)

        # Load preview images in background
        if new_to_load:
            self._start_image_load(new_to_load)

    def _clear_results(self):
        while self._results_layout.count():
            item = self._results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_add_from_card(self, wid: str):
        from server import dst_mod_manager
        mod_info = next(
            (m for m in self._search_results if m["workshop_id"] == wid), {}
        )
        if dst_mod_manager.add_mod(self._game, wid):
            if mod_info:
                self._details[wid] = mod_info
            card = self._search_cards.get(wid)
            if card:
                card.mark_installed()
            self._refresh_installed()
            self._set_add_status("")

    # ── Image loading ──────────────────────────────────────────────────────────

    def _start_image_load(self, items: list[tuple[str, str]]):
        """Start (or restart) the image loader thread for the given (wid, url) pairs."""
        if self._img_thread and self._img_thread.isRunning():
            self._img_thread.cancel()
            self._img_thread.quit()

        self._img_thread = _ImageLoaderThread(items)
        self._img_thread.image_ready.connect(self._on_image_ready)
        self._img_thread.start()

    def _on_image_ready(self, wid: str, data: bytes):
        """Called in the main thread; converts raw bytes to QPixmap and updates cards."""
        pix = QPixmap()
        if not pix.loadFromData(data):
            return
        _IMAGE_CACHE[wid] = pix
        card = self._search_cards.get(wid)
        if card:
            card.set_image(pix)

    # ── Installed mods section ─────────────────────────────────────────────────

    def _build_installed_section(self) -> QWidget:
        self._installed_card = _card()
        self._installed_layout = QVBoxLayout(self._installed_card)
        self._installed_layout.setContentsMargins(
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
            theme.Layout.MARGIN_MD, theme.Layout.MARGIN_MD,
        )
        self._installed_layout.setSpacing(theme.Layout.SPACING_SM)

        self._installed_header = _lbl("Installed Mods", bold=True)
        self._installed_layout.addWidget(self._installed_header)

        self._installed_list = QVBoxLayout()
        self._installed_list.setSpacing(4)
        self._installed_layout.addLayout(self._installed_list)

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
                _lbl("No mods installed — browse the Workshop above and click + Add.",
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

        # Preview thumbnail from cache
        img_lbl = QLabel()
        img_lbl.setFixedSize(40, 40)
        img_lbl.setStyleSheet(
            f"background: {theme.Colors.BG_SURFACE}; "
            f"border-radius: {theme.Layout.RADIUS_SM}px; border: none;"
        )
        if wid in _IMAGE_CACHE:
            pix = _IMAGE_CACHE[wid].scaled(40, 40, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            img_lbl.setPixmap(pix)
            img_lbl.setStyleSheet(f"border-radius: {theme.Layout.RADIUS_SM}px; border: none;")
        layout.addWidget(img_lbl)

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
            cfg_btn.setToolTip("Start the server once to download the mod, then re-open to see config options.")
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
            # Mark any visible card as not installed
            card = self._search_cards.get(wid)
            if card:
                card._add_btn.setVisible(True)
                card._added_lbl.setVisible(False)
            self._refresh_installed()

    # ── Detail prefetching ─────────────────────────────────────────────────────

    def _prefetch_details(self):
        ids = self._get_installed_ids()
        unfetched = [i for i in ids if i not in self._details]

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

    # ── Misc ───────────────────────────────────────────────────────────────────

    def _stash_thread(self, t: QThread):
        """Keep a reference to short-lived threads so they aren't garbage-collected."""
        if not hasattr(self, "_threads"):
            self._threads: list[QThread] = []
        self._threads.append(t)
        t.finished.connect(lambda: self._threads.remove(t) if t in self._threads else None)
