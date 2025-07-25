"""
Modern Professional UI Styling System
Light Blue, Silver & Black Theme with Premium Visual Effects

Design Philosophy:
- Clean, modern interface with subtle depth and shadows
- Professional color palette: Light blue (#3498db), Silver (#bdc3c7), Charcoal (#2c3e50)
- Smooth animations and hover effects for enhanced user experience
- High contrast for accessibility while maintaining elegant appearance
- Custom window chrome with rounded corners and modern aesthetics
"""

import os

# ============================================================================
# COLOR PALETTE - Professional Dark Mode Theme
# ============================================================================

class Colors:
    """Centralized color definitions for dark mode theming"""
    
    # Primary Colors
    PRIMARY_BLUE = "#3498db"        # Light blue - primary accent
    SECONDARY_BLUE = "#2980b9"      # Darker blue - hover states
    ACCENT_BLUE = "#5dade2"         # Lighter blue - highlights
    
    # Dark Mode Backgrounds
    BACKGROUND_DARK = "#1a1a1a"     # Main dark background
    BACKGROUND_MEDIUM = "#2d2d2d"   # Medium dark for panels
    BACKGROUND_LIGHT = "#3a3a3a"    # Lighter dark for cards/inputs
    BACKGROUND_HOVER = "#404040"    # Hover state background
    
    # Gray Palette for Dark Mode
    GRAY_DARK = "#2c2c2c"          # Dark gray for borders
    GRAY_MEDIUM = "#4a4a4a"        # Medium gray for elements
    GRAY_LIGHT = "#6a6a6a"         # Light gray for subtle borders
    
    # Legacy Silver aliases (mapped to dark equivalents)
    SILVER_LIGHT = "#3a3a3a"       # Maps to BACKGROUND_LIGHT
    SILVER = "#4a4a4a"             # Maps to GRAY_MEDIUM
    SILVER_DARK = "#2c2c2c"        # Maps to GRAY_DARK
    
    # Dark Colors
    CHARCOAL = "#1a1a1a"           # Main dark background
    CHARCOAL_LIGHT = "#2d2d2d"     # Secondary dark
    BLACK = "#000000"              # Pure black for depth
    
    # Status Colors (brightened for dark mode)
    SUCCESS = "#2ecc71"            # Brighter green for dark backgrounds
    WARNING = "#f39c12"            # Orange for warnings
    ERROR = "#e74c3c"              # Red for errors
    INFO = "#3498db"               # Blue for information
    
    # Text Colors for Dark Mode
    TEXT_PRIMARY = "#ffffff"       # White text on dark backgrounds
    TEXT_SECONDARY = "#b0b0b0"     # Light gray for secondary text
    TEXT_MUTED = "#808080"         # Muted gray text
    TEXT_LIGHT = "#ffffff"         # White text (alias)
    TEXT_ACCENT = "#3498db"        # Blue accent text

class Effects:
    """Visual effects and styling constants"""
    
    # Shadows
    SHADOW_LIGHT = "0px 2px 8px rgba(52, 152, 219, 0.15)"
    SHADOW_MEDIUM = "0px 4px 16px rgba(52, 152, 219, 0.25)"
    SHADOW_HEAVY = "0px 8px 32px rgba(52, 152, 219, 0.35)"
    
    # Border Radius
    RADIUS_SMALL = "6px"
    RADIUS_MEDIUM = "12px"
    RADIUS_LARGE = "18px"
    RADIUS_ROUND = "50%"
    
    # Gradients (updated for dark mode)
    GRADIENT_PRIMARY = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {Colors.PRIMARY_BLUE}, stop:1 {Colors.SECONDARY_BLUE})"
    GRADIENT_DARK = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {Colors.BACKGROUND_MEDIUM}, stop:1 {Colors.BACKGROUND_DARK})"
    GRADIENT_LIGHT = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {Colors.BACKGROUND_LIGHT}, stop:1 {Colors.BACKGROUND_MEDIUM})"

# ============================================================================
# MAIN WINDOW STYLING - Custom Chrome & Layout
# ============================================================================

MAIN_WINDOW_STYLE = f"""
QMainWindow {{
    background-color: {Colors.BACKGROUND_DARK};
    border: 2px solid {Colors.GRAY_MEDIUM};
    border-radius: {Effects.RADIUS_LARGE};
    color: {Colors.TEXT_PRIMARY};
    font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
    font-size: 11px;
}}

QWidget {{
    background-color: {Colors.BACKGROUND_DARK};
    color: {Colors.TEXT_PRIMARY};
}}

/* Custom Title Bar */
QMainWindow::title {{
    background-color: {Colors.BACKGROUND_MEDIUM};
    color: {Colors.TEXT_PRIMARY};
    padding: 12px;
    font-weight: 600;
    font-size: 14px;
    border-top-left-radius: {Effects.RADIUS_LARGE};
    border-top-right-radius: {Effects.RADIUS_LARGE};
}}

/* Central Widget */
QWidget#centralWidget {{
    background-color: {Colors.BACKGROUND_DARK};
    border-radius: {Effects.RADIUS_MEDIUM};
}}

/* Scrollbars */
QScrollBar:vertical {{
    background-color: {Colors.BACKGROUND_MEDIUM};
    width: 12px;
    border-radius: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {Colors.GRAY_MEDIUM};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {Colors.TEXT_SECONDARY};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    border: none;
    background: none;
}}
"""

# ============================================================================
# PANEL STYLING - Left Navigation & Content Areas
# ============================================================================

LEFT_PANEL_STYLE = f"""
QWidget {{
    background-color: {Colors.BACKGROUND_MEDIUM};
    border-right: 2px solid {Colors.GRAY_MEDIUM};
    border-top-left-radius: {Effects.RADIUS_LARGE};
    border-bottom-left-radius: {Effects.RADIUS_LARGE};
    color: {Colors.TEXT_PRIMARY};
}}

QLabel {{
    color: {Colors.TEXT_PRIMARY};
    font-weight: 500;
    padding: 0px;
    border-top: 1px solid {Colors.BACKGROUND_LIGHT};
    border-bottom: 1px solid {Colors.BACKGROUND_LIGHT};
}}

QLabel:hover {{
    background-color: {Colors.BACKGROUND_HOVER};
    border-radius: 8px;
    border-top: 1px solid {Colors.PRIMARY_BLUE};
    border-bottom: 1px solid {Colors.PRIMARY_BLUE};
}}
"""

RIGHT_PANEL_STYLE = f"""
QWidget {{
    background-color: {Colors.BACKGROUND_MEDIUM};
    border: 2px solid {Colors.GRAY_MEDIUM};
    border-top-right-radius: {Effects.RADIUS_LARGE};
    border-bottom-right-radius: {Effects.RADIUS_LARGE};
    padding: 20px;
}}

QLabel {{
    color: {Colors.TEXT_PRIMARY};
    font-weight: 400;
}}
"""

# ============================================================================
# GAME CARD STYLING - Modern Card Design
# ============================================================================

GAME_IMAGE_STYLE = f"""
QLabel {{
    background: transparent;
    border: none;
    border-radius: 0px;
    padding: 0px;
    margin: 2px 0px;
    font-weight: 600;
    color: {Colors.TEXT_PRIMARY};
    qproperty-alignment: AlignCenter;
}}

QLabel:hover {{
    border-radius: 8px;
    border: 2px solid rgba(52, 152, 219, 0.6);
    background: rgba(52, 152, 219, 0.1);
}}

QLabel:pressed {{
    background: {Colors.ACCENT_BLUE};
    border-color: {Colors.SECONDARY_BLUE};
}}
"""

# ============================================================================
# BUTTON STYLING - Modern Interactive Elements
# ============================================================================

BUTTON_PRIMARY_STYLE = f"""
QPushButton {{
    background-color: {Colors.PRIMARY_BLUE};
    color: {Colors.TEXT_PRIMARY};
    border: none;
    border-radius: {Effects.RADIUS_MEDIUM};
    padding: 12px 24px;
    font-size: 12px;
    font-weight: 600;
    min-width: 120px;
}}

QPushButton:hover {{
    background-color: {Colors.SECONDARY_BLUE};
}}

QPushButton:pressed {{
    background-color: {Colors.ACCENT_BLUE};
}}

QPushButton:disabled {{
    background-color: {Colors.GRAY_MEDIUM};
    color: {Colors.TEXT_SECONDARY};
}}
"""

BUTTON_SECONDARY_STYLE = f"""
QPushButton {{
    background-color: {Colors.GRAY_MEDIUM};
    color: {Colors.TEXT_PRIMARY};
    border: none;
    border-radius: {Effects.RADIUS_MEDIUM};
    padding: 10px 20px;
    font-size: 12px;
    font-weight: 500;
    min-width: 100px;
}}

QPushButton:hover {{
    background-color: {Colors.BACKGROUND_HOVER};
}}

QPushButton:pressed {{
    background-color: {Colors.GRAY_LIGHT};
}}
"""

BUTTON_DANGER_STYLE = f"""
QPushButton {{
    background: {Colors.ERROR};
    color: {Colors.TEXT_LIGHT};
    border: none;
    border-radius: {Effects.RADIUS_MEDIUM};
    padding: 10px 20px;
    font-size: 12px;
    font-weight: 600;
}}

QPushButton:hover {{
    background: #c0392b;
    box-shadow: {Effects.SHADOW_MEDIUM};
}}

QPushButton:pressed {{
    background: #a93226;
}}
"""

# ============================================================================
# INPUT FIELD STYLING - Modern Form Elements
# ============================================================================

INPUT_STYLE = f"""
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {Colors.BACKGROUND_MEDIUM};
    border: 2px solid {Colors.GRAY_MEDIUM};
    border-radius: {Effects.RADIUS_SMALL};
    padding: 12px 16px;
    font-size: 12px;
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.PRIMARY_BLUE};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {Colors.PRIMARY_BLUE};
}}

QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
    border-color: {Colors.SECONDARY_BLUE};
}}

QLineEdit::placeholder, QTextEdit::placeholder, QPlainTextEdit::placeholder {{
    color: {Colors.TEXT_SECONDARY};
    font-style: italic;
}}
"""

COMBOBOX_STYLE = f"""
QComboBox {{
    background: {Colors.BACKGROUND_LIGHT};
    border: 2px solid {Colors.GRAY_MEDIUM};
    border-radius: {Effects.RADIUS_SMALL};
    padding: 10px 16px;
    font-size: 12px;
    color: {Colors.TEXT_PRIMARY};
    min-width: 150px;
}}

QComboBox:hover {{
    border-color: {Colors.SECONDARY_BLUE};
}}

QComboBox:focus {{
    border-color: {Colors.PRIMARY_BLUE};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 8px solid {Colors.PRIMARY_BLUE};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background: {Colors.BACKGROUND_LIGHT};
    border: 2px solid {Colors.PRIMARY_BLUE};
    border-radius: {Effects.RADIUS_SMALL};
    padding: 4px;
    selection-background-color: {Colors.ACCENT_BLUE};
}}
"""

# ============================================================================
# CHECKBOX & RADIO BUTTON STYLING
# ============================================================================

CHECKBOX_STYLE = f"""
QCheckBox {{
    color: {Colors.TEXT_PRIMARY};
    font-size: 12px;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {Colors.GRAY_MEDIUM};
    border-radius: 4px;
    background: {Colors.BACKGROUND_LIGHT};
}}

QCheckBox::indicator:hover {{
    border-color: {Colors.PRIMARY_BLUE};
}}

QCheckBox::indicator:checked {{
    background: {Colors.PRIMARY_BLUE};
    border-color: {Colors.PRIMARY_BLUE};
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
}}
"""

# ============================================================================
# DIALOG & POPUP STYLING
# ============================================================================

DIALOG_STYLE = f"""
QDialog {{
    background: {Colors.BACKGROUND_MEDIUM};
    border: 3px solid {Colors.PRIMARY_BLUE};
    border-radius: {Effects.RADIUS_LARGE};
    color: {Colors.TEXT_PRIMARY};
}}

QDialog QLabel {{
    color: {Colors.TEXT_PRIMARY};
    font-size: 12px;
    margin: 8px 0;
}}

QDialog QPushButton {{
    min-width: 100px;
    margin: 8px 4px;
}}
"""

# ============================================================================
# PROGRESS BAR STYLING
# ============================================================================

PROGRESS_BAR_STYLE = f"""
QProgressBar {{
    background: {Colors.BACKGROUND_MEDIUM};
    border: 2px solid {Colors.GRAY_DARK};
    border-radius: {Effects.RADIUS_SMALL};
    text-align: center;
    font-size: 11px;
    font-weight: 600;
    color: {Colors.TEXT_PRIMARY};
    height: 24px;
}}

QProgressBar::chunk {{
    background: {Effects.GRADIENT_PRIMARY};
    border-radius: {Effects.RADIUS_SMALL};
    margin: 1px;
}}
"""

# ============================================================================
# MENU & MENUBAR STYLING
# ============================================================================

MENU_STYLE = f"""
QMenuBar {{
    background: {Effects.GRADIENT_DARK};
    color: {Colors.TEXT_LIGHT};
    border-bottom: 2px solid {Colors.PRIMARY_BLUE};
    padding: 4px;
}}

QMenuBar::item {{
    background: transparent;
    padding: 8px 16px;
    border-radius: {Effects.RADIUS_SMALL};
}}

QMenuBar::item:selected {{
    background: {Colors.PRIMARY_BLUE};
}}

QMenu {{
    background: {Colors.BACKGROUND_MEDIUM};
    border: 2px solid {Colors.PRIMARY_BLUE};
    border-radius: {Effects.RADIUS_SMALL};
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: {Effects.RADIUS_SMALL};
    color: {Colors.TEXT_PRIMARY};
}}

QMenu::item:selected {{
    background: {Colors.ACCENT_BLUE};
    color: {Colors.TEXT_LIGHT};
}}
"""

# ============================================================================
# STATUS BAR STYLING
# ============================================================================

STATUS_BAR_STYLE = f"""
QStatusBar {{
    background: {Effects.GRADIENT_DARK};
    color: {Colors.TEXT_LIGHT};
    border-top: 2px solid {Colors.PRIMARY_BLUE};
    padding: 6px 12px;
    font-size: 11px;
}}

QStatusBar::item {{
    border: none;
}}

QStatusBar QLabel {{
    color: {Colors.TEXT_LIGHT};
    padding: 0 8px;
}}
"""

# Legacy button styling for compatibility
BUTTON_STYLE = BUTTON_PRIMARY_STYLE

# ============================================================================
# LAYOUT CONSTANTS - Spacing and sizing values
# ============================================================================

class Layout:
    """Layout constants for consistent spacing and sizing"""
    MARGIN_LARGE = 40
    MARGIN_MEDIUM = 25
    MARGIN_SMALL = 15
    SPACING_LARGE = 25
    SPACING_MEDIUM = 20
    SPACING_SMALL = 15
    BORDER_RADIUS_LARGE = 12
    BORDER_RADIUS_MEDIUM = 8
    BORDER_RADIUS_SMALL = 6
