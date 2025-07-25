"""
Main Window Module for Dedicated Server Automation Application

This module contains the MainWindow class which serves as the primary GUI container
for the application. It provides a two-panel layout with game selection on the left
and detailed game information on the right.

Features:
- Dynamic window resizing with minimum size constraints
- Fullscreen support (F11 to toggle, Escape to exit)
- Modern dark theme styling
- Clickable game images for navigation
- Real-time game server status monitoring

The main window acts as the central hub for all server management activities.
"""

# ============================================================================
# WINDOW CONFIGURATION CONSTANTS
# ============================================================================

# Window sizing constants
WINDOW_MIN_WIDTH = 1200              # Minimum window width for UI usability
WINDOW_MIN_HEIGHT = 800              # Minimum window height for UI usability
WINDOW_DEFAULT_WIDTH = 1600          # Default window width on startup
WINDOW_DEFAULT_HEIGHT = 1000         # Default window height on startup

# Layout configuration constants
LAYOUT_NO_SPACING = 0                # No spacing between layout elements
LAYOUT_SMALL_SPACING = 2             # Small spacing for subtle visual separation
LAYOUT_NO_MARGINS = 0                # No margins around layout containers

# Image sizing constants
GAME_IMAGE_WIDTH = 400               # Width for game images in list
GAME_IMAGE_HEIGHT = 300               # Height for game images in list
GAME_IMAGE_MIN_HEIGHT = 80           # Minimum height for game image labels
GAME_IMAGE_MAX_HEIGHT = 80           # Maximum height for game image labels

# Animation constants
HOVER_ANIMATION_DURATION_MS = 200    # Duration of hover animations in milliseconds
HOVER_SCALE_FACTOR = 1.05           # Scale factor for hover zoom effect (5% larger)
HOVER_SCALE_OFFSET_DIVISOR = 2       # Divisor for centering scaled images

# Layout proportion constants
LEFT_PANEL_LAYOUT_PROPORTION = 4     # Left panel takes 4 parts of layout (40%)
RIGHT_PANEL_LAYOUT_PROPORTION = 6    # Right panel takes 6 parts of layout (60%)

# Hover effect styling constants
HOVER_BACKGROUND_OPACITY = 0.1       # Background opacity for hover effects
HOVER_BORDER_OPACITY = 0.6          # Border opacity for hover effects
HOVER_BORDER_WIDTH_PX = 2            # Border width for hover effects in pixels
HOVER_BORDER_RADIUS_PX = 8           # Border radius for hover effects in pixels
HOVER_FONT_WEIGHT = 600              # Font weight for hover text

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QKeySequence, QIcon
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtWidgets import QStackedWidget, QShortcut, QGraphicsOpacityEffect
from game_list_page import GameListPage
from game import Game
from game_details_page import GameDetailsPage
from static.games_list import GAMES_LIST
from styles import (
    MAIN_WINDOW_STYLE, 
    LEFT_PANEL_STYLE, 
    RIGHT_PANEL_STYLE, 
    GAME_IMAGE_STYLE,
    BUTTON_PRIMARY_STYLE,
    BUTTON_SECONDARY_STYLE,
    INPUT_STYLE,
    Layout,
    Colors
)


class MainWindow(QWidget):
    """
    Main application window class.
    
    Provides the primary interface for the Dedicated Server Automation application.
    Features a two-panel layout with game selection on the left and detailed 
    information/controls on the right.
    
    Attributes:
        games (list): List of Game objects representing available games
        game_details_page (GameDetailsPage): Right panel for game details
        is_fullscreen (bool): Current fullscreen state
        normal_geometry (QRect): Saved window geometry before fullscreen
        fullscreen_shortcut (QShortcut): F11 key shortcut for fullscreen toggle
        escape_shortcut (QShortcut): Escape key shortcut for exiting fullscreen
    """
    
    def __init__(self):
        """
        Initialize the main window.
        
        Sets up the UI, loads games, and configures keyboard shortcuts.
        """
        super().__init__()
        self.initUI()

    def _set_window_icon(self):
        """
        Set the application window icon.
        
        Attempts to load the custom application icon from the assets directory.
        Falls back gracefully if the icon file is not found.
        """
        try:
            # Get the path to the icon file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "assets", "app_icon.ico")
            
            # Set icon if file exists
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                self.setWindowIcon(icon)
                
                # Also set the application icon (for taskbar)
                QApplication.instance().setWindowIcon(icon)
            else:
                # Try SVG fallback
                svg_path = os.path.join(script_dir, "assets", "app_icon.svg") 
                if os.path.exists(svg_path):
                    icon = QIcon(svg_path)
                    self.setWindowIcon(icon)
                    QApplication.instance().setWindowIcon(icon)
                else:
                    print("Warning: Application icon not found")
                    
        except Exception as e:
            print(f"Warning: Could not load application icon: {e}")

    def initUI(self):
        """
        Initialize the user interface.
        
        Creates the main layout with:
        - Left panel: Clickable game images in a vertical list
        - Right panel: Detailed game information and server controls
        - Fullscreen support with keyboard shortcuts
        - Modern light blue/silver/black theme styling
        - Custom application icon
        - Enhanced window appearance
        
        The window is designed to be responsive with minimum size constraints
        and supports both windowed and fullscreen modes.
        """
        # Set window title with user instructions
        self.setWindowTitle('Dedicated Server Automation - Press F11 for Fullscreen')
        
        # Set application icon
        self._set_window_icon()
        
        # Configure dynamic window sizing
        # Minimum size ensures UI elements remain usable
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)  # Minimum size for usability
        self.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)  # Default starting size for good visibility
        
        # Start in windowed mode (not maximized)
        self.setWindowState(self.windowState() & ~Qt.WindowMaximized)
        
        # Configure fullscreen keyboard shortcuts
        # F11 is the standard fullscreen toggle key in most applications
        self.fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        self.fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
        
        # Escape key provides standard way to exit fullscreen
        self.escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.escape_shortcut.activated.connect(self.exit_fullscreen)
        
        # Initialize fullscreen state tracking
        self.is_fullscreen = False
        self.normal_geometry = None  # Store geometry before fullscreen
        
        # Apply the modern light blue/silver/black theme styling
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # Create main horizontal layout (left panel + right panel)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(LAYOUT_NO_SPACING)  # No spacing between panels for seamless look
        main_layout.setContentsMargins(LAYOUT_NO_MARGINS, LAYOUT_NO_MARGINS, LAYOUT_NO_MARGINS, LAYOUT_NO_MARGINS)  # Edge-to-edge layout
        
        # Configure left panel for game image list
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(LAYOUT_NO_MARGINS, LAYOUT_NO_MARGINS, LAYOUT_NO_MARGINS, LAYOUT_NO_MARGINS)  # Remove margins for full-width images
        left_layout.setSpacing(LAYOUT_SMALL_SPACING)  # Small spacing for blur border effect
        
        # Load and display game images
        self._setup_game_images(left_layout)
        
        # Push all game images to the top of the left panel
        left_layout.addStretch()
        
        # Create right panel for game details and controls
        self.game_details_page = GameDetailsPage()
        
        # Assemble the main layout
        self._assemble_main_layout(main_layout, left_layout)
    
    def _setup_game_images(self, left_layout):
        """
        Set up clickable game images in the left panel.
        
        Loads game data from the games list, creates Game objects,
        and sets up clickable image labels for navigation.
        
        Args:
            left_layout (QVBoxLayout): Layout to add game images to
        """
        # Create Game objects from the static games list
        self.games = [Game(name) for name in GAMES_LIST]
        
        for game in self.games:
            # Skip games without image URLs
            if not game.image_url:
                continue
            
            # Resolve image file path
            image_path = self._resolve_image_path(game.image_url)
            
            if image_path and os.path.exists(image_path):
                try:
                    # Create clickable image widget
                    image_label = self._create_game_image_label(image_path, game)
                    left_layout.addWidget(image_label)
                except Exception as e:
                    # Log error but continue with other games
                    print(f"Failed to load image for {game.name}: {e}")
    
    def _resolve_image_path(self, image_url):
        """
        Resolve the full path to a game image file.
        
        Tries multiple potential locations for the image file:
        1. Relative to the current script
        2. In the images subdirectory
        3. Fallback to known good image
        
        Args:
            image_url (str): Relative path to the image file
            
        Returns:
            str: Full path to the image file, or None if not found
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try the provided path relative to script directory
        image_path = os.path.join(script_dir, image_url)
        if os.path.exists(image_path):
            return image_path
        
        # Try in the images subdirectory
        fallback_path = os.path.join(script_dir, "images", "palworld_image.jpg")
        if os.path.exists(fallback_path):
            return fallback_path
        
        return None
    
    def _create_game_image_label(self, image_path, game):
        """
        Create a clickable image label for a game.
        
        Args:
            image_path (str): Path to the image file
            game (Game): Game object to associate with this image
            
        Returns:
            QLabel: Configured image label widget
        """
        # Load and scale the image
        pixmap = QPixmap(image_path)
        # Make image full width with proper aspect ratio
        scaled_pixmap = pixmap.scaled(GAME_IMAGE_WIDTH, GAME_IMAGE_HEIGHT, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        # Create the label with image
        image_label = QLabel()
        image_label.setPixmap(scaled_pixmap)
        image_label.setStyleSheet(GAME_IMAGE_STYLE)
        image_label.setScaledContents(True)
        image_label.setMinimumHeight(GAME_IMAGE_MIN_HEIGHT)
        image_label.setMaximumHeight(GAME_IMAGE_MAX_HEIGHT)
        
        # Store reference to game for hover effects
        image_label.game = game
        
        # Override mouse events for custom hover effects
        image_label.enterEvent = lambda event: self._on_image_hover_enter(image_label)
        image_label.leaveEvent = lambda event: self._on_image_hover_leave(image_label)
        
        # Make it clickable with visual feedback
        image_label.setCursor(Qt.PointingHandCursor)
        # Use lambda to capture the game object for the click handler
        image_label.mousePressEvent = lambda event, g=game: self.on_game_clicked(g)
        
        return image_label
    
    def _on_image_hover_enter(self, image_label):
        """Handle mouse enter event for game images"""
        # Create scale animation
        self.hover_animation = QPropertyAnimation(image_label, b"geometry")
        self.hover_animation.setDuration(HOVER_ANIMATION_DURATION_MS)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Get current geometry and calculate scaled geometry
        current_rect = image_label.geometry()
        scale_factor = HOVER_SCALE_FACTOR
        new_width = int(current_rect.width() * scale_factor)
        new_height = int(current_rect.height() * scale_factor)
        
        # Center the scaled image
        x_offset = (new_width - current_rect.width()) // HOVER_SCALE_OFFSET_DIVISOR
        y_offset = (new_height - current_rect.height()) // HOVER_SCALE_OFFSET_DIVISOR
        
        scaled_rect = QRect(
            current_rect.x() - x_offset,
            current_rect.y() - y_offset,
            new_width,
            new_height
        )
        
        self.hover_animation.setStartValue(current_rect)
        self.hover_animation.setEndValue(scaled_rect)
        self.hover_animation.start()
        
        # Add glow effect
        image_label.setStyleSheet(f"""
            QLabel {{
                background: rgba(52, 152, 219, {HOVER_BACKGROUND_OPACITY});
                border: {HOVER_BORDER_WIDTH_PX}px solid rgba(52, 152, 219, {HOVER_BORDER_OPACITY});
                border-radius: {HOVER_BORDER_RADIUS_PX}px;
                padding: 0px;
                margin: 2px 0px;
                font-weight: {HOVER_FONT_WEIGHT};
                color: {Colors.TEXT_PRIMARY};
                qproperty-alignment: AlignCenter;
            }}
        """)
    
    def _on_image_hover_leave(self, image_label):
        """Handle mouse leave event for game images"""
        # Create scale animation back to normal
        self.hover_animation = QPropertyAnimation(image_label, b"geometry")
        self.hover_animation.setDuration(HOVER_ANIMATION_DURATION_MS)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Get current geometry and calculate original geometry
        current_rect = image_label.geometry()
        scale_factor = 1.0 / HOVER_SCALE_FACTOR
        new_width = int(current_rect.width() * scale_factor)
        new_height = int(current_rect.height() * scale_factor)
        
        # Center the normal image
        x_offset = (current_rect.width() - new_width) // HOVER_SCALE_OFFSET_DIVISOR
        y_offset = (current_rect.height() - new_height) // HOVER_SCALE_OFFSET_DIVISOR
        
        normal_rect = QRect(
            current_rect.x() + x_offset,
            current_rect.y() + y_offset,
            new_width,
            new_height
        )
        
        self.hover_animation.setStartValue(current_rect)
        self.hover_animation.setEndValue(normal_rect)
        self.hover_animation.start()
        
        # Remove glow effect
        image_label.setStyleSheet(GAME_IMAGE_STYLE)
    
    def _assemble_main_layout(self, main_layout, left_layout):
        """
        Assemble the main application layout.
        
        Combines the left game selection panel with the right details panel
        in the appropriate proportions.
        
        Args:
            main_layout (QHBoxLayout): Main horizontal layout container
            left_layout (QVBoxLayout): Left panel layout with game images
        """
        # Create widget container for left layout
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setStyleSheet(LEFT_PANEL_STYLE)
        
        # Add both panels to main layout with sizing ratios
        main_layout.addWidget(left_widget, LEFT_PANEL_LAYOUT_PROPORTION)  # Left takes 4 parts (40% of width)
        main_layout.addWidget(self.game_details_page, RIGHT_PANEL_LAYOUT_PROPORTION)  # Right takes 6 parts (60% of width)

        # Apply the main layout to the window
        self.setLayout(main_layout)
    
    def on_game_clicked(self, game):
        """
        Handle game image click events.
        
        When a user clicks on a game image in the left panel, this method
        updates the right panel to show detailed information and controls
        for that specific game.
        
        Args:
            game (Game): The game object that was clicked
        """
        # Update the right panel with the selected game's information
        self.game_details_page.update_game(game)
    
    def toggle_fullscreen(self):
        """
        Toggle between fullscreen and windowed mode.
        
        Switches the application between fullscreen and normal windowed mode.
        Preserves the window geometry when switching modes so the user
        can return to their preferred window size.
        """
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()
    
    def enter_fullscreen(self):
        """
        Enter fullscreen mode.
        
        Saves the current window geometry and switches to fullscreen display.
        Updates the window title to show fullscreen status and available
        exit methods (F11 or Escape).
        """
        if not self.is_fullscreen:
            # Save current window position and size
            self.normal_geometry = self.geometry()
            
            # Switch to fullscreen mode
            self.showFullScreen()
            self.is_fullscreen = True
            
            # Update title to show fullscreen status and exit instructions
            self.setWindowTitle('Game Library - Fullscreen (Press F11 or Esc to exit)')
    
    def exit_fullscreen(self):
        """
        Exit fullscreen mode and return to windowed display.
        
        Restores the previous window geometry if available, otherwise
        uses the default window size. Updates the window title to
        show normal mode instructions.
        """
        if self.is_fullscreen:
            # Return to normal windowed mode
            self.showNormal()
            
            # Restore previous window geometry if available
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            else:
                # Fallback to default size if no saved geometry
                self.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
                
            self.is_fullscreen = False
            
            # Restore normal window title with instructions
            self.setWindowTitle('Game Library - Press F11 for Fullscreen')
    
    def keyPressEvent(self, event):
        """
        Handle keyboard input events.
        
        Processes special key combinations for window management:
        - F11: Toggle fullscreen mode
        - Escape: Exit fullscreen mode (when in fullscreen)
        
        All other key events are passed to the parent class for
        normal processing.
        
        Args:
            event (QKeyEvent): The keyboard event to process
        """
        if event.key() == Qt.Key_F11:
            # F11 always toggles fullscreen
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape and self.is_fullscreen:
            # Escape only works when in fullscreen mode
            self.exit_fullscreen()
        else:
            # Let parent class handle all other key events
            super().keyPressEvent(event)


if __name__ == '__main__':
    """
    Direct execution entry point for testing.
    
    Allows the main window to be run directly for development and testing
    purposes. In normal operation, the application is started through main.py.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
