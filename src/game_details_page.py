# ============================================================================
# GAME DETAILS PAGE CONFIGURATION CONSTANTS
# ============================================================================

# Font family constants
FONT_FAMILY_UI = 'Segoe UI'         # Primary UI font family

# Font sizing constants
GAME_TITLE_FONT_SIZE = 28           # Font size for game title in details page
GAME_TITLE_MARGIN_BOTTOM = 15       # Bottom margin for game title in pixels
WELCOME_MESSAGE_FONT_SIZE = 18      # Font size for welcome message when no game selected
DESCRIPTION_TITLE_FONT_SIZE = 16    # Font size for section titles in game details
DESCRIPTION_TEXT_FONT_SIZE = 14     # Font size for description and other text

# Image sizing constants (details page)
DETAIL_IMAGE_WIDTH = 400            # Width for large game image in details page
DETAIL_IMAGE_HEIGHT = 300           # Height for large game image in details page
DETAIL_IMAGE_BORDER_WIDTH = 2       # Border width for detail images in pixels
DETAIL_IMAGE_PADDING = 10           # Padding around detail images in pixels

# Scrollbar styling constants
SCROLLBAR_WIDTH = 14                # Width of custom scrollbars in pixels
SCROLLBAR_BORDER_RADIUS = 7         # Border radius for scrollbars in pixels
SCROLLBAR_MIN_HANDLE_HEIGHT = 30    # Minimum height for scrollbar handle in pixels

# Layout margin constants (using zero for edge-to-edge layouts)
NO_MARGINS_ALL_SIDES = 0           # Zero margins for all sides of layout

# Section spacing constants
SECTION_TOP_MARGIN = 15             # Top margin for section titles in pixels

import os
import platform
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from styles import (
    RIGHT_PANEL_STYLE, 
    BUTTON_PRIMARY_STYLE,
    BUTTON_SECONDARY_STYLE, 
    GAME_IMAGE_STYLE,
    Colors, 
    Layout
)
from utils.server_detection import get_server_status_info, get_server_status_info_fast

class ServerStatusWorker(QThread):
    """Worker thread for checking server status without blocking UI"""
    status_ready = pyqtSignal(dict)  # Emits server status info when ready
    fast_status_ready = pyqtSignal(dict)  # Emits fast local status first
    
    def __init__(self, game_name, fast_mode=False):
        super().__init__()
        self.game_name = game_name
        self.fast_mode = fast_mode
    
    def run(self):
        """Run server status check in background thread"""
        try:
            if self.fast_mode:
                # First, get fast local status without public IP
                fast_status = get_server_status_info_fast(self.game_name)
                self.fast_status_ready.emit(fast_status)
                
                # Then get full status with public IP
                full_status = get_server_status_info(self.game_name)
                self.status_ready.emit(full_status)
            else:
                # Get full status directly
                status_info = get_server_status_info(self.game_name)
                self.status_ready.emit(status_info)
                
        except Exception as e:
            # Emit a minimal status if there's an error
            error_status = {
                'is_running': False,
                'local_ip': "Unable to determine",
                'public_ip': "Unable to determine", 
                'port': None,
                'connection_string': None,
                'error': str(e)
            }
            self.status_ready.emit(error_status)

class GameDetailsPage(QWidget):
    def __init__(self, game=None):
        super().__init__()
        self.game = game
        self.server_status_widget = None
        self.status_timer = None
        
        # Thread management for server status checking
        self.status_worker = None
        self.refresh_status_worker = None
        
        self.initUI()
        self.setup_status_timer()
    
    def cleanup_status_worker(self):
        """Safely cleanup and stop any running status worker thread"""
        if self.status_worker and self.status_worker.isRunning():
            self.status_worker.quit()
            self.status_worker.wait(1000)  # Wait up to 1 second for clean shutdown
            if self.status_worker.isRunning():
                self.status_worker.terminate()  # Force terminate if needed
                self.status_worker.wait()
        self.status_worker = None
    
    def cleanup_refresh_worker(self):
        """Safely cleanup and stop any running refresh worker thread"""
        if self.refresh_status_worker and self.refresh_status_worker.isRunning():
            self.refresh_status_worker.quit()
            self.refresh_status_worker.wait(1000)  # Wait up to 1 second for clean shutdown
            if self.refresh_status_worker.isRunning():
                self.refresh_status_worker.terminate()  # Force terminate if needed
                self.refresh_status_worker.wait()
        self.refresh_status_worker = None
    
    def cleanup_all_threads(self):
        """Clean up all running threads before destroying the widget"""
        self.cleanup_status_worker()
        self.cleanup_refresh_worker()
    
    def closeEvent(self, event):
        """Handle widget close event and clean up threads"""
        self.cleanup_all_threads()
        super().closeEvent(event)
    
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
                background: {Colors.SILVER};
                width: {SCROLLBAR_WIDTH}px;
                border-radius: {SCROLLBAR_BORDER_RADIUS}px;
                margin: {NO_MARGINS_ALL_SIDES};
            }}
            QScrollBar::handle:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 {Colors.PRIMARY_BLUE}, 
                            stop:1 {Colors.SECONDARY_BLUE});
                border-radius: {SCROLLBAR_BORDER_RADIUS}px;
                min-height: {SCROLLBAR_MIN_HANDLE_HEIGHT}px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Colors.SECONDARY_BLUE};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
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
        main_layout.setContentsMargins(NO_MARGINS_ALL_SIDES, NO_MARGINS_ALL_SIDES, NO_MARGINS_ALL_SIDES, NO_MARGINS_ALL_SIDES)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
    
    def build_ui_content(self, layout):
        """Build the UI content for the given layout"""
        if self.game:
            # Game title
            title_label = QLabel(self.game.name)
            title_label.setFont(QFont(FONT_FAMILY_UI, GAME_TITLE_FONT_SIZE, QFont.Bold))
            title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-bottom: {GAME_TITLE_MARGIN_BOTTOM}px;")
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
            welcome_label.setFont(QFont(FONT_FAMILY_UI, WELCOME_MESSAGE_FONT_SIZE))
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
                image_layout.setContentsMargins(NO_MARGINS_ALL_SIDES, NO_MARGINS_ALL_SIDES, NO_MARGINS_ALL_SIDES, NO_MARGINS_ALL_SIDES)
                
                # Load and scale image
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(DETAIL_IMAGE_WIDTH, DETAIL_IMAGE_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                image_label = QLabel()
                image_label.setPixmap(scaled_pixmap)
                image_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {Colors.SILVER_LIGHT};
                        border: {DETAIL_IMAGE_BORDER_WIDTH}px solid {Colors.SILVER};
                        border-radius: {Layout.BORDER_RADIUS_LARGE}px;
                        padding: {DETAIL_IMAGE_PADDING}px;
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
            desc_title.setFont(QFont(FONT_FAMILY_UI, DESCRIPTION_TITLE_FONT_SIZE, QFont.Bold))
            desc_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-top: {SECTION_TOP_MARGIN}px;")
            info_layout.addWidget(desc_title)
            
            desc_label = QLabel(self.game.description)
            desc_label.setFont(QFont(FONT_FAMILY_UI, DESCRIPTION_TEXT_FONT_SIZE))
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
            # Create placeholder button first (will be updated when status check completes)
            self.start_button = QPushButton("Checking Server Status...")
            self.start_button.setFont(QFont('Segoe UI', 16, QFont.Bold))
            self.start_button.setStyleSheet(f"""
                {BUTTON_SECONDARY_STYLE}
                QPushButton {{
                    min-width: 250px;
                    min-height: 60px;
                    font-size: 18px;
                }}
            """)
            self.start_button.setEnabled(False)
            
            # Start async server status check with fast mode for immediate feedback
            self.cleanup_status_worker()  # Clean up any existing worker
            
            self.status_worker = ServerStatusWorker(self.game.name, fast_mode=True)
            self.status_worker.fast_status_ready.connect(self.on_fast_server_status_ready)
            self.status_worker.status_ready.connect(self.on_server_status_ready)
            self.status_worker.start()
        else:
            # Server needs setup - show setup button
            self.start_button = QPushButton("Start Dedicated Server Setup")
            self.start_button.setFont(QFont('Segoe UI', 16, QFont.Bold))
            self.start_button.setStyleSheet(f"""
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
            self.start_button.clicked.connect(self.start_server_setup)
        
        # Button is already stored as self.start_button
        
        button_layout.addWidget(self.start_button)
        
        # Add delete button if server is installed
        if self.game and self.is_server_installed(self.game.name):
            delete_button = QPushButton("Uninstall Server")
            delete_button.setFont(QFont('Segoe UI', 14, QFont.Bold))
            delete_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
                    padding: 15px 30px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 180px;
                    min-height: 50px;
                    margin-left: 20px;
                }}
                QPushButton:hover {{
                    background-color: #c82333;
                }}
                QPushButton:pressed {{
                    background-color: #bd2130;
                }}
            """)
            delete_button.clicked.connect(self.uninstall_server)
            delete_button.setToolTip("Remove server files and port forwarding (keeps SteamCMD)")
            button_layout.addWidget(delete_button)
        
        button_layout.addStretch()
        button_container.setLayout(button_layout)
        
        layout.addWidget(button_container)
    
    def on_fast_server_status_ready(self, server_info):
        """Handle fast server status check completion with local info only"""
        # Update button immediately with local status
        if hasattr(self, 'start_button'):
            is_running = server_info.get('is_running', False)
            if is_running:
                self.start_button.setText("Server Running")
                self.start_button.setStyleSheet(f"""
                    {BUTTON_SECONDARY_STYLE}
                    QPushButton {{
                        min-width: 250px;
                        min-height: 60px;
                        font-size: 18px;
                    }}
                """)
                self.start_button.setEnabled(False)
            else:
                self.start_button.setText("Start Server")
                self.start_button.setStyleSheet(f"""
                    {BUTTON_PRIMARY_STYLE}
                    QPushButton {{
                        min-width: 250px;
                        min-height: 60px;
                        font-size: 18px;
                    }}
                """)
                self.start_button.setEnabled(True)
    
    def on_server_status_ready(self, server_info):
        """Handle server status check completion and update button accordingly"""
        if not hasattr(self, 'start_button'):
            return  # Button may have been removed
            
        is_running = server_info.get('is_running', False)
        
        if is_running:
            # Server is running - show disabled button
            self.start_button.setText("Server Running")
            self.start_button.setStyleSheet(f"""
                {BUTTON_SECONDARY_STYLE}
                QPushButton {{
                    min-width: 250px;
                    min-height: 60px;
                    font-size: 18px;
                }}
            """)
            self.start_button.setEnabled(False)
            self.start_button.setToolTip("Server is already running")
        else:
            # Server is installed but not running - show appropriate start button
            if self.game and self.game.name.lower() == "valheim":
                self.start_button.setText("Start Server")
                button_tooltip = "Start the Valheim server"
            else:
                self.start_button.setText("Start Server")
                button_tooltip = "Start the server with saved settings"
            
            self.start_button.setStyleSheet(f"""
                {BUTTON_PRIMARY_STYLE}
                QPushButton {{
                    min-width: 250px;
                    min-height: 60px;
                    font-size: 18px;
                    background: {Colors.SUCCESS};
                }}
                QPushButton:hover {{
                    background: #218838;
                }}
                QPushButton:pressed {{
                    background: #1e7e34;
                }}
            """)
            self.start_button.setEnabled(True)
            self.start_button.setToolTip(button_tooltip)
            
            # Connect the appropriate action
            try:
                self.start_button.clicked.disconnect()  # Remove any existing connections
            except TypeError:
                pass  # No connections to disconnect
            self.start_button.clicked.connect(self.start_server_directly)
    
    def start_server_setup(self):
        """Open the dedicated server setup window"""
        if self.game and self.game.name.lower() == "palworld":
            # Import here to avoid circular imports
            from setup_windows.palworld_setup_window import PalworldServerSetupWindow
            
            # Create and show the setup window
            self.setup_window = PalworldServerSetupWindow(self.game)
            self.setup_window.show()
        elif self.game and self.game.name.lower() == "valheim":
            # Import here to avoid circular imports
            from setup_windows.valheim_setup_window import ValheimServerSetupWindow
            # Create and show the Valheim setup window
            self.setup_window = ValheimServerSetupWindow(self.game)
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
        elif self.game and self.game.name.lower() == "valheim":
            try:
                # Import the Valheim configuration dialog and server start function
                import sys
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                sys.path.insert(0, os.path.join(parent_dir, "scripts"))
                sys.path.insert(0, os.path.join(parent_dir, "utils"))
                sys.path.insert(0, os.path.join(parent_dir, "setup_windows"))
                
                from setup_windows.valheim_setup_window import ValheimConfigDialog
                from scripts.valheim_server_startup_script import start_valheim_server
                from utils.config_manager import config_manager
                
                print("Opening Valheim server configuration...")
                
                # Show configuration dialog first
                config_dialog = ValheimConfigDialog(self)
                if config_dialog.exec_() == config_dialog.Accepted:
                    # User accepted configuration, get the settings
                    config = config_dialog.get_config()
                    print("📂 Using configured server settings")
                    print(f"🏰 Server: {config.get('server_name', 'Valheim Server')}")
                    print(f"🗺️ World: {config.get('world_name', 'DedicatedWorld')}")
                    print(f"🌐 Port: {config.get('port', 2456)}")
                    print("Starting Valheim server...")
                    
                    success = start_valheim_server(
                        world_name=config.get('world_name', 'DedicatedWorld'),
                        server_name=config.get('server_name', 'Valheim Server'), 
                        password=config.get('password', 'valheim123'),
                        public_server=config.get('public_server', True),
                        port=config.get('port', 2456)
                    )
                    if success:
                        print("✅ Valheim server started successfully!")
                        print("🏰 Your Viking realm is now active!")
                        print(f"🔒 Server password: {config.get('password', 'valheim123')}")
                    else:
                        print("❌ Failed to start Valheim server")
                else:
                    print("⏹️ Server start cancelled by user")
            except Exception as e:
                print(f"❌ Error starting server: {str(e)}")
        else:
            print(f"Direct server start not yet implemented for {self.game.name if self.game else 'Unknown Game'}")

    def uninstall_server(self):
        """Uninstall the server and SteamCMD with confirmation dialog"""
        if not self.game:
            return
            
        # Show confirmation dialog
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 
            'Confirm Uninstallation',
            f'Are you sure you want to uninstall the {self.game.name} server?\n\n'
            'This will remove:\n'
            '• All server files\n'
            '• UPnP port forwarding rules\n\n'
            'Note: SteamCMD will be kept for future server installations.\n\n'
            'This action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        try:
            if self.game.name.lower() == "palworld":
                # Import the uninstall functions
                import sys
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                sys.path.insert(0, os.path.join(parent_dir, "scripts"))
                from scripts.palworld_server_startup_script import (
                    uninstall_palworld_server,
                    remove_port_forward_rule
                )
                
                print(f"Uninstalling {self.game.name} server...")
                
                # Remove port forwarding first
                try:
                    if remove_port_forward_rule():
                        print("✅ Port forwarding rules removed")
                    else:
                        print("ℹ️ No port forwarding rules to remove")
                except Exception as e:
                    print(f"⚠️ Failed to remove port forwarding: {e}")
                
                # Uninstall server files
                if uninstall_palworld_server():
                    print("✅ Palworld server files removed")
                else:
                    print("⚠️ Failed to remove server files")
                
                print(f"🗑️ {self.game.name} server uninstallation completed")
                print("ℹ️ SteamCMD has been kept for future server installations")
                
                # Refresh the UI to reflect the changes
                self.update_game(self.game)
                
                # Show success message
                QMessageBox.information(
                    self,
                    'Uninstallation Complete',
                    f'{self.game.name} server has been successfully uninstalled.\n\n'
                    'Server files and port forwarding rules have been removed.\n'
                    'SteamCMD has been kept for future server installations.',
                    QMessageBox.Ok
                )
                
            elif self.game.name.lower() == "valheim":
                # Import the Valheim uninstall functions
                import sys
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                sys.path.insert(0, os.path.join(parent_dir, "scripts"))
                from scripts.valheim_server_startup_script import (
                    uninstall_valheim_server,
                    remove_port_forward_rule
                )
                
                print(f"Uninstalling {self.game.name} server...")
                
                # Remove port forwarding first
                try:
                    if remove_port_forward_rule():
                        print("✅ Port forwarding rules removed")
                    else:
                        print("ℹ️ No port forwarding rules to remove")
                except Exception as e:
                    print(f"⚠️ Failed to remove port forwarding: {e}")
                
                # Uninstall server files
                if uninstall_valheim_server():
                    print("✅ Valheim server files removed")
                    print("🏰 All Viking realms and server data have been deleted")
                else:
                    print("⚠️ Failed to remove server files")
                
                print(f"🗑️ {self.game.name} server uninstallation completed")
                print("ℹ️ SteamCMD has been kept for future server installations")
                
                # Refresh the UI to reflect the changes
                self.update_game(self.game)
                
                # Show success message
                QMessageBox.information(
                    self,
                    'Uninstallation Complete',
                    f'{self.game.name} server has been successfully uninstalled.\n\n'
                    'Server files, world data, and port forwarding rules have been removed.\n'
                    'SteamCMD has been kept for future server installations.',
                    QMessageBox.Ok
                )
                
            else:
                print(f"Uninstallation not yet implemented for {self.game.name}")
                QMessageBox.warning(
                    self,
                    'Not Implemented',
                    f'Uninstallation is not yet implemented for {self.game.name}',
                    QMessageBox.Ok
                )
                
        except Exception as e:
            print(f"❌ Error during uninstallation: {str(e)}")
            QMessageBox.critical(
                self,
                'Uninstallation Error',
                f'An error occurred during uninstallation:\n{str(e)}',
                QMessageBox.Ok
            )

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
        elif game_name.lower() == "valheim":
            return self.is_valheim_server_installed()
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

    def is_valheim_server_installed(self):
        """Check if Valheim server files are installed"""
        # Use the same paths as the startup script
        if platform.system().lower() == 'windows':
            steamcmd_dir = os.path.expandvars(r'%USERPROFILE%\SteamCMD')
            server_dir = os.path.expandvars(r'%USERPROFILE%\Steam\steamapps\common\Valheim dedicated server')
        else:
            steamcmd_dir = os.path.expanduser('~/SteamCMD')
            server_dir = os.path.expanduser('~/Steam/steamapps/common/Valheim dedicated server')
        
        # Check if SteamCMD is installed
        steamcmd_exe = os.path.join(steamcmd_dir, 'steamcmd.exe' if platform.system().lower() == 'windows' else 'steamcmd.sh')
        steamcmd_installed = os.path.exists(steamcmd_exe)
        
        # Check if Valheim server is installed
        valheim_exe = os.path.join(server_dir, 'valheim_server.exe' if platform.system().lower() == 'windows' else 'valheim_server.sh')
        server_installed = os.path.exists(valheim_exe)
        
        return steamcmd_installed and server_installed

    def add_server_status(self, layout):
        """Add server status section"""
        self.server_status_widget = QWidget()
        status_layout = QVBoxLayout()
        status_layout.setSpacing(Layout.SPACING_MEDIUM)
        
        # Server Status Title with refresh button
        title_container = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        status_title = QLabel("Server Status:")
        status_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        status_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-top: 20px;")
        title_layout.addWidget(status_title)
        
        # Add refresh button
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setFont(QFont('Segoe UI', 10))
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SILVER};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.SILVER_DARK};
                border-radius: 4px;
                padding: 5px 12px;
                margin-top: 20px;
            }}
            QPushButton:hover {{
                background-color: {Colors.SILVER_DARK};
            }}
            QPushButton:pressed {{
                background-color: {Colors.BACKGROUND_DARK};
                color: white;
            }}
        """)
        self.refresh_button.clicked.connect(self.update_server_status)
        title_layout.addWidget(self.refresh_button)
        
        title_container.setLayout(title_layout)
        status_layout.addWidget(title_container)
        
        # Status container with border
        status_container = QWidget()
        status_container.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.SILVER_LIGHT};
                border: 2px solid {Colors.SILVER};
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
        """Update the server status information using async worker"""
        if not self.game:
            return
            
        # Clean up any existing refresh worker before starting new one
        self.cleanup_refresh_worker()
        
        self.refresh_status_worker = ServerStatusWorker(self.game.name, fast_mode=True)
        self.refresh_status_worker.fast_status_ready.connect(self.on_fast_status_refresh_ready)
        self.refresh_status_worker.status_ready.connect(self.on_status_refresh_ready)
        self.refresh_status_worker.start()
    
    def on_fast_status_refresh_ready(self, status_info):
        """Handle fast status refresh (local info only) and update UI immediately"""
        self.update_server_status_display(status_info, is_fast_update=True)
    
    def on_status_refresh_ready(self, status_info):
        """Handle server status refresh completion and update UI"""
        self.update_server_status_display(status_info, is_fast_update=False)

    def update_server_status_display(self, status_info, is_fast_update=False):
        """Update the server status display with the provided information
        
        Args:
            status_info: Dictionary containing server status information
            is_fast_update: True if this is a fast update (local info only)
        """
        try:
            # Clear existing status content
            while self.status_content_layout.count():
                child = self.status_content_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            if status_info['is_running']:
                # Server is running - show green status
                status_text = "🟢 Server is RUNNING"
                if is_fast_update and status_info.get('public_ip') == "Unable to determine":
                    status_text += " (checking public IP...)"
                    
                running_label = QLabel(status_text)
                running_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
                running_label.setStyleSheet("color: #28a745; margin-bottom: 15px;")
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
                elif is_fast_update:
                    # Show loading indicator for public IP
                    loading_info = QLabel("Public IP: Loading...")
                    loading_info.setFont(QFont('Segoe UI', 13))
                    loading_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-family: 'Consolas', 'Courier New', monospace; font-style: italic;")
                    self.status_content_layout.addWidget(loading_info)
                
            else:
                # Server is not running - show red status
                not_running_label = QLabel("🔴 Server is NOT RUNNING")
                not_running_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
                not_running_label.setStyleSheet("color: #dc3545;")
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
            error_label.setStyleSheet("color: #ffc107;")
            self.status_content_layout.addWidget(error_label)
            
            error_detail = QLabel(f"Error: {str(e)}")
            error_detail.setFont(QFont('Segoe UI', 10))
            error_detail.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
            error_detail.setWordWrap(True)
            self.status_content_layout.addWidget(error_detail)

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
