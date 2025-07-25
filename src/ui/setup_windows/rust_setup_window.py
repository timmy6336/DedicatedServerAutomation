"""
Rust Dedicated Server Setup Window

This module provides a specialized setup window for Rust dedicated servers.
It inherits from the base setup window and provides Rust-specific configuration
options and installation steps.

The setup process includes:
- SteamCMD installation and verification
- Rust dedicated server download and installation
- User-configurable server settings (name, max players, world size, port)
- Network configuration with firewall and UPnP options
- UPnP port forwarding configuration (ports 28015-28016, 28082)
- Server launch and verification
- Survival-themed status messages and guidance

Features:
- Interactive server configuration dialog
- Progress tracking with real-time status updates
- User-configurable port forwarding options
- Network configuration assistance
- Error handling and recovery guidance
- Integration with Rust-specific automation scripts
"""

# ================== RUST SERVER CONFIGURATION CONSTANTS ==================
# Dialog window dimensions and sizing
RUST_CONFIG_DIALOG_WIDTH = 650           # Width of the configuration dialog window
RUST_CONFIG_DIALOG_HEIGHT = 450          # Height of the configuration dialog window
RUST_CONFIG_DIALOG_MIN_HEIGHT = 400      # Minimum height for the configuration dialog
RUST_CONFIG_DIALOG_MAX_HEIGHT = 550      # Maximum height for the configuration dialog
RUST_CONFIG_DIALOG_TOP_OFFSET = 20       # Offset from top of parent window when positioning dialog

# Rust server port configuration
RUST_DEFAULT_PORT_MIN = 1024              # Minimum allowed port for Rust server
RUST_DEFAULT_PORT_MAX = 65535             # Maximum allowed port for Rust server
RUST_DEFAULT_PORT_BASE = 28015            # Base port number for Rust (default)
RUST_PORT_OFFSET_QUERY = 1                # Offset for query port (+1 from base)
RUST_PORT_OFFSET_APP = 67                 # Offset for app port (28082 - 28015)

# Rust server configuration limits
RUST_MIN_PLAYERS = 1                      # Minimum players for private servers
RUST_MAX_PLAYERS = 300                    # Maximum players supported by Rust
RUST_DEFAULT_MAX_PLAYERS = 100            # Default maximum players
RUST_MIN_WORLD_SIZE = 1000                # Minimum world size
RUST_MAX_WORLD_SIZE = 4000                # Maximum world size
RUST_DEFAULT_WORLD_SIZE = 3000            # Default world size
RUST_DEFAULT_SEED = 12345                 # Default world generation seed

# Font sizes for UI elements
FONT_SIZE_CONFIG_TITLE = 18               # Font size for main configuration dialog title
FONT_SIZE_GROUP_HEADER = 14               # Font size for group box headers
FONT_SIZE_INPUT_FIELDS = 12               # Font size for input fields and labels
FONT_SIZE_INFO_TEXT = 10                  # Font size for information/help text
FONT_SIZE_BUTTON_LARGE = 12               # Font size for dialog buttons

# Layout and spacing constants
LAYOUT_SPACING_LARGE = 15                 # Large spacing between major sections
LAYOUT_SPACING_MEDIUM = 10                # Medium spacing between form elements
LAYOUT_SPACING_SMALL = 8                  # Small spacing for margins and padding
GROUP_BOX_MARGIN_TOP = 8                  # Top margin for group boxes
GROUP_BOX_PADDING_TOP = 8                 # Top padding inside group boxes
TITLE_PADDING_HORIZONTAL = 5              # Horizontal padding for group box titles
INFO_TEXT_MAX_HEIGHT = 60                 # Maximum height for information text areas

# Border and visual styling
BORDER_WIDTH_STANDARD = 2                 # Standard border width for UI elements
BORDER_RADIUS_STANDARD = 8                # Standard border radius for buttons and groups
BORDER_RADIUS_SMALL = 6                   # Small border radius for input fields
BUTTON_PADDING_VERTICAL = 10              # Vertical padding inside buttons
BUTTON_PADDING_HORIZONTAL = 20            # Horizontal padding inside buttons
INPUT_FIELD_PADDING = 6                   # Padding inside input fields
INPUT_FIELD_MIN_WIDTH = 200               # Minimum width for input fields

# Game-specific constants
RUST_DOWNLOAD_SIZE_GB = 3                 # Approximate download size in GB
RUST_DOWNLOAD_SIZE_MB = 10                # SteamCMD download size in MB

import os
import sys
from PyQt5.QtWidgets import (QCheckBox, QLabel, QDialog, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QSpinBox,
                            QGroupBox, QFormLayout, QMessageBox, QComboBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread
from .base_setup_window import BaseServerSetupWindow

# Import styles from parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from styles import Colors, Layout

# Import the Rust startup script
sys.path.insert(0, os.path.join(parent_dir, "scripts"))
from scripts.rust_server_startup_script import (
    download_steamcmd,
    install_or_update_rust_server,
    setup_upnp_port_forwarding,
    start_rust_server,
    configure_rust_firewall,
    create_rust_server_config,
    is_rust_server_installed
)

# Import configuration manager
sys.path.insert(0, os.path.join(parent_dir, "utils"))
from utils.config_manager import config_manager


class RustConfigDialog(QDialog):
    """
    Dialog for configuring Rust server settings.
    
    Provides a user-friendly interface for configuring:
    - Server name and description
    - Maximum players and world settings
    - Port configuration
    - Game mode options (PvE/PvP)
    - Network and firewall options
    """
    
    def __init__(self, parent=None):
        # Ensure dialog is created on the main thread
        if QThread.currentThread() != parent.thread() if parent else False:
            raise RuntimeError("RustConfigDialog must be created on the main thread")
            
        super().__init__(parent)
        self.setWindowTitle("🦀 Configure Rust Server")
        self.setModal(True)
        
        # Make dialog resizable with size constraints
        self.setMinimumSize(RUST_CONFIG_DIALOG_WIDTH, RUST_CONFIG_DIALOG_MIN_HEIGHT)
        self.setMaximumSize(RUST_CONFIG_DIALOG_WIDTH, RUST_CONFIG_DIALOG_MAX_HEIGHT)
        self.resize(RUST_CONFIG_DIALOG_WIDTH, RUST_CONFIG_DIALOG_HEIGHT)
        
        self.setStyleSheet(f"background-color: {Colors.BACKGROUND_DARK};")
        
        # Server configuration values - load from persistent storage or use defaults
        saved_config = config_manager.load_server_config('Rust')
        if saved_config:
            self.server_config = saved_config
        else:
            self.server_config = config_manager.get_default_rust_config()
        
        # Initialize UI first
        self.init_ui()
        
        # Ensure proper sizing after UI initialization
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())
        
        # Position the dialog after size calculation
        self.position_dialog_at_top()
    
    def position_dialog_at_top(self):
        """Position the dialog at the top of the parent window after size calculation."""
        parent = self.parent()
        if parent:
            parent_geometry = parent.geometry()
            # Position dialog at top-center of parent window
            dialog_x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            dialog_y = parent_geometry.y() + RUST_CONFIG_DIALOG_TOP_OFFSET
            
            # Ensure dialog stays within screen bounds
            screen = parent.screen() if hasattr(parent, 'screen') else None
            if screen:
                screen_geometry = screen.availableGeometry()
                dialog_x = max(screen_geometry.x(), min(dialog_x, screen_geometry.x() + screen_geometry.width() - self.width()))
                dialog_y = max(screen_geometry.y(), min(dialog_y, screen_geometry.y() + screen_geometry.height() - self.height()))
            
            self.move(dialog_x, dialog_y)
    
    def init_ui(self):
        """Initialize the configuration dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(LAYOUT_SPACING_SMALL)
        layout.setContentsMargins(LAYOUT_SPACING_MEDIUM, LAYOUT_SPACING_SMALL, LAYOUT_SPACING_MEDIUM, LAYOUT_SPACING_SMALL)
        layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        
        # Title
        title = QLabel("🦀 Rust Server Configuration")
        title.setFont(QFont('Segoe UI', FONT_SIZE_CONFIG_TITLE, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-bottom: {LAYOUT_SPACING_SMALL//2}px;")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # Server Settings Group
        server_group = QGroupBox("⚙️ Server Settings")
        server_group.setFont(QFont('Segoe UI', FONT_SIZE_GROUP_HEADER, QFont.Bold))
        server_group.setStyleSheet(f"""
            QGroupBox {{
                color: {Colors.TEXT_PRIMARY};
                border: {BORDER_WIDTH_STANDARD}px solid {Colors.GRAY_MEDIUM};
                border-radius: {BORDER_RADIUS_STANDARD}px;
                margin-top: {GROUP_BOX_MARGIN_TOP}px;
                padding-top: {GROUP_BOX_PADDING_TOP}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {LAYOUT_SPACING_SMALL}px;
                padding: 0 {TITLE_PADDING_HORIZONTAL}px 0 {TITLE_PADDING_HORIZONTAL}px;
            }}
        """)
        
        server_form = QFormLayout(server_group)
        server_form.setSpacing(LAYOUT_SPACING_SMALL//2)
        
        # Server Name
        self.server_name_input = QLineEdit(self.server_config.get('server_name', 'My Rust Server'))
        self.server_name_input.setStyleSheet(f"""
            QLineEdit {{
                padding: {INPUT_FIELD_PADDING}px;
                border: 1px solid {Colors.GRAY_MEDIUM};
                border-radius: {BORDER_RADIUS_SMALL}px;
                background-color: {Colors.BACKGROUND_LIGHT};
                color: {Colors.TEXT_PRIMARY};
                font-size: {FONT_SIZE_INPUT_FIELDS}px;
                min-width: {INPUT_FIELD_MIN_WIDTH}px;
            }}
            QLineEdit:focus {{
                border-color: {Colors.PRIMARY_BLUE};
            }}
        """)
        server_form.addRow(QLabel("🏷️ Server Name:"), self.server_name_input)
        
        # Max Players
        self.max_players_input = QSpinBox()
        self.max_players_input.setRange(RUST_MIN_PLAYERS, RUST_MAX_PLAYERS)
        self.max_players_input.setValue(self.server_config.get('max_players', RUST_DEFAULT_MAX_PLAYERS))
        self.max_players_input.setStyleSheet(f"""
            QSpinBox {{
                padding: {INPUT_FIELD_PADDING}px;
                border: 1px solid {Colors.GRAY_MEDIUM};
                border-radius: {BORDER_RADIUS_SMALL}px;
                background-color: {Colors.BACKGROUND_LIGHT};
                color: {Colors.TEXT_PRIMARY};
                font-size: {FONT_SIZE_INPUT_FIELDS}px;
                min-width: {INPUT_FIELD_MIN_WIDTH}px;
            }}
        """)
        server_form.addRow(QLabel("👥 Max Players:"), self.max_players_input)
        
        # World Size
        self.world_size_input = QComboBox()
        world_sizes = ["1000", "2000", "3000", "4000"]
        self.world_size_input.addItems(world_sizes)
        current_world_size = str(self.server_config.get('world_size', RUST_DEFAULT_WORLD_SIZE))
        if current_world_size in world_sizes:
            self.world_size_input.setCurrentText(current_world_size)
        self.world_size_input.setStyleSheet(f"""
            QComboBox {{
                padding: {INPUT_FIELD_PADDING}px;
                border: 1px solid {Colors.GRAY_MEDIUM};
                border-radius: {BORDER_RADIUS_SMALL}px;
                background-color: {Colors.BACKGROUND_LIGHT};
                color: {Colors.TEXT_PRIMARY};
                font-size: {FONT_SIZE_INPUT_FIELDS}px;
                min-width: {INPUT_FIELD_MIN_WIDTH}px;
            }}
        """)
        server_form.addRow(QLabel("🗺️ World Size:"), self.world_size_input)
        
        # World Seed
        self.seed_input = QSpinBox()
        self.seed_input.setRange(1, 2147483647)
        self.seed_input.setValue(self.server_config.get('seed', RUST_DEFAULT_SEED))
        self.seed_input.setStyleSheet(f"""
            QSpinBox {{
                padding: {INPUT_FIELD_PADDING}px;
                border: 1px solid {Colors.GRAY_MEDIUM};
                border-radius: {BORDER_RADIUS_SMALL}px;
                background-color: {Colors.BACKGROUND_LIGHT};
                color: {Colors.TEXT_PRIMARY};
                font-size: {FONT_SIZE_INPUT_FIELDS}px;
                min-width: {INPUT_FIELD_MIN_WIDTH}px;
            }}
        """)
        server_form.addRow(QLabel("🎲 World Seed:"), self.seed_input)
        
        # Port
        self.port_input = QSpinBox()
        self.port_input.setRange(RUST_DEFAULT_PORT_MIN, RUST_DEFAULT_PORT_MAX)
        self.port_input.setValue(self.server_config.get('port', 28015))
        self.port_input.setStyleSheet(f"""
            QSpinBox {{
                padding: {INPUT_FIELD_PADDING}px;
                border: 1px solid {Colors.GRAY_MEDIUM};
                border-radius: {BORDER_RADIUS_SMALL}px;
                background-color: {Colors.BACKGROUND_LIGHT};
                color: {Colors.TEXT_PRIMARY};
                font-size: {FONT_SIZE_INPUT_FIELDS}px;
                min-width: {INPUT_FIELD_MIN_WIDTH}px;
            }}
        """)
        server_form.addRow(QLabel("🌐 Port:"), self.port_input)
        
        layout.addWidget(server_group)
        
        # Game Mode Settings Group
        gamemode_group = QGroupBox("⚔️ Game Mode Settings")
        gamemode_group.setFont(QFont('Segoe UI', FONT_SIZE_GROUP_HEADER, QFont.Bold))
        gamemode_group.setStyleSheet(f"""
            QGroupBox {{
                color: {Colors.TEXT_PRIMARY};
                border: {BORDER_WIDTH_STANDARD}px solid {Colors.GRAY_MEDIUM};
                border-radius: {BORDER_RADIUS_STANDARD}px;
                margin-top: {GROUP_BOX_MARGIN_TOP}px;
                padding-top: {GROUP_BOX_PADDING_TOP}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {LAYOUT_SPACING_SMALL}px;
                padding: 0 {TITLE_PADDING_HORIZONTAL}px 0 {TITLE_PADDING_HORIZONTAL}px;
            }}
        """)
        
        gamemode_layout = QVBoxLayout(gamemode_group)
        gamemode_layout.setSpacing(LAYOUT_SPACING_SMALL//2)
        
        # PvE Mode Checkbox
        self.pve_checkbox = QCheckBox("🕊️ Enable PvE Mode (No Player vs Player)")
        self.pve_checkbox.setChecked(self.server_config.get('pve_mode', False))
        self.pve_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {FONT_SIZE_INPUT_FIELDS}px;
                spacing: {LAYOUT_SPACING_SMALL}px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {Colors.BACKGROUND_LIGHT};
                border: 1px solid {Colors.GRAY_MEDIUM};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {Colors.PRIMARY_BLUE};
                border: 1px solid {Colors.PRIMARY_BLUE};
                border-radius: 3px;
            }}
        """)
        gamemode_layout.addWidget(self.pve_checkbox)
        
        # VAC Secure Checkbox
        self.secure_checkbox = QCheckBox("🛡️ Enable VAC (Anti-Cheat Protection)")
        self.secure_checkbox.setChecked(self.server_config.get('secure', True))
        self.secure_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {FONT_SIZE_INPUT_FIELDS}px;
                spacing: {LAYOUT_SPACING_SMALL}px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {Colors.BACKGROUND_LIGHT};
                border: 1px solid {Colors.GRAY_MEDIUM};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {Colors.PRIMARY_BLUE};
                border: 1px solid {Colors.PRIMARY_BLUE};
                border-radius: 3px;
            }}
        """)
        gamemode_layout.addWidget(self.secure_checkbox)
        
        layout.addWidget(gamemode_group)
        
        # Network Settings Group
        network_group = QGroupBox("🌐 Network Settings")
        network_group.setFont(QFont('Segoe UI', FONT_SIZE_GROUP_HEADER, QFont.Bold))
        network_group.setStyleSheet(f"""
            QGroupBox {{
                color: {Colors.TEXT_PRIMARY};
                border: {BORDER_WIDTH_STANDARD}px solid {Colors.GRAY_MEDIUM};
                border-radius: {BORDER_RADIUS_STANDARD}px;
                margin-top: {GROUP_BOX_MARGIN_TOP}px;
                padding-top: {GROUP_BOX_PADDING_TOP}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {LAYOUT_SPACING_SMALL}px;
                padding: 0 {TITLE_PADDING_HORIZONTAL}px 0 {TITLE_PADDING_HORIZONTAL}px;
            }}
        """)
        
        network_layout = QVBoxLayout(network_group)
        network_layout.setSpacing(LAYOUT_SPACING_SMALL//2)
        
        # Firewall Configuration
        self.firewall_checkbox = QCheckBox("🔥 Configure Windows Firewall")
        self.firewall_checkbox.setChecked(self.server_config.get('configure_firewall', True))
        self.firewall_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {FONT_SIZE_INPUT_FIELDS}px;
                spacing: {LAYOUT_SPACING_SMALL}px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {Colors.BACKGROUND_LIGHT};
                border: 1px solid {Colors.GRAY_MEDIUM};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {Colors.PRIMARY_BLUE};
                border: 1px solid {Colors.PRIMARY_BLUE};
                border-radius: 3px;
            }}
        """)
        network_layout.addWidget(self.firewall_checkbox)
        
        # UPnP Port Forwarding
        self.upnp_checkbox = QCheckBox("📡 Enable UPnP Port Forwarding")
        self.upnp_checkbox.setChecked(self.server_config.get('enable_upnp', True))
        self.upnp_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {FONT_SIZE_INPUT_FIELDS}px;
                spacing: {LAYOUT_SPACING_SMALL}px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {Colors.BACKGROUND_LIGHT};
                border: 1px solid {Colors.GRAY_MEDIUM};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {Colors.PRIMARY_BLUE};
                border: 1px solid {Colors.PRIMARY_BLUE};
                border-radius: 3px;
            }}
        """)
        network_layout.addWidget(self.upnp_checkbox)
        
        layout.addWidget(network_group)
        
        # Information Text
        info_text = QLabel("ℹ️ Rust servers require significant system resources. Recommended: 8GB+ RAM, SSD storage, and good CPU for large player counts.")
        info_text.setWordWrap(True)
        info_text.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-size: {FONT_SIZE_INFO_TEXT}px;
                padding: {LAYOUT_SPACING_SMALL}px;
                background-color: {Colors.BACKGROUND_MEDIUM};
                border-radius: {BORDER_RADIUS_SMALL}px;
                margin: {LAYOUT_SPACING_SMALL}px 0px;
            }}
        """)
        info_text.setMaximumHeight(INFO_TEXT_MAX_HEIGHT)
        layout.addWidget(info_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(LAYOUT_SPACING_SMALL)
        
        self.ok_button = QPushButton("✅ Apply Configuration")
        self.ok_button.setFont(QFont('Segoe UI', FONT_SIZE_BUTTON_LARGE, QFont.Bold))
        self.ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.PRIMARY_BLUE};
                color: white;
                border: none;
                padding: {BUTTON_PADDING_VERTICAL}px {BUTTON_PADDING_HORIZONTAL}px;
                border-radius: {BORDER_RADIUS_STANDARD}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.SECONDARY_BLUE};
            }}
            QPushButton:pressed {{
                background-color: {Colors.ACCENT_BLUE};
            }}
        """)
        self.ok_button.clicked.connect(self.accept_config)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.setFont(QFont('Segoe UI', FONT_SIZE_BUTTON_LARGE))
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GRAY_MEDIUM};
                color: {Colors.TEXT_PRIMARY};
                border: none;
                padding: {BUTTON_PADDING_VERTICAL}px {BUTTON_PADDING_HORIZONTAL}px;
                border-radius: {BORDER_RADIUS_STANDARD}px;
            }}
            QPushButton:hover {{
                background-color: {Colors.GRAY_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {Colors.GRAY_DARK};
            }}
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def accept_config(self):
        """Validate and accept the server configuration."""
        try:
            # Validate server name
            server_name = self.server_name_input.text().strip()
            if not server_name:
                QMessageBox.warning(self, "Invalid Configuration", "Server name cannot be empty.")
                return
            
            # Validate max players
            max_players = self.max_players_input.value()
            if max_players < RUST_MIN_PLAYERS or max_players > RUST_MAX_PLAYERS:
                QMessageBox.warning(self, "Invalid Configuration", 
                                  f"Max players must be between {RUST_MIN_PLAYERS} and {RUST_MAX_PLAYERS}.")
                return
            
            # All validation passed
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Configuration Error", f"Error validating configuration: {str(e)}")
    
    def get_config(self):
        """Get the server configuration as a dictionary."""
        config = {
            'server_name': self.server_name_input.text().strip(),
            'max_players': self.max_players_input.value(),
            'world_size': int(self.world_size_input.currentText()),
            'seed': self.seed_input.value(),
            'port': self.port_input.value(),
            'pve_mode': self.pve_checkbox.isChecked(),
            'secure': self.secure_checkbox.isChecked(),
            'configure_firewall': self.firewall_checkbox.isChecked(),
            'enable_upnp': self.upnp_checkbox.isChecked()
        }
        
        # Save configuration for next time
        config_manager.save_server_config('Rust', config)
        
        return config


class RustServerSetupWindow(BaseServerSetupWindow):
    """
    Rust-specific server setup window.
    
    Provides step-by-step installation and configuration for Rust dedicated servers
    with survival-themed UI elements and comprehensive server management options.
    
    Features:
    - Multi-step installation process with progress tracking
    - Rust-specific configuration options and validation
    - Survival-themed status messages for better user experience
    - Integration with Rust automation scripts
    """
    
    def __init__(self, game):
        """
        Initialize the Rust setup window.
        
        Args:
            game: Game object containing Rust metadata and configuration
        """
        self.port_checkbox = None
        self.server_config = None  # Initialize server configuration
        super().__init__(game)
    
    def get_setup_steps(self):
        """
        Define the setup steps specific to Rust server installation.
        
        Checks if Rust is already installed and skips installation steps
        if it exists, going directly to the configuration step.
        
        Returns a list of setup steps with survival-themed descriptions and
        appropriate confirmation prompts for the Rust installation process.
        
        Returns:
            list: List of setup step dictionaries containing step configuration
        """
        # Check if Rust server is already installed
        if is_rust_server_installed():
            # Skip installation steps, go directly to configuration
            return [
                {
                    'name': '🦀 Rust Server Found',
                    'description': '''
                    <h3>🎉 Great news! Rust dedicated server is already installed!</h3>
                    <p>We found an existing Rust server installation on your system.</p>
                    <p><strong>📁 Installation Details:</strong></p>
                    <ul>
                        <li>✅ Rust dedicated server files are present</li>
                        <li>✅ SteamCMD installation verified</li>
                        <li>🦀 Ready for survival server configuration</li>
                    </ul>
                    <p><strong>🚀 Next Steps:</strong></p>
                    <ul>
                        <li>Configure your survival server settings</li>
                        <li>Set up world generation and player limits</li>
                        <li>Launch your Rust world for players to explore</li>
                    </ul>
                    ''',
                    'function': start_rust_server,
                    'button_text': '⚙️ Configure Rust Server',
                    'skippable': False,
                    'confirmation_required': False
                }
            ]
        else:
            # Full installation process
            return [
                {
                    'name': '📥 Download SteamCMD',
                    'description': f'''
                    <h3>🔧 Setting up SteamCMD for Rust</h3>
                    <p>SteamCMD is Steam's command-line tool for downloading and managing dedicated servers.</p>
                    <p><strong>📊 Download Information:</strong></p>
                    <ul>
                        <li>📦 Size: ~{RUST_DOWNLOAD_SIZE_MB}MB</li>
                        <li>⏱️ Time: 1-3 minutes</li>
                        <li>🔧 Used for: Installing and updating Rust servers</li>
                    </ul>
                    <p><strong>🚀 What happens next:</strong></p>
                    <ul>
                        <li>Download SteamCMD from Valve's servers</li>
                        <li>Extract and configure the tool</li>
                        <li>Prepare for Rust server download</li>
                    </ul>
                    ''',
                    'function': download_steamcmd,
                    'button_text': '📥 Download SteamCMD',
                    'skippable': False,
                    'confirmation_required': True,
                    'confirmation_message': 'Ready to download SteamCMD? This will download the Steam command-line tool needed for server management.'
                },
                {
                    'name': '🦀 Install Rust Server',
                    'description': f'''
                    <h3>🎮 Downloading Rust Dedicated Server</h3>
                    <p>Now we'll download the official Rust dedicated server files from Steam.</p>
                    
                    <p><strong>🦀 About Rust:</strong></p>
                    <p>Rust is a multiplayer survival game where players must gather resources, build bases, and survive against other players and environmental threats. The game features intense PvP combat, complex crafting systems, and persistent world progression with wipe cycles.</p>
                    
                    <p><strong>📊 System Requirements for Dedicated Server:</strong></p>
                    <p><u>Minimum Requirements:</u></p>
                    <ul>
                        <li><b>RAM:</b> 8GB (for 25-50 players)</li>
                        <li><b>CPU:</b> 4-core 3.0GHz (Intel i5-6400 / AMD Ryzen 5 1400)</li>
                        <li><b>GPU:</b> Not required (headless server)</li>
                        <li><b>Storage:</b> 20GB available space</li>
                        <li><b>Network:</b> Broadband connection</li>
                    </ul>
                    
                    <p><u>Recommended for 100-300 Players:</u></p>
                    <ul>
                        <li><b>RAM:</b> 16-32GB dedicated to server</li>
                        <li><b>CPU:</b> 8-16 core 3.5GHz+ (Intel i7-10700K / AMD Ryzen 7 5800X)</li>
                        <li><b>GPU:</b> Not required (dedicated server runs headless)</li>
                        <li><b>Storage:</b> 50GB+ NVMe SSD for map data and player saves</li>
                        <li><b>Upload Speed:</b> 50+ Mbps for large-scale PvP servers</li>
                    </ul>
                    
                    <p><strong>📦 Download Information:</strong></p>
                    <ul>
                        <li>📦 Size: ~{RUST_DOWNLOAD_SIZE_GB}GB server files</li>
                        <li>⏱️ Time: 10-30 minutes (depends on connection)</li>
                        <li>🎯 Version: Latest stable build</li>
                        <li>🗺️ Map Save Size: 100MB-1GB (varies by world size)</li>
                    </ul>
                    
                    <p><strong>🦀 Rust Server Features:</strong></p>
                    <ul>
                        <li>🌍 Support for up to 300 players</li>
                        <li>🗺️ Procedural world generation (1000-4000 map size)</li>
                        <li>⚔️ Full PvP and PvE support</li>
                        <li>🔧 Comprehensive admin tools and modding support</li>
                        <li>📱 Rust+ companion app integration</li>
                    </ul>
                    
                    <p><strong>⚠️ Performance Note:</strong> Rust servers are very resource-intensive, especially with large player counts. More RAM and faster CPUs significantly improve performance and reduce lag.</p>
                    ''',
                    'function': install_or_update_rust_server,
                    'button_text': '🦀 Install Rust Server',
                    'skippable': False,
                    'confirmation_required': True,
                    'confirmation_message': f'Ready to download Rust server? This will download approximately {RUST_DOWNLOAD_SIZE_GB}GB of server files.'
                },
                {
                    'name': '⚙️ Configure & Launch',
                    'description': '''
                    <h3>🎯 Final Server Configuration</h3>
                    <p>Time to configure your Rust survival server and launch it for the first time!</p>
                    <p><strong>🔧 Configuration Options:</strong></p>
                    <ul>
                        <li>🏷️ Server name and description</li>
                        <li>👥 Maximum player count (1-300)</li>
                        <li>🗺️ World size and generation seed</li>
                        <li>⚔️ PvP/PvE mode selection</li>
                        <li>🌐 Network and port settings</li>
                    </ul>
                    <p><strong>🚀 Launch Process:</strong></p>
                    <ul>
                        <li>Apply your custom server settings</li>
                        <li>Configure firewall and port forwarding</li>
                        <li>Generate and launch your Rust world</li>
                        <li>Start accepting player connections</li>
                    </ul>
                    ''',
                    'function': 'configure_and_launch_server',
                    'button_text': '⚙️ Configure & Launch Server',
                    'skippable': False,
                    'confirmation_required': False
                }
            ]
    
    def get_game_specific_ui_elements(self):
        """
        Get Rust-specific UI elements for the setup window.
        
        Returns:
            list: List of UI elements specific to Rust server setup
        """
        elements = []
        
        # Add Rust-specific information or controls if needed
        if hasattr(self, 'current_step') and self.current_step == len(self.setup_steps) - 1:
            # Final step - add launch information
            action_info = QLabel("""
            🦀 <strong>Ready to Survive!</strong><br/>
            Your Rust server will be configured and launched with your selected settings.<br/>
            Players will be able to connect and start their survival journey!
            """)
            action_info.setStyleSheet(f"""
                QLabel {{
                    color: {Colors.TEXT_PRIMARY};
                    background-color: {Colors.BACKGROUND_MEDIUM};
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid {Colors.SUCCESS};
                    font-size: 12px;
                }}
            """)
            action_info.setWordWrap(True)
            action_info.setAlignment(Qt.AlignCenter)
            elements.append(action_info)
        
        return elements
    
    def configure_and_launch_server(self):
        """
        Handle the configure and launch step preparation.
        
        Opens the configuration dialog for the user to set up their Rust server
        settings including server name, max players, world configuration, and network options.
        
        Returns:
            bool: True to proceed to final step completion
        """
        self.log_message("🦀 Ready to configure your survival server...")
        self.log_message("⚙️ Opening server configuration dialog...")
        self.log_message("📋 Please complete the configuration form to customize your server...")
        
        # Show configuration dialog directly on main thread
        config_dialog = RustConfigDialog(self)
        
        if config_dialog.exec_() == QDialog.Accepted:
            # Store the configuration for use in final step
            self.server_config = config_dialog.get_config()
            self.log_message("✅ Server configuration completed!")
            self.log_message("📊 Configuration Summary:")
            self.log_message(f"   🏷️ Server: {self.server_config['server_name']}")
            self.log_message(f"   👥 Max Players: {self.server_config['max_players']}")
            self.log_message(f"   🗺️ World Size: {self.server_config['world_size']}")
            self.log_message(f"   🎲 Seed: {self.server_config['seed']}")
            self.log_message(f"   🌐 Port: {self.server_config['port']}")
            self.log_message(f"   ⚔️ PvE Mode: {'Yes' if self.server_config['pve_mode'] else 'No'}")
            self.log_message(f"   🛡️ VAC Secure: {'Yes' if self.server_config['secure'] else 'No'}")
            self.log_message(f"   🔥 Firewall: {'Enabled' if self.server_config['configure_firewall'] else 'Disabled'}")
            self.log_message(f"   📡 UPnP: {'Enabled' if self.server_config['enable_upnp'] else 'Disabled'}")
            self.log_message("🦀 Preparing for survival server launch...")
            return True
        else:
            self.log_message("❌ Server configuration cancelled.")
            self.log_message("ℹ️ Please configure your server to continue.")
            self.log_message("💡 Click 'Continue' again to reopen the configuration dialog.")
            return False
    
    def handle_final_step_completion(self):
        """
        Handle Rust-specific final step completion.
        
        Performs the actual server configuration including:
        - Firewall configuration (if selected)
        - UPnP port forwarding setup (if selected)
        - Server configuration file creation
        - Server startup with user settings
        
        Returns:
            bool: True if server setup and launch succeeded, False otherwise
        """
        self.log_message("🚀 Launching your Rust survival server...")
        self.log_message("⚡ Preparing for the ultimate survival experience...")
        
        # Get configuration (set during configure_and_launch_server)
        if not hasattr(self, 'server_config'):
            self.log_message("❌ No server configuration found!")
            return False
        
        config = self.server_config
        success = True
        
        # Configure firewall if selected
        if config['configure_firewall']:
            self.log_message("🔥 Configuring Windows Firewall for Rust...")
            self.log_message(f"🔓 Adding firewall rules for ports {config['port']}-{config['port']+1} and 28082...")
            try:
                firewall_success = configure_rust_firewall(config['port'])
                if firewall_success:
                    self.log_message("✅ Firewall configured successfully!")
                    self.log_message("🔥 Rust traffic is now allowed through Windows Firewall!")
                else:
                    self.log_message("⚠️ Firewall configuration failed!")
                    self.log_message("🛠️ You may need to manually allow Rust through Windows Firewall")
            except Exception as e:
                self.log_message(f"❌ Firewall configuration error: {str(e)}")
                self.log_message("ℹ️ Server will continue without firewall configuration")
        
        # Configure port forwarding if selected
        if config['enable_upnp']:
            self.log_message("🌐 Configuring UPnP port forwarding for external players...")
            self.log_message(f"📡 Opening ports ({config['port']}, {config['port']+1}, 28082) through your router...")
            try:
                port_success = setup_upnp_port_forwarding(config['port'])
                if port_success:
                    self.log_message("✅ Port forwarding configured successfully!")
                    self.log_message("🌍 External players can now reach your server!")
                else:
                    self.log_message("⚠️ Port forwarding failed, but no worries!")
                    self.log_message(f"🛠️ Manual setup: Forward UDP {config['port']}-{config['port']+1}, TCP 28082")
                    self.log_message(f"📋 Game: {config['port']} UDP, Query: {config['port']+1} UDP, App: 28082 TCP")
            except Exception as e:
                self.log_message(f"❌ Port forwarding error: {str(e)}")
                self.log_message("ℹ️ Server will be accessible locally")
        else:
            self.log_message("🏠 Port forwarding skipped - server will be accessible locally only.")
            self.log_message("ℹ️ Local players can still join the survival experience!")
        
        # Create server configuration file
        self.log_message("📄 Creating server configuration files...")
        try:
            config_success = create_rust_server_config(config)
            if config_success:
                self.log_message("✅ Server configuration files created!")
            else:
                self.log_message("⚠️ Could not create configuration files, using defaults")
        except Exception as e:
            self.log_message(f"❌ Configuration file error: {str(e)}")
            self.log_message("ℹ️ Server will use default configuration")
        
        # Start the server
        self.log_message("🔥 Igniting the Rust survival server...")
        self.log_message("🦀 Preparing tools, resources, and survival challenges...")
        try:
            server_success = start_rust_server(
                server_name=config['server_name'],
                max_players=config['max_players'],
                world_size=config['world_size'],
                seed=config['seed'],
                port=config['port'],
                pve_mode=config['pve_mode'],
                secure=config['secure']
            )
            if server_success:
                self.log_message("🎉 Rust dedicated server started successfully!")
                self.log_message("🖥️ The server is now running in a separate command prompt window!")
                self.log_message("🦀 Your survival world is now active and ready for players!")
                self.log_message(f"👥 Up to {config['max_players']} survivors can join your world!")
                self.log_message(f"🗺️ World size {config['world_size']} generated with seed {config['seed']}")
                self.log_message(f"🌐 Server '{config['server_name']}' broadcasting on port {config['port']}")
                self.log_message("💾 Player progress and world changes will be automatically saved.")
                self.log_message("🔧 To stop the server: Close the server console window or press Ctrl+C in it.")
                if config['pve_mode']:
                    self.log_message("🕊️ PvE Mode: Cooperative survival experience enabled!")
                else:
                    self.log_message("⚔️ PvP Mode: Full survival competition enabled!")
                if config['secure']:
                    self.log_message("🛡️ VAC protection enabled for a secure gaming environment!")
                self.log_message("🦀 Welcome to the harsh world of Rust survival!")
                self.log_message("=" * 60)
            else:
                self.log_message("❌ Failed to start Rust server!")
                self.log_message("🛠️ Check the error messages above for troubleshooting.")
                success = False
        except Exception as e:
            self.log_message(f"❌ Server startup error: {str(e)}")
            self.log_message("🔧 Please check your configuration and try again.")
            success = False
        
        return success
    
    def add_control_buttons(self, layout):
        """Add control buttons - using base implementation (no custom delete button)"""
        super().add_control_buttons(layout)
