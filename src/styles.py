# Modern dark theme styles for the application

# Main application styling
MAIN_WINDOW_STYLE = """
QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QLabel {
    border-radius: 8px;
}
"""

# Left panel styling (game library panel)
LEFT_PANEL_STYLE = """
QWidget {
    background-color: #252525;
    border-right: 1px solid #404040;
}
"""

# Right panel styling (main content area)
RIGHT_PANEL_STYLE = """
QWidget {
    background-color: #1e1e1e;
}
"""

# Game image styling with hover effects
GAME_IMAGE_STYLE = """
QLabel {
    background-color: #2d2d2d;
    border: 2px solid #404040;
    border-radius: 12px;
    padding: 8px;
    margin: 5px;
}
QLabel:hover {
    border-color: #0078d4;
    background-color: #333333;
}
"""

# Button styling (for future use)
BUTTON_STYLE = """
QPushButton {
    background-color: #0078d4;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #106ebe;
}
QPushButton:pressed {
    background-color: #005a9e;
}
QPushButton:disabled {
    background-color: #404040;
    color: #808080;
}
"""

# Input field styling (for future use)
INPUT_STYLE = """
QLineEdit {
    background-color: #2d2d2d;
    border: 2px solid #404040;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 14px;
    color: #ffffff;
}
QLineEdit:focus {
    border-color: #0078d4;
}
"""

# List widget styling (for future use)
LIST_STYLE = """
QListWidget {
    background-color: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 6px;
    padding: 5px;
}
QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin: 2px;
}
QListWidget::item:selected {
    background-color: #0078d4;
}
QListWidget::item:hover {
    background-color: #333333;
}
"""

# Scrollbar styling (for future use)
SCROLLBAR_STYLE = """
QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 12px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background-color: #404040;
    border-radius: 6px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #505050;
}
"""

# Color constants for consistent theming
class Colors:
    BACKGROUND_DARK = "#1e1e1e"
    BACKGROUND_MEDIUM = "#252525"
    BACKGROUND_LIGHT = "#2d2d2d"
    BORDER = "#404040"
    ACCENT = "#0078d4"
    ACCENT_HOVER = "#106ebe"
    ACCENT_PRESSED = "#005a9e"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#cccccc"
    TEXT_DISABLED = "#808080"

# Layout constants
class Layout:
    MARGIN_LARGE = 30
    MARGIN_MEDIUM = 20
    MARGIN_SMALL = 10
    SPACING_LARGE = 20
    SPACING_MEDIUM = 15
    SPACING_SMALL = 10
    BORDER_RADIUS_LARGE = 12
    BORDER_RADIUS_MEDIUM = 8
    BORDER_RADIUS_SMALL = 6
