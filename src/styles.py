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
# UI MEASUREMENT CONSTANTS
# ============================================================================

# Border and spacing constants (pixels)
BORDER_WIDTH_THIN = 1               # Thin border for subtle separations
BORDER_WIDTH_STANDARD = 2           # Standard border width for most elements
BORDER_WIDTH_THICK = 3              # Thick border for emphasis

# Padding constants (pixels)
PADDING_NONE = 0                    # No padding
PADDING_SMALL = 10                  # Small padding for compact elements
PADDING_MEDIUM = 12                 # Medium padding for buttons
PADDING_LARGE = 20                  # Large padding for content areas
PADDING_BUTTON_HORIZONTAL = 24      # Horizontal padding for primary buttons

# Margin constants (pixels)
MARGIN_NONE = 0                     # No margins
MARGIN_TINY = 2                     # Tiny margin for image spacing
MARGIN_SMALL = 8                    # Small margin for checkboxes and spacing
MARGIN_MEDIUM = 15                  # Medium margin for section separation

# Font size constants (pixels)
FONT_SIZE_SMALL = 11                # Small font for status bars and fine print
FONT_SIZE_STANDARD = 12             # Standard font size for UI elements
FONT_SIZE_TITLE = 14                # Title font size for headers

# Width and height constants (pixels)
SCROLLBAR_WIDTH = 12                # Width of custom scrollbars
SCROLLBAR_BORDER_RADIUS = 6         # Border radius for scrollbars
SCROLLBAR_MIN_HANDLE_HEIGHT = 20    # Minimum height for scrollbar handles
BUTTON_MIN_WIDTH_STANDARD = 100     # Minimum width for standard buttons
BUTTON_MIN_WIDTH_PRIMARY = 120      # Minimum width for primary buttons
COMBOBOX_MIN_WIDTH = 150            # Minimum width for combo boxes
COMBOBOX_DROPDOWN_WIDTH = 30        # Width of combo box dropdown arrow
COMBOBOX_ARROW_MARGIN = 8           # Margin for combo box arrow
CHECKBOX_SIZE = 18                  # Size of checkbox indicators
PROGRESS_BAR_HEIGHT = 24            # Height of progress bars

# Border radius constants (pixels - keeping string format for CSS)
RADIUS_NONE = "0px"                 # No border radius
RADIUS_SMALL_PX = "6px"             # Small border radius
RADIUS_MEDIUM_PX = "8px"            # Medium border radius 
RADIUS_LARGE_PX = "12px"            # Large border radius
RADIUS_XLARGE_PX = "18px"           # Extra large border radius
RADIUS_CHECKBOX = "4px"             # Border radius for checkboxes

# Shadow offset constants (pixels)
SHADOW_OFFSET_LIGHT_Y = 2           # Light shadow Y offset
SHADOW_OFFSET_LIGHT_BLUR = 8        # Light shadow blur radius
SHADOW_OFFSET_MEDIUM_Y = 4          # Medium shadow Y offset
SHADOW_OFFSET_MEDIUM_BLUR = 16      # Medium shadow blur radius
SHADOW_OFFSET_HEAVY_Y = 8           # Heavy shadow Y offset
SHADOW_OFFSET_HEAVY_BLUR = 32       # Heavy shadow blur radius

# Opacity constants (for RGBA values)
OPACITY_LIGHT = 0.15                # Light opacity for subtle effects
OPACITY_MEDIUM = 0.25               # Medium opacity
OPACITY_HEAVY = 0.35                # Heavy opacity for strong effects

# Arrow constants for combo boxes
ARROW_BORDER_WIDTH = 6              # Border width for dropdown arrows
ARROW_TOP_HEIGHT = 8                # Height of dropdown arrow

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
    
    # Shadows using the defined constants
    SHADOW_LIGHT = f"0px {SHADOW_OFFSET_LIGHT_Y}px {SHADOW_OFFSET_LIGHT_BLUR}px rgba(52, 152, 219, {OPACITY_LIGHT})"
    SHADOW_MEDIUM = f"0px {SHADOW_OFFSET_MEDIUM_Y}px {SHADOW_OFFSET_MEDIUM_BLUR}px rgba(52, 152, 219, {OPACITY_MEDIUM})"
    SHADOW_HEAVY = f"0px {SHADOW_OFFSET_HEAVY_Y}px {SHADOW_OFFSET_HEAVY_BLUR}px rgba(52, 152, 219, {OPACITY_HEAVY})"
    
    # Border Radius
    RADIUS_SMALL = RADIUS_SMALL_PX
    RADIUS_MEDIUM = RADIUS_LARGE_PX
    RADIUS_LARGE = RADIUS_XLARGE_PX
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
    border: {BORDER_WIDTH_STANDARD}px solid {Colors.GRAY_MEDIUM};
    border-radius: {Effects.RADIUS_LARGE};
    color: {Colors.TEXT_PRIMARY};
    font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
    font-size: {FONT_SIZE_SMALL}px;
}}

QWidget {{
    background-color: {Colors.BACKGROUND_DARK};
    color: {Colors.TEXT_PRIMARY};
}}

/* Custom Title Bar */
QMainWindow::title {{
    background-color: {Colors.BACKGROUND_MEDIUM};
    color: {Colors.TEXT_PRIMARY};
    padding: {PADDING_MEDIUM}px;
    font-weight: 600;
    font-size: {FONT_SIZE_TITLE}px;
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
    width: {SCROLLBAR_WIDTH}px;
    border-radius: {SCROLLBAR_BORDER_RADIUS}px;
    margin: {MARGIN_NONE};
}}

QScrollBar::handle:vertical {{
    background-color: {Colors.GRAY_MEDIUM};
    border-radius: {SCROLLBAR_BORDER_RADIUS}px;
    min-height: {SCROLLBAR_MIN_HANDLE_HEIGHT}px;
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
    border-right: {BORDER_WIDTH_STANDARD}px solid {Colors.GRAY_MEDIUM};
    border-top-left-radius: {Effects.RADIUS_LARGE};
    border-bottom-left-radius: {Effects.RADIUS_LARGE};
    color: {Colors.TEXT_PRIMARY};
}}

QLabel {{
    color: {Colors.TEXT_PRIMARY};
    font-weight: 500;
    padding: {PADDING_NONE}px;
    border-top: {BORDER_WIDTH_THIN}px solid {Colors.BACKGROUND_LIGHT};
    border-bottom: {BORDER_WIDTH_THIN}px solid {Colors.BACKGROUND_LIGHT};
}}

QLabel:hover {{
    background-color: {Colors.BACKGROUND_HOVER};
    border-radius: {RADIUS_MEDIUM_PX};
    border-top: {BORDER_WIDTH_THIN}px solid {Colors.PRIMARY_BLUE};
    border-bottom: {BORDER_WIDTH_THIN}px solid {Colors.PRIMARY_BLUE};
}}
"""

RIGHT_PANEL_STYLE = f"""
QWidget {{
    background-color: {Colors.BACKGROUND_MEDIUM};
    border: {BORDER_WIDTH_STANDARD}px solid {Colors.GRAY_MEDIUM};
    border-top-right-radius: {Effects.RADIUS_LARGE};
    border-bottom-right-radius: {Effects.RADIUS_LARGE};
    padding: {PADDING_LARGE}px;
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
