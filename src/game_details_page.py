import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from styles import (
    RIGHT_PANEL_STYLE, 
    BUTTON_STYLE, 
    GAME_IMAGE_STYLE,
    Colors, 
    Layout
)

class GameDetailsPage(QWidget):
    def __init__(self, game=None):
        super().__init__()
        self.game = game
        self.initUI()
    
    def initUI(self):
        # Apply styling
        self.setStyleSheet(RIGHT_PANEL_STYLE)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(Layout.MARGIN_LARGE, Layout.MARGIN_LARGE, Layout.MARGIN_LARGE, Layout.MARGIN_LARGE)
        main_layout.setSpacing(Layout.SPACING_LARGE)
        
        # Build the content
        self.build_ui_content(main_layout)
        
        self.setLayout(main_layout)
    
    def build_ui_content(self, layout):
        """Build the UI content for the given layout"""
        if self.game:
            # Game title
            title_label = QLabel(self.game.name)
            title_label.setFont(QFont('Segoe UI', 24, QFont.Bold))
            title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-bottom: 10px;")
            layout.addWidget(title_label)
            
            # Game image (larger version)
            self.add_game_image(layout)
            
            # Game information section
            self.add_game_info(layout)
            
            # Add stretch to push button to bottom
            layout.addStretch()
            
            # Start server button
            self.add_start_button(layout)
        else:
            # Default message when no game is selected
            welcome_label = QLabel("Select a game to view details")
            welcome_label.setFont(QFont('Segoe UI', 18))
            welcome_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; text-align: center;")
            welcome_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(welcome_label)
            layout.addStretch()
    
    def add_game_image(self, layout):
        """Add the game image to the layout"""
        try:
            # Get the directory of the current script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, self.game.image_url)
            
            # Fallback to actual filename
            if not os.path.exists(image_path):
                image_path = os.path.join(script_dir, "images", "palworld_image.jpg")
            
            if os.path.exists(image_path):
                # Create image container
                image_container = QWidget()
                image_layout = QHBoxLayout()
                image_layout.setContentsMargins(0, 0, 0, 0)
                
                # Load and scale image
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                image_label = QLabel()
                image_label.setPixmap(scaled_pixmap)
                image_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {Colors.BACKGROUND_LIGHT};
                        border: 2px solid {Colors.BORDER};
                        border-radius: {Layout.BORDER_RADIUS_LARGE}px;
                        padding: 10px;
                    }}
                """)
                image_label.setAlignment(Qt.AlignCenter)
                
                image_layout.addWidget(image_label)
                image_layout.addStretch()
                image_container.setLayout(image_layout)
                
                layout.addWidget(image_container)
        except Exception:
            pass  # Skip image if it fails to load
    
    def add_game_info(self, layout):
        """Add game information section"""
        # Info container
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        info_layout.setSpacing(Layout.SPACING_MEDIUM)
        
        # Game description
        if self.game.description and self.game.description != "No description available.":
            desc_title = QLabel("Description:")
            desc_title.setFont(QFont('Segoe UI', 14, QFont.Bold))
            desc_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-top: 10px;")
            info_layout.addWidget(desc_title)
            
            desc_label = QLabel(self.game.description)
            desc_label.setFont(QFont('Segoe UI', 12))
            desc_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; line-height: 1.4;")
            desc_label.setWordWrap(True)
            info_layout.addWidget(desc_label)
        
        # Game genre
        if self.game.genre and self.game.genre != "Unknown":
            genre_title = QLabel("Genre:")
            genre_title.setFont(QFont('Segoe UI', 14, QFont.Bold))
            genre_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-top: 10px;")
            info_layout.addWidget(genre_title)
            
            genre_label = QLabel(self.game.genre)
            genre_label.setFont(QFont('Segoe UI', 12))
            genre_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
            info_layout.addWidget(genre_label)
        
        # Platforms
        if self.game.platforms:
            platforms_title = QLabel("Platforms:")
            platforms_title.setFont(QFont('Segoe UI', 14, QFont.Bold))
            platforms_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-top: 10px;")
            info_layout.addWidget(platforms_title)
            
            platforms_text = ", ".join(self.game.platforms)
            platforms_label = QLabel(platforms_text)
            platforms_label.setFont(QFont('Segoe UI', 12))
            platforms_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
            platforms_label.setWordWrap(True)
            info_layout.addWidget(platforms_label)
        
        info_widget.setLayout(info_layout)
        layout.addWidget(info_widget)
    
    def add_start_button(self, layout):
        """Add the start dedicated server button"""
        # Button container to control positioning
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, Layout.MARGIN_MEDIUM, 0, 0)
        
        start_button = QPushButton("Start Dedicated Server")
        start_button.setFont(QFont('Segoe UI', 14, QFont.Bold))
        start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: {Layout.BORDER_RADIUS_SMALL}px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                min-width: 200px;
            }}
            QPushButton:hover {{
                background-color: #218838;
            }}
            QPushButton:pressed {{
                background-color: #1e7e34;
            }}
        """)
        
        # Connect button (no functionality yet)
        start_button.clicked.connect(self.start_server)
        
        button_layout.addWidget(start_button)
        button_layout.addStretch()
        button_container.setLayout(button_layout)
        
        layout.addWidget(button_container)
    
    def start_server(self):
        """Open the dedicated server setup window"""
        if self.game and self.game.name.lower() == "palworld":
            # Import here to avoid circular imports
            from palworld_setup_window import PalworldServerSetupWindow
            
            # Create and show the setup window
            self.setup_window = PalworldServerSetupWindow(self.game)
            self.setup_window.show()
        else:
            print(f"Server setup not yet implemented for {self.game.name if self.game else 'Unknown Game'}")
            # Could show a message box here for other games
    
    def update_game(self, game):
        """Update the page with a new game"""
        self.game = game
        
        # Clear the current layout contents
        layout = self.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            # Create layout if it doesn't exist
            layout = QVBoxLayout()
            self.setLayout(layout)
        
        # Rebuild the UI with the new game
        self.build_ui_content(layout)
