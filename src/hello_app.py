import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStackedWidget
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
        self.setWindowTitle('Game Library')
        
        # Set window size to a large fixed rectangle
        self.setFixedSize(1200, 800)
        
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
                        # Scale the image to stretch across about 1/3 of the screen width (400px) with reduced height (100px)
                        scaled_pixmap = pixmap.scaled(400, 100)
                        
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
        
        main_layout.addWidget(left_widget, 1)  # Left takes space
        main_layout.addWidget(self.game_details_page, 2)  # Right takes more space
        
        self.setLayout(main_layout)
    
    def on_game_clicked(self, game):
        """Handle game image click - show game details on the right"""
        self.game_details_page.update_game(game)

    def show_game_list(self):
        pass  # No longer needed since games are displayed on main page

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
