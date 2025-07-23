import os
import platform
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
from styles import (
    RIGHT_PANEL_STYLE, 
    BUTTON_STYLE, 
    GAME_IMAGE_STYLE,
    Colors, 
    Layout
)
from utils.server_detection import get_server_status_info

class GameDetailsPage(QWidget):
    def __init__(self, game=None):
        super().__init__()
        self.game = game
        self.server_status_widget = None
        self.status_timer = None
        self.initUI()
        self.setup_status_timer()
    
    def initUI(self):
        # Apply styling
        self.setStyleSheet(RIGHT_PANEL_STYLE)
        
        # Create a scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {Colors.BACKGROUND_LIGHT};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {Colors.BORDER};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {Colors.TEXT_SECONDARY};
            }}
        """)
        
        # Content widget that will go inside the scroll area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(Layout.MARGIN_LARGE, Layout.MARGIN_LARGE, Layout.MARGIN_LARGE, Layout.MARGIN_LARGE)
        self.content_layout.setSpacing(Layout.SPACING_LARGE)
        
        # Build the content
        self.build_ui_content(self.content_layout)
        
        self.content_widget.setLayout(self.content_layout)
        scroll_area.setWidget(self.content_widget)
        
        # Main layout just contains the scroll area
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
    
    def build_ui_content(self, layout):
        """Build the UI content for the given layout"""
        if self.game:
            # Game title
            title_label = QLabel(self.game.name)
            title_label.setFont(QFont('Segoe UI', 28, QFont.Bold))
            title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-bottom: 15px;")
            layout.addWidget(title_label)
            
            # Game image (larger version)
            self.add_game_image(layout)
            
            # Game information section
            self.add_game_info(layout)
            
            # Server status section
            self.add_server_status(layout)
            
            # Start server button (no stretch needed with scrolling)
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
                scaled_pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
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
            desc_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
            desc_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-top: 15px;")
            info_layout.addWidget(desc_title)
            
            desc_label = QLabel(self.game.description)
            desc_label.setFont(QFont('Segoe UI', 14))
            desc_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; line-height: 1.5;")
            desc_label.setWordWrap(True)
            info_layout.addWidget(desc_label)
        
        # Game genre
        if self.game.genre and self.game.genre != "Unknown":
            genre_title = QLabel("Genre:")
            genre_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
            genre_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-top: 15px;")
            info_layout.addWidget(genre_title)
            
            genre_label = QLabel(self.game.genre)
            genre_label.setFont(QFont('Segoe UI', 14))
            genre_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
            info_layout.addWidget(genre_label)
        
        # Platforms
        if self.game.platforms:
            platforms_title = QLabel("Platforms:")
            platforms_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
            platforms_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-top: 15px;")
            info_layout.addWidget(platforms_title)
            
            platforms_text = ", ".join(self.game.platforms)
            platforms_label = QLabel(platforms_text)
            platforms_label.setFont(QFont('Segoe UI', 14))
            platforms_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
            platforms_label.setWordWrap(True)
            info_layout.addWidget(platforms_label)
        
        info_widget.setLayout(info_layout)
        layout.addWidget(info_widget)
    
    def add_start_button(self, layout):
        """Add the start server button (setup or direct start based on installation status)"""
        # Button container to control positioning
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, Layout.MARGIN_MEDIUM, 0, 0)
        
        # Check if server files are already installed
        if self.game and self.is_server_installed(self.game.name):
            # Check if server is currently running
            server_info = get_server_status_info(self.game.name)
            is_running = server_info.get('is_running', False)
            
            if is_running:
                # Server is running - show disabled button
                start_button = QPushButton("Server Running")
                start_button.setFont(QFont('Segoe UI', 16, QFont.Bold))
                start_button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #6c757d;
                        color: white;
                        border: none;
                        border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
                        padding: 20px 40px;
                        font-size: 18px;
                        font-weight: bold;
                        min-width: 250px;
                        min-height: 60px;
                    }}
                    QPushButton:disabled {{
                        background-color: #6c757d;
                        color: #adb5bd;
                    }}
                """)
                start_button.setEnabled(False)
                start_button.setToolTip("Server is already running")
            else:
                # Server is installed but not running - show start button
                start_button = QPushButton("Start Server")
                start_button.setFont(QFont('Segoe UI', 16, QFont.Bold))
                start_button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #28a745;
                        color: white;
                        border: none;
                        border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
                        padding: 20px 40px;
                        font-size: 18px;
                        font-weight: bold;
                        min-width: 250px;
                        min-height: 60px;
                    }}
                    QPushButton:hover {{
                        background-color: #218838;
                    }}
                    QPushButton:pressed {{
                        background-color: #1e7e34;
                    }}
                """)
                start_button.clicked.connect(self.start_server_directly)
        else:
            # Server needs setup - show setup button
            start_button = QPushButton("Start Dedicated Server Setup")
            start_button.setFont(QFont('Segoe UI', 16, QFont.Bold))
            start_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
                    padding: 20px 40px;
                    font-size: 18px;
                    font-weight: bold;
                    min-width: 250px;
                    min-height: 60px;
                }}
                QPushButton:hover {{
                    background-color: #0056b3;
                }}
                QPushButton:pressed {{
                    background-color: #004085;
                }}
            """)
            start_button.clicked.connect(self.start_server_setup)
        
        # Store reference to the button for status updates
        self.start_button = start_button
        
        button_layout.addWidget(start_button)
        button_layout.addStretch()
        button_container.setLayout(button_layout)
        
        layout.addWidget(button_container)
    
    def start_server_setup(self):
        """Open the dedicated server setup window"""
        if self.game and self.game.name.lower() == "palworld":
            # Import here to avoid circular imports
            from setup_windows.palworld_setup_window import PalworldServerSetupWindow
            
            # Create and show the setup window
            self.setup_window = PalworldServerSetupWindow(self.game)
            self.setup_window.show()
        else:
            print(f"Server setup not yet implemented for {self.game.name if self.game else 'Unknown Game'}")
    
    def start_server_directly(self):
        """Start the server directly without setup (when files are already installed)"""
        if self.game and self.game.name.lower() == "palworld":
            try:
                # Import the server start function
                import sys
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                sys.path.insert(0, os.path.join(parent_dir, "scripts"))
                from scripts.palworld_server_startup_script import start_palworld_server
                
                print("Starting Palworld server...")
                success = start_palworld_server()
                if success:
                    print("✅ Palworld server started successfully!")
                else:
                    print("❌ Failed to start Palworld server")
            except Exception as e:
                print(f"❌ Error starting server: {str(e)}")
        else:
            print(f"Direct server start not yet implemented for {self.game.name if self.game else 'Unknown Game'}")

    def start_server(self):
        """Legacy method - redirects to appropriate start method"""
        if self.game and self.is_server_installed(self.game.name):
            self.start_server_directly()
        else:
            self.start_server_setup()
    
    def update_game(self, game):
        """Update the page with a new game"""
        self.game = game
        
        # Clear the current content layout contents
        if hasattr(self, 'content_layout'):
            while self.content_layout.count():
                child = self.content_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Rebuild the UI with the new game
            self.build_ui_content(self.content_layout)
        else:
            # Fallback to reinitialize if content_layout doesn't exist
            self.initUI()
        
        # Restart the status timer for the new game
        self.setup_status_timer()
    
    def is_server_installed(self, game_name):
        """Check if the server files are already installed for the given game"""
        if game_name.lower() == "palworld":
            return self.is_palworld_server_installed()
        # Add more games here as needed
        return False
    
    def is_palworld_server_installed(self):
        """Check if Palworld server files are installed"""
        # Use the same paths as the startup script
        if platform.system().lower() == 'windows':
            steamcmd_dir = os.path.expandvars(r'%USERPROFILE%\SteamCMD')
            server_dir = os.path.expandvars(r'%USERPROFILE%\Steam\steamapps\common\Palworld Dedicated Server')
        else:
            steamcmd_dir = os.path.expanduser('~/SteamCMD')
            server_dir = os.path.expanduser('~/Steam/steamapps/common/Palworld Dedicated Server')
        
        # Check if SteamCMD is installed
        steamcmd_exe = os.path.join(steamcmd_dir, 'steamcmd.exe' if platform.system().lower() == 'windows' else 'steamcmd.sh')
        steamcmd_installed = os.path.exists(steamcmd_exe)
        
        # Check if Palworld server is installed
        pal_exe = os.path.join(server_dir, 'PalServer.exe' if platform.system().lower() == 'windows' else 'PalServer')
        server_installed = os.path.exists(pal_exe)
        
        return steamcmd_installed and server_installed

    def add_server_status(self, layout):
        """Add server status section"""
        self.server_status_widget = QWidget()
        status_layout = QVBoxLayout()
        status_layout.setSpacing(Layout.SPACING_MEDIUM)
        
        # Server Status Title
        status_title = QLabel("Server Status:")
        status_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        status_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-top: 20px;")
        status_layout.addWidget(status_title)
        
        # Status container with border
        status_container = QWidget()
        status_container.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BACKGROUND_LIGHT};
                border: 2px solid {Colors.BORDER};
                border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
                padding: 25px;
                margin: 10px 0px;
            }}
        """)
        
        self.status_content_layout = QVBoxLayout()
        self.status_content_layout.setSpacing(Layout.SPACING_MEDIUM)
        
        # Initialize with "Checking..." message
        self.status_checking_label = QLabel("Checking server status...")
        self.status_checking_label.setFont(QFont('Segoe UI', 14))
        self.status_checking_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self.status_content_layout.addWidget(self.status_checking_label)
        
        status_container.setLayout(self.status_content_layout)
        status_layout.addWidget(status_container)
        
        self.server_status_widget.setLayout(status_layout)
        layout.addWidget(self.server_status_widget)
        
        # Update status immediately
        self.update_server_status()

    def update_server_status(self):
        """Update the server status information"""
        if not self.game:
            return
            
        try:
            status_info = get_server_status_info(self.game.name)
            
            # Clear existing status content
            while self.status_content_layout.count():
                child = self.status_content_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            if status_info['is_running']:
                # Server is running - show green status
                running_label = QLabel("🟢 Server is RUNNING")
                running_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
                running_label.setStyleSheet(f"color: #28a745; margin-bottom: 15px;")
                self.status_content_layout.addWidget(running_label)
                
                # Connection information
                if status_info['local_ip'] != "Unable to determine":
                    local_info = QLabel(f"Local IP: {status_info['local_ip']}:{status_info['port']}")
                    local_info.setFont(QFont('Segoe UI', 13))
                    local_info.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-family: 'Consolas', 'Courier New', monospace;")
                    self.status_content_layout.addWidget(local_info)
                
                if status_info['public_ip'] != "Unable to determine":
                    public_info = QLabel(f"Public IP: {status_info['public_ip']}:{status_info['port']}")
                    public_info.setFont(QFont('Segoe UI', 13))
                    public_info.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-family: 'Consolas', 'Courier New', monospace;")
                    self.status_content_layout.addWidget(public_info)
                    
                    connection_note = QLabel("Share the Public IP with friends to connect from outside your network")
                    connection_note.setFont(QFont('Segoe UI', 12))
                    connection_note.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-style: italic; margin-top: 8px;")
                    connection_note.setWordWrap(True)
                    self.status_content_layout.addWidget(connection_note)
                
            else:
                # Server is not running - show red status
                not_running_label = QLabel("🔴 Server is NOT RUNNING")
                not_running_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
                not_running_label.setStyleSheet(f"color: #dc3545;")
                self.status_content_layout.addWidget(not_running_label)
                
                help_text = QLabel("Use the 'Start Dedicated Server' button below to set up and start your server")
                help_text.setFont(QFont('Segoe UI', 12))
                help_text.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-style: italic;")
                help_text.setWordWrap(True)
                self.status_content_layout.addWidget(help_text)
                
        except Exception as e:
            # Error occurred - show error status
            error_label = QLabel("⚠️ Error checking server status")
            error_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
            error_label.setStyleSheet(f"color: #ffc107;")
            self.status_content_layout.addWidget(error_label)
            
            error_detail = QLabel(f"Error: {str(e)}")
            error_detail.setFont(QFont('Segoe UI', 10))
            error_detail.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
            error_detail.setWordWrap(True)
            self.status_content_layout.addWidget(error_detail)
        
        # Update button state based on server status
        self.update_button_state()

    def update_button_state(self):
        """Update the start button based on current server status"""
        if not hasattr(self, 'start_button') or not self.start_button or not self.game:
            return
            
        # Only update if server files are installed (otherwise it's always the setup button)
        if self.is_server_installed(self.game.name):
            try:
                status_info = get_server_status_info(self.game.name)
                is_running = status_info.get('is_running', False)
                
                if is_running:
                    # Server is running - disable button
                    self.start_button.setText("Server Running")
                    self.start_button.setEnabled(False)
                    self.start_button.setToolTip("Server is already running")
                    self.start_button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: #6c757d;
                            color: white;
                            border: none;
                            border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
                            padding: 20px 40px;
                            font-size: 18px;
                            font-weight: bold;
                            min-width: 250px;
                            min-height: 60px;
                        }}
                        QPushButton:disabled {{
                            background-color: #6c757d;
                            color: #adb5bd;
                        }}
                    """)
                else:
                    # Server is not running - enable button
                    self.start_button.setText("Start Server")
                    self.start_button.setEnabled(True)
                    self.start_button.setToolTip("")
                    self.start_button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: #28a745;
                            color: white;
                            border: none;
                            border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
                            padding: 20px 40px;
                            font-size: 18px;
                            font-weight: bold;
                            min-width: 250px;
                            min-height: 60px;
                        }}
                        QPushButton:hover {{
                            background-color: #218838;
                        }}
                        QPushButton:pressed {{
                            background-color: #1e7e34;
                        }}
                    """)
                    # Reconnect the click handler (in case it was disconnected)
                    try:
                        self.start_button.clicked.disconnect()
                    except TypeError:
                        # No connections to disconnect
                        pass
                    self.start_button.clicked.connect(self.start_server_directly)
                    
            except Exception as e:
                print(f"Error updating button state: {e}")

    def setup_status_timer(self):
        """Set up timer to refresh server status every 10 seconds"""
        if self.status_timer:
            self.status_timer.stop()
            
        if self.game:
            self.status_timer = QTimer()
            self.status_timer.timeout.connect(self.update_server_status)
            self.status_timer.start(10000)  # Update every 10 seconds
