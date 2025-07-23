import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStackedWidget, QShortcut
from game_list_page import GameListPage
from game import Game
from game_details_page import GameDetailsPage
from static.games_list import GAMES_LIST
from styles import (
    MAIN_WINDOW_STYLE, 
    LEFT_PANEL_STYLE, 
    RIGHT_PANEL_STYLE, 
    GAME_IMAGE_STYLE,
    Layout
)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Game Library - Press F11 for Fullscreen')
        
        # Set up dynamic resizable window
        self.setMinimumSize(1200, 800)  # Minimum size for usability
        self.resize(1600, 1000)  # Default starting size
        
        # Enable window features
        self.setWindowState(self.windowState() & ~Qt.WindowMaximized)  # Start not maximized
        
        # Set up fullscreen toggle (F11 key)
        self.fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        self.fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
        
        # Set up escape key to exit fullscreen
        self.escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.escape_shortcut.activated.connect(self.exit_fullscreen)
        
        # Track fullscreen state
        self.is_fullscreen = False
        self.normal_geometry = None
        
        # Apply modern dark theme styling
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # Main layout with horizontal arrangement
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side for game images (starting from top left)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(Layout.MARGIN_LARGE, Layout.MARGIN_LARGE, Layout.MARGIN_LARGE, Layout.MARGIN_LARGE)
        left_layout.setSpacing(Layout.SPACING_LARGE)
        
        # Create Game objects and display their images
        self.games = [Game(name) for name in GAMES_LIST]
        for game in self.games:
            # Construct the proper path to the image file
            if game.image_url:
                # Get the directory of the current script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(script_dir, game.image_url)
                
                # Also try the actual filename that exists
                if not os.path.exists(image_path):
                    image_path = os.path.join(script_dir, "images", "palworld_image.jpg")
                
                if os.path.exists(image_path):
                    try:
                        # Load image from local file
                        pixmap = QPixmap(image_path)
                        # Scale the image larger to fit the bigger window (500px wide, 120px tall)
                        scaled_pixmap = pixmap.scaled(500, 120)
                        
                        # Create clickable image label
                        image_label = QLabel()
                        image_label.setPixmap(scaled_pixmap)
                        image_label.setStyleSheet(GAME_IMAGE_STYLE)
                        image_label.setScaledContents(True)
                        
                        # Make image clickable (cursor is handled differently in PyQt5)
                        image_label.setCursor(Qt.PointingHandCursor)
                        image_label.mousePressEvent = lambda event, g=game: self.on_game_clicked(g)
                        
                        left_layout.addWidget(image_label)
                    except Exception:
                        # If image fails to load, skip this game
                        pass
                else:
                    # If no image path or file doesn't exist, skip this game
                    pass
            else:
                # If no image_url at all, skip this game
                pass
        
        # Add stretch at the end to push content to top
        left_layout.addStretch()
        
        # Right side for game details
        self.game_details_page = GameDetailsPage()
        
        # Add layouts to main layout
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setStyleSheet(LEFT_PANEL_STYLE)
        
        main_layout.addWidget(left_widget, 1)  # Left takes 1 part
        main_layout.addWidget(self.game_details_page, 3)  # Right takes 3 parts (more space)
        
        self.setLayout(main_layout)
    
    def on_game_clicked(self, game):
        """Handle game image click - show game details on the right"""
        self.game_details_page.update_game(game)

    def show_game_list(self):
        pass  # No longer needed since games are displayed on main page
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()
    
    def enter_fullscreen(self):
        """Enter fullscreen mode"""
        if not self.is_fullscreen:
            # Save current geometry
            self.normal_geometry = self.geometry()
            
            # Enter fullscreen
            self.showFullScreen()
            self.is_fullscreen = True
            
            # Update window title to show fullscreen status
            self.setWindowTitle('Game Library - Fullscreen (Press F11 or Esc to exit)')
    
    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        if self.is_fullscreen:
            # Exit fullscreen
            self.showNormal()
            
            # Restore previous geometry if available
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            else:
                self.resize(1600, 1000)  # Default size
                
            self.is_fullscreen = False
            
            # Restore normal window title
            self.setWindowTitle('Game Library - Press F11 for Fullscreen')
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape and self.is_fullscreen:
            self.exit_fullscreen()
        else:
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
