"""
Theme — centralized colors, fonts, and stylesheet strings for the entire app.

Import Colors or Fonts for constants, or call the helper functions to get
pre-built Qt stylesheet strings for specific widget types.
"""

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------

class Colors:
    BG_BASE        = "#0f0f0f"   # Main window background
    BG_SURFACE     = "#1c1c1e"   # Cards / panels
    BG_ELEVATED    = "#2c2c2e"   # Hover / active state
    BG_INPUT       = "#3a3a3c"   # Input fields
    BG_SIDEBAR     = "#141416"   # Sidebar background

    ACCENT         = "#3a86ff"   # Primary blue accent
    ACCENT_HOVER   = "#4d95ff"
    ACCENT_PRESSED = "#2568d4"

    SUCCESS        = "#30d158"
    WARNING        = "#ffd60a"
    ERROR          = "#ff453a"
    MUTED          = "#636366"

    TEXT_PRIMARY   = "#ffffff"
    TEXT_SECONDARY = "#8e8e93"
    TEXT_DISABLED  = "#48484a"

    BORDER         = "#3a3a3c"
    BORDER_FOCUS   = "#3a86ff"
    DIVIDER        = "#2c2c2e"


class Fonts:
    FAMILY     = "Segoe UI"
    SIZE_XS    = 10
    SIZE_SM    = 11
    SIZE_BASE  = 12
    SIZE_MD    = 14
    SIZE_LG    = 18
    SIZE_XL    = 24
    SIZE_HERO  = 32


# ---------------------------------------------------------------------------
# Spacing / layout constants
# ---------------------------------------------------------------------------

class Layout:
    RADIUS_SM   = 6
    RADIUS_MD   = 10
    RADIUS_LG   = 14
    MARGIN_SM   = 8
    MARGIN_MD   = 16
    MARGIN_LG   = 24
    SPACING_SM  = 6
    SPACING_MD  = 12
    SPACING_LG  = 20
    SIDEBAR_W   = 220


# ---------------------------------------------------------------------------
# Pre-built stylesheet strings
# ---------------------------------------------------------------------------

MAIN_WINDOW = f"""
    QWidget {{
        background-color: {Colors.BG_BASE};
        color: {Colors.TEXT_PRIMARY};
        font-family: {Fonts.FAMILY};
        font-size: {Fonts.SIZE_BASE}px;
    }}
    QScrollBar:vertical {{
        background: {Colors.BG_SURFACE};
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {Colors.BG_ELEVATED};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {Colors.MUTED};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background: {Colors.BG_SURFACE};
        height: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {Colors.BG_ELEVATED};
        border-radius: 4px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {Colors.MUTED};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
"""

SIDEBAR = f"""
    QWidget {{
        background-color: {Colors.BG_SIDEBAR};
        border-right: 1px solid {Colors.DIVIDER};
    }}
"""

DETAILS_PANEL = f"""
    QWidget {{
        background-color: {Colors.BG_BASE};
    }}
"""

GAME_CARD_NORMAL = f"""
    QFrame {{
        background-color: {Colors.BG_SURFACE};
        border-radius: {Layout.RADIUS_MD}px;
        border: 1px solid transparent;
    }}
    QFrame:hover {{
        background-color: {Colors.BG_ELEVATED};
        border: 1px solid {Colors.BORDER};
    }}
    QLabel {{
        background: transparent;
        border: none;
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_SM}px;
    }}
"""

GAME_CARD_SELECTED = f"""
    QFrame {{
        background-color: {Colors.BG_ELEVATED};
        border-radius: {Layout.RADIUS_MD}px;
        border: 1px solid {Colors.ACCENT};
    }}
    QLabel {{
        background: transparent;
        border: none;
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_SM}px;
        font-weight: 600;
    }}
"""

BTN_PRIMARY = f"""
    QPushButton {{
        background-color: {Colors.ACCENT};
        color: {Colors.TEXT_PRIMARY};
        border: none;
        border-radius: {Layout.RADIUS_SM}px;
        padding: 9px 20px;
        font-size: {Fonts.SIZE_SM}px;
        font-weight: 600;
        font-family: {Fonts.FAMILY};
    }}
    QPushButton:hover {{
        background-color: {Colors.ACCENT_HOVER};
    }}
    QPushButton:pressed {{
        background-color: {Colors.ACCENT_PRESSED};
    }}
    QPushButton:disabled {{
        background-color: {Colors.BG_ELEVATED};
        color: {Colors.TEXT_DISABLED};
    }}
"""

BTN_SECONDARY = f"""
    QPushButton {{
        background-color: {Colors.BG_ELEVATED};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        border-radius: {Layout.RADIUS_SM}px;
        padding: 9px 20px;
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
    }}
    QPushButton:hover {{
        background-color: {Colors.BG_INPUT};
        border-color: {Colors.MUTED};
    }}
    QPushButton:pressed {{
        background-color: {Colors.BG_SURFACE};
    }}
    QPushButton:disabled {{
        background-color: {Colors.BG_SURFACE};
        color: {Colors.TEXT_DISABLED};
        border-color: {Colors.DIVIDER};
    }}
"""

BTN_DANGER = f"""
    QPushButton {{
        background-color: transparent;
        color: {Colors.ERROR};
        border: 1px solid {Colors.ERROR};
        border-radius: {Layout.RADIUS_SM}px;
        padding: 9px 20px;
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
    }}
    QPushButton:hover {{
        background-color: {Colors.ERROR};
        color: {Colors.TEXT_PRIMARY};
    }}
    QPushButton:pressed {{
        background-color: #cc362e;
    }}
    QPushButton:disabled {{
        color: {Colors.TEXT_DISABLED};
        border-color: {Colors.TEXT_DISABLED};
    }}
"""

BTN_SUCCESS = f"""
    QPushButton {{
        background-color: {Colors.SUCCESS};
        color: #000000;
        border: none;
        border-radius: {Layout.RADIUS_SM}px;
        padding: 9px 20px;
        font-size: {Fonts.SIZE_SM}px;
        font-weight: 600;
        font-family: {Fonts.FAMILY};
    }}
    QPushButton:hover {{
        background-color: #3de069;
    }}
    QPushButton:pressed {{
        background-color: #26a844;
    }}
    QPushButton:disabled {{
        background-color: {Colors.BG_ELEVATED};
        color: {Colors.TEXT_DISABLED};
    }}
"""

INPUT = f"""
    QLineEdit, QSpinBox, QComboBox, QTextEdit, QPlainTextEdit {{
        background-color: {Colors.BG_INPUT};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        border-radius: {Layout.RADIUS_SM}px;
        padding: 7px 10px;
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        selection-background-color: {Colors.ACCENT};
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {Colors.BORDER_FOCUS};
    }}
    QSpinBox::up-button, QSpinBox::down-button {{
        background-color: {Colors.BG_ELEVATED};
        border: none;
        width: 18px;
    }}
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
        background-color: {Colors.ACCENT};
    }}
    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {Colors.BG_ELEVATED};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        selection-background-color: {Colors.ACCENT};
        outline: none;
    }}
"""

CHECKBOX = f"""
    QCheckBox {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid {Colors.BORDER};
        background-color: {Colors.BG_INPUT};
    }}
    QCheckBox::indicator:checked {{
        background-color: {Colors.ACCENT};
        border-color: {Colors.ACCENT};
    }}
    QCheckBox::indicator:hover {{
        border-color: {Colors.BORDER_FOCUS};
    }}
"""

LABEL_HEADING = f"""
    QLabel {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_LG}px;
        font-weight: 700;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
"""

LABEL_SUBHEADING = f"""
    QLabel {{
        color: {Colors.TEXT_SECONDARY};
        font-size: {Fonts.SIZE_SM}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
"""

LABEL_MUTED = f"""
    QLabel {{
        color: {Colors.TEXT_DISABLED};
        font-size: {Fonts.SIZE_XS}px;
        font-family: {Fonts.FAMILY};
        background: transparent;
    }}
"""

PROGRESS_BAR = f"""
    QProgressBar {{
        background-color: {Colors.BG_ELEVATED};
        border: none;
        border-radius: 4px;
        height: 8px;
        text-align: center;
        color: transparent;
    }}
    QProgressBar::chunk {{
        background-color: {Colors.ACCENT};
        border-radius: 4px;
    }}
"""

LOG_AREA = f"""
    QPlainTextEdit {{
        background-color: #0a0a0a;
        color: #cccccc;
        border: 1px solid {Colors.DIVIDER};
        border-radius: {Layout.RADIUS_SM}px;
        padding: 8px;
        font-family: Consolas, "Courier New", monospace;
        font-size: {Fonts.SIZE_SM}px;
        selection-background-color: {Colors.ACCENT};
    }}
"""

DIALOG = f"""
    QDialog {{
        background-color: {Colors.BG_SURFACE};
        color: {Colors.TEXT_PRIMARY};
        font-family: {Fonts.FAMILY};
    }}
    QLabel {{
        background: transparent;
        color: {Colors.TEXT_PRIMARY};
        font-family: {Fonts.FAMILY};
    }}
"""

SEPARATOR = f"""
    QFrame[frameShape="4"], QFrame[frameShape="5"] {{
        color: {Colors.DIVIDER};
        background-color: {Colors.DIVIDER};
        max-height: 1px;
        border: none;
    }}
"""

TOOLTIP = f"""
    QToolTip {{
        background-color: {Colors.BG_ELEVATED};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        border-radius: {Layout.RADIUS_SM}px;
        padding: 4px 8px;
        font-family: {Fonts.FAMILY};
        font-size: {Fonts.SIZE_SM}px;
    }}
"""

# Combined global stylesheet applied to the main window
GLOBAL = MAIN_WINDOW + TOOLTIP + SEPARATOR
