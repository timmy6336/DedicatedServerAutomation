"""
Game List Page - Legacy Implementation

This module provides a simple list-based interface for browsing supported games.
While currently not actively used in the main application (which uses an image-based
selection system), this page serves as a reference implementation for future
list-based features or alternative game browsing interfaces.

Features:
- Dynamic game loading from centralized game list
- Game image retrieval and display with error handling
- Vertical scrolling layout for multiple games
- Integration with Game data model

Note: The main application currently uses hello_app.py for game selection
with an image-based interface instead of this list-based approach.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
import requests
from static.games_list import GAMES_LIST
from game import Game

class GameListPage(QWidget):
    """
    Legacy game list interface showing games in a vertical list format.
    
    This widget displays all supported games in a simple list format with
    game names and images (when available). Currently serves as a reference
    implementation for alternative game browsing interfaces.
    
    Attributes:
        games (list): List of Game objects loaded from the centralized game registry
    """
    
    def __init__(self):
        """
        Initialize the game list page.
        
        Creates the widget and immediately sets up the UI with all available games.
        """
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Initialize the user interface for the game list page.
        
        Creates a vertical layout containing:
        - Header label indicating this is a games list
        - Dynamic list of game entries with names and images
        - Error handling for image loading failures
        
        The method loads all games from the centralized game registry,
        creates Game objects for each entry, and displays them with
        their associated metadata and images when available.
        """
        self.setWindowTitle('Game List')
        layout = QVBoxLayout()
        
        # Add header label
        label = QLabel('Games:')
        layout.addWidget(label)
        
        # Create Game objects for each entry from the centralized registry
        self.games = [Game(name) for name in GAMES_LIST]
        
        # Add each game to the layout with name and image
        for game in self.games:
            game_layout = QVBoxLayout()
            
            # Add game name label
            game_label = QLabel(str(game))
            game_layout.addWidget(game_label)
            
            # Attempt to load and display game image
            if game.image_url:
                try:
                    # Download image data from the game's image URL
                    response = requests.get(game.image_url)
                    response.raise_for_status()
                    image_data = response.content
                    
                    # Create and display the image
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)
                    image_label = QLabel()
                    image_label.setPixmap(pixmap)
                    game_layout.addWidget(image_label)
                except Exception as e:
                    # Display error message if image loading fails
                    error_label = QLabel(f"Image load error: {e}")
                    game_layout.addWidget(error_label)
            
            # Add this game's layout to the main layout
            layout.addLayout(game_layout)
        
        self.setLayout(layout)
