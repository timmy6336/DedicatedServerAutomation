"""
Valheim Dedicated Ser# Dialog window dimensions and sizing
VALHEIM_CONFIG_DIALOG_WIDTH = 600          # Width of the configuration dialog window
VALHEIM_CONFIG_DIALOG_HEIGHT = 550         # Height of the configuration dialog window
VALHEIM_CONFIG_DIALOG_MIN_HEIGHT = 500     # Minimum height for the configuration dialog
VALHEIM_CONFIG_DIALOG_MAX_HEIGHT = 700     # Maximum height for the configuration dialog
VALHEIM_CONFIG_DIALOG_TOP_OFFSET = 20      # Offset from top of parent window when positioning dialogetup Window

This module provides a specialized setup window for Valheim dedicated servers.
It inherits from the base setup window and provides Valheim-specific configuration
options and installation steps.

The setup process includes:
- SteamCMD installation and verification
- Valheim dedicated server download and installation
- User-configurable server settings (name, password, world, port)
- Network configuration with firewall and UPnP options
- UPnP port forwarding configuration (ports 2456-2458)
- Server launch and verification
- Viking-themed status messages and guidance

Features:
- Interactive server configuration dialog
- Progress tracking with real-time status updates
- User-configurable port forwarding options
- Network configuration assistance
- Error handling and recovery guidance
- Integration with Valheim-specific automation scripts
"""

# ================== VALHEIM SERVER CONFIGURATION CONSTANTS ==================
# Dialog window dimensions and sizing
VALHEIM_CONFIG_DIALOG_WIDTH = 600          # Width of the configuration dialog window
VALHEIM_CONFIG_DIALOG_HEIGHT = 550         # Height of the configuration dialog window
VALHEIM_CONFIG_DIALOG_MIN_HEIGHT = 500     # Minimum height for the configuration dialog
VALHEIM_CONFIG_DIALOG_MAX_HEIGHT = 700     # Maximum height for the configuration dialog
VALHEIM_CONFIG_DIALOG_TOP_OFFSET = 20      # Offset from top of parent window when positioning dialog

# Valheim server port configuration
VALHEIM_DEFAULT_PORT_MIN = 1024             # Minimum allowed port for Valheim server
VALHEIM_DEFAULT_PORT_MAX = 65535            # Maximum allowed port for Valheim server
VALHEIM_DEFAULT_PORT_BASE = 2456            # Base port number for Valheim (default)
VALHEIM_PORT_OFFSET_QUERY = 1               # Offset for query port (+1 from base)
VALHEIM_PORT_OFFSET_ADDITIONAL = 2          # Offset for additional port (+2 from base)
VALHEIM_PASSWORD_MIN_LENGTH = 5             # Minimum password length required by Valheim

# Font sizes for UI elements
FONT_SIZE_CONFIG_TITLE = 18                 # Font size for main configuration dialog title
FONT_SIZE_GROUP_HEADER = 14                 # Font size for group box headers (Server/Network)
FONT_SIZE_INPUT_FIELDS = 12                 # Font size for input fields and labels
FONT_SIZE_INFO_TEXT = 10                    # Font size for information/help text
FONT_SIZE_BUTTON_LARGE = 12                 # Font size for dialog buttons

# Layout and spacing constants
LAYOUT_SPACING_LARGE = 20                   # Large spacing between major sections
LAYOUT_SPACING_MEDIUM = 15                  # Medium spacing between form elements
LAYOUT_SPACING_SMALL = 10                   # Small spacing for margins and padding
GROUP_BOX_MARGIN_TOP = 10                   # Top margin for group boxes
GROUP_BOX_PADDING_TOP = 10                  # Top padding inside group boxes
TITLE_PADDING_HORIZONTAL = 5                # Horizontal padding for group box titles
INFO_TEXT_MAX_HEIGHT = 80                   # Maximum height for information text areas (reduced from 120)

# Border and visual styling
BORDER_WIDTH_STANDARD = 2                   # Standard border width for UI elements
BORDER_RADIUS_STANDARD = 8                  # Standard border radius for buttons and groups
BORDER_RADIUS_SMALL = 6                     # Small border radius for input fields
BUTTON_PADDING_VERTICAL = 12                # Vertical padding inside buttons
BUTTON_PADDING_HORIZONTAL = 20              # Horizontal padding inside buttons
INPUT_FIELD_PADDING = 8                     # Padding inside input fields
INPUT_FIELD_MIN_WIDTH = 200                 # Minimum width for input fields to ensure proper display

# Step tracking and installation
SETUP_STEP_EXISTING_INDEX = 0               # Step index for existing installation
SETUP_STEP_NEW_CONFIG_INDEX = 2             # Step index for new installation configuration
SETUP_STEP_INCREMENT = 1                    # Standard increment for step progression

# Progress and system constants
PROGRESS_INITIAL_VALUE = 10                 # Initial progress percentage for setup
PROGRESS_COMPLETE_VALUE = 100               # Progress value indicating completion
SYS_PATH_INSERT_INDEX = 0                   # Index for inserting paths into sys.path

# Game-specific constants
VALHEIM_MAX_PLAYERS = 10                    # Maximum players supported by Valheim server
VALHEIM_DOWNLOAD_SIZE_GB = 2                # Approximate download size in GB
VALHEIM_DOWNLOAD_SIZE_MB = 10               # SteamCMD download size in MB
SETUP_WINDOW_MIN_WIDTH = 900                # Minimum width for setup windows
SETUP_WINDOW_MIN_HEIGHT = 700               # Minimum height for setup windows
SETUP_WINDOW_DEFAULT_WIDTH = 1200           # Default width for setup windows
SETUP_WINDOW_DEFAULT_HEIGHT = 900           # Default height for setup windows

# Header icon scaling
HEADER_ICON_WIDTH = 100                     # Width for header game icons
HEADER_ICON_HEIGHT = 60                     # Height for header game icons

# Setup window font sizes
FONT_SIZE_SETUP_TITLE = 24                  # Font size for setup window title
FONT_SIZE_SETUP_DESCRIPTION = 14            # Font size for setup descriptions
FONT_SIZE_SETUP_STEP_HEADER = 16            # Font size for step headers
FONT_SIZE_SETUP_STEP_CONTENT = 14           # Font size for step content text
FONT_SIZE_SETUP_STATUS = 16                 # Font size for status labels
FONT_SIZE_SETUP_BUTTON = 14                 # Font size for setup buttons
FONT_SIZE_SETUP_CLOSE_BUTTON = 12           # Font size for close button

# UI explanation font sizes
FONT_SIZE_EXPLANATION_HEADER = 18           # Font size for explanation headers
FONT_SIZE_EXPLANATION_STATUS = 14           # Font size for status information
FONT_SIZE_EXPLANATION_CONFIG = 14           # Font size for configuration instructions
FONT_SIZE_EXPLANATION_OPTIONS = 12          # Font size for option descriptions
FONT_SIZE_EXPLANATION_DEFAULTS = 11         # Font size for default preview text
FONT_SIZE_EXPLANATION_ACTION = 13           # Font size for action instructions

# Margin and padding for explanations
EXPLANATION_MARGIN_STANDARD = 15            # Standard margin for explanation elements
EXPLANATION_MARGIN_LARGE = 15               # Large margin for major sections
EXPLANATION_MARGIN_SMALL = 5                # Small margin for minor spacing
EXPLANATION_PADDING_STANDARD = 15           # Standard padding for explanation boxes
EXPLANATION_PADDING_SMALL = 10              # Small padding for compact elements
EXPLANATION_PADDING_LARGE = 12              # Large padding for action boxes

import os
import sys
from PyQt5.QtWidgets import (QCheckBox, QLabel, QDialog, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QSpinBox,
                            QGroupBox, QFormLayout, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread
from .base_setup_window import BaseServerSetupWindow

# Import styles from parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from styles import Colors, Layout

# Import the Valheim startup script
sys.path.insert(0, os.path.join(parent_dir, "scripts"))
from scripts.valheim_server_startup_script import (
    download_steamcmd,
    install_or_update_valheim_server,
    setup_upnp_port_forwarding,
    start_valheim_server,
    configure_valheim_firewall,
    create_valheim_server_config,
    is_valheim_server_installed
)

# Import configuration manager
sys.path.insert(0, os.path.join(parent_dir, "utils"))
from utils.config_manager import config_manager


class ValheimConfigDialog(QDialog):
    """
    Dialog for configuring Valheim server settings.
    
    Provides a user-friendly interface for configuring:
    - Server name and password
    - World name and settings
    - Port configuration
    - Network and firewall options
    """
    
    def __init__(self, parent=None):
        # Ensure dialog is created on the main thread
        if QThread.currentThread() != parent.thread() if parent else False:
            raise RuntimeError("ValheimConfigDialog must be created on the main thread")
            
        super().__init__(parent)
        self.setWindowTitle("🏰 Configure Valheim Server")
        self.setModal(True)
        
        # Make dialog resizable with size constraints instead of fixed size
        self.setMinimumSize(VALHEIM_CONFIG_DIALOG_WIDTH, VALHEIM_CONFIG_DIALOG_MIN_HEIGHT)
        self.setMaximumSize(VALHEIM_CONFIG_DIALOG_WIDTH, VALHEIM_CONFIG_DIALOG_MAX_HEIGHT)
        self.resize(VALHEIM_CONFIG_DIALOG_WIDTH, VALHEIM_CONFIG_DIALOG_HEIGHT)
        
        self.setStyleSheet(f"background-color: {Colors.BACKGROUND_DARK};")
        
        # Server configuration values - load from persistent storage or use defaults
        saved_config = config_manager.load_server_config('Valheim')
        if saved_config:
            self.server_config = saved_config
        else:
            self.server_config = config_manager.get_default_valheim_config()
        
        # Initialize UI first
        self.init_ui()
        
        # Ensure proper sizing after UI initialization
        self.adjustSize()  # Let Qt calculate the optimal size
        self.setMinimumSize(self.sizeHint())  # Set minimum size based on content
        
        # Now position the dialog after size has been calculated
        self.position_dialog_at_top()
    
    def position_dialog_at_top(self):
        """Position the dialog at the top of the parent window after size calculation."""
        parent = self.parent()
        if parent:
            parent_geometry = parent.geometry()
            # Position dialog at top-center of parent window
            dialog_x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            dialog_y = parent_geometry.y() + VALHEIM_CONFIG_DIALOG_TOP_OFFSET
            
            # Ensure dialog stays within screen bounds
            screen = parent.screen() if hasattr(parent, 'screen') else None
            if screen:
                screen_geometry = screen.availableGeometry()
                # Clamp X position to stay within screen bounds
                dialog_x = max(screen_geometry.x(), min(dialog_x, screen_geometry.x() + screen_geometry.width() - self.width()))
                # Clamp Y position to stay within screen bounds
                dialog_y = max(screen_geometry.y(), min(dialog_y, screen_geometry.y() + screen_geometry.height() - self.height()))
            
            self.move(dialog_x, dialog_y)
    
    def init_ui(self):
        """Initialize the configuration dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(LAYOUT_SPACING_MEDIUM)  # Reduced from LAYOUT_SPACING_LARGE
        layout.setContentsMargins(LAYOUT_SPACING_MEDIUM, LAYOUT_SPACING_SMALL, LAYOUT_SPACING_MEDIUM, LAYOUT_SPACING_SMALL)
        layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)  # Ensure layout calculates minimum size properly
        
        # Title
        title = QLabel("🏰 Valheim Server Configuration")
        title.setFont(QFont('Segoe UI', FONT_SIZE_CONFIG_TITLE, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-bottom: {LAYOUT_SPACING_SMALL}px;")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)  # Allow word wrapping if needed
        layout.addWidget(title)
        
        # Server Settings Group
        server_group = QGroupBox("⚔️ Server Settings")
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
        server_form.setSpacing(LAYOUT_SPACING_SMALL)  # Reduced from LAYOUT_SPACING_MEDIUM
        server_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)  # Allow fields to expand properly
        server_form.setRowWrapPolicy(QFormLayout.DontWrapRows)  # Keep labels and fields on same row
        
        # World Name
        self.world_name_input = QLineEdit(self.server_config['world_name'])
        self.world_name_input.setFont(QFont('Segoe UI', FONT_SIZE_INPUT_FIELDS))
        self.world_name_input.setMinimumWidth(INPUT_FIELD_MIN_WIDTH)  # Ensure minimum width for proper display
        self.world_name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BACKGROUND_MEDIUM};
                border: {BORDER_WIDTH_STANDARD}px solid {Colors.GRAY_MEDIUM};
                border-radius: {BORDER_RADIUS_SMALL}px;
                padding: {INPUT_FIELD_PADDING}px;
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        server_form.addRow("🗺️ World Name:", self.world_name_input)
        
        # Server Name
        self.server_name_input = QLineEdit(self.server_config['server_name'])
        self.server_name_input.setFont(QFont('Segoe UI', FONT_SIZE_INPUT_FIELDS))
        self.server_name_input.setMinimumWidth(INPUT_FIELD_MIN_WIDTH)  # Ensure minimum width for proper display
        self.server_name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BACKGROUND_MEDIUM};
                border: {BORDER_WIDTH_STANDARD}px solid {Colors.GRAY_MEDIUM};
                border-radius: {BORDER_RADIUS_SMALL}px;
                padding: {INPUT_FIELD_PADDING}px;
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        server_form.addRow("🏰 Server Name:", self.server_name_input)
        
        # Password
        self.password_input = QLineEdit(self.server_config['password'])
        self.password_input.setFont(QFont('Segoe UI', FONT_SIZE_INPUT_FIELDS))
        self.password_input.setMinimumWidth(INPUT_FIELD_MIN_WIDTH)  # Ensure minimum width for proper display
        self.password_input.setEchoMode(QLineEdit.Normal)  # Show password text instead of dots
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BACKGROUND_MEDIUM};
                border: {BORDER_WIDTH_STANDARD}px solid {Colors.GRAY_MEDIUM};
                border-radius: {BORDER_RADIUS_SMALL}px;
                padding: {INPUT_FIELD_PADDING}px;
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        server_form.addRow(f"🔒 Password (min {VALHEIM_PASSWORD_MIN_LENGTH} chars):", self.password_input)
        
        # Port
        self.port_input = QSpinBox()
        self.port_input.setRange(VALHEIM_DEFAULT_PORT_MIN, VALHEIM_DEFAULT_PORT_MAX)
        self.port_input.setValue(self.server_config['port'])
        self.port_input.setFont(QFont('Segoe UI', FONT_SIZE_INPUT_FIELDS))
        self.port_input.setStyleSheet(f"""
            QSpinBox {{
                background-color: {Colors.BACKGROUND_MEDIUM};
                border: {BORDER_WIDTH_STANDARD}px solid {Colors.GRAY_MEDIUM};
                border-radius: {BORDER_RADIUS_SMALL}px;
                padding: {INPUT_FIELD_PADDING}px;
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        server_form.addRow("🌐 Port:", self.port_input)
        
        # Public Server
        self.public_checkbox = QCheckBox("Make server visible in public server list")
        self.public_checkbox.setChecked(self.server_config['public_server'])
        self.public_checkbox.setFont(QFont('Segoe UI', FONT_SIZE_INPUT_FIELDS))
        self.public_checkbox.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        server_form.addRow("📡 Visibility:", self.public_checkbox)
        
        layout.addWidget(server_group)
        
        # Network Settings Group
        network_group = QGroupBox("🌐 Network Configuration")
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
        
        network_form = QFormLayout(network_group)
        network_form.setSpacing(LAYOUT_SPACING_SMALL)  # Reduced from LAYOUT_SPACING_MEDIUM
        network_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)  # Allow fields to expand properly
        network_form.setRowWrapPolicy(QFormLayout.DontWrapRows)  # Keep labels and fields on same row
        
        # Firewall Configuration
        self.firewall_checkbox = QCheckBox("Configure Windows Firewall rules for Valheim")
        self.firewall_checkbox.setChecked(self.server_config['configure_firewall'])
        self.firewall_checkbox.setFont(QFont('Segoe UI', FONT_SIZE_INPUT_FIELDS))
        self.firewall_checkbox.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        network_form.addRow("🛡️ Firewall:", self.firewall_checkbox)
        
        # UPnP Configuration
        self.upnp_checkbox = QCheckBox("Enable automatic port forwarding (UPnP)")
        self.upnp_checkbox.setChecked(self.server_config['enable_upnp'])
        self.upnp_checkbox.setFont(QFont('Segoe UI', FONT_SIZE_INPUT_FIELDS))
        self.upnp_checkbox.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        network_form.addRow("🔄 UPnP:", self.upnp_checkbox)
        
        layout.addWidget(network_group)
        
        # Information Text - Using QLabel instead of QTextEdit to avoid threading issues
        info_text = QLabel()
        info_text.setWordWrap(True)
        info_text.setMaximumHeight(INFO_TEXT_MAX_HEIGHT)
        info_text.setFont(QFont('Segoe UI', FONT_SIZE_INFO_TEXT))
        info_text.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.BACKGROUND_MEDIUM};
                border: {BORDER_WIDTH_STANDARD}px solid {Colors.GRAY_MEDIUM};
                border-radius: {BORDER_RADIUS_SMALL}px;
                padding: {INPUT_FIELD_PADDING}px;
                color: {Colors.TEXT_SECONDARY};
            }}
        """)
        info_text.setText(
            "📋 Configuration Notes:\n"
            f"• Firewall: Allows Valheim traffic on ports {VALHEIM_DEFAULT_PORT_BASE}-{VALHEIM_DEFAULT_PORT_BASE + VALHEIM_PORT_OFFSET_ADDITIONAL} UDP\n"
            f"• UPnP: Auto-configures router port forwarding • Password: Min {VALHEIM_PASSWORD_MIN_LENGTH} chars required"
        )
        layout.addWidget(info_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Advanced Button
        advanced_button = QPushButton("⚙️ Advanced Settings")
        advanced_button.setFont(QFont('Segoe UI', FONT_SIZE_BUTTON_LARGE))
        advanced_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GRAY_MEDIUM};
                border: none;
                border-radius: {BORDER_RADIUS_STANDARD}px;
                color: {Colors.TEXT_PRIMARY};
                padding: {BUTTON_PADDING_VERTICAL}px {BUTTON_PADDING_HORIZONTAL}px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BACKGROUND_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.GRAY_LIGHT};
            }}
        """)
        advanced_button.clicked.connect(self.show_advanced_settings)
        button_layout.addWidget(advanced_button)
        
        button_layout.addStretch()
        
        # Cancel Button
        cancel_button = QPushButton("❌ Cancel")
        cancel_button.setFont(QFont('Segoe UI', FONT_SIZE_BUTTON_LARGE))
        cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GRAY_MEDIUM};
                border: none;
                border-radius: {BORDER_RADIUS_STANDARD}px;
                color: {Colors.TEXT_PRIMARY};
                padding: {BUTTON_PADDING_VERTICAL}px {BUTTON_PADDING_HORIZONTAL}px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BACKGROUND_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.GRAY_LIGHT};
            }}
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # OK Button
        ok_button = QPushButton("✅ Start Server")
        ok_button.setFont(QFont('Segoe UI', FONT_SIZE_BUTTON_LARGE))
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                border: none;
                border-radius: 8px;
                color: white;
                padding: 12px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        ok_button.clicked.connect(self.accept_config)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
    
    def show_advanced_settings(self):
        """Show advanced configuration options."""
        QMessageBox.information(self, "Advanced Settings", 
                              "🔧 Advanced settings will be available in a future update.\n\n"
                              "Current configuration covers the most common server setup options. "
                              "For now, you can manually edit the server configuration files after installation.")
    
    def accept_config(self):
        """Validate and accept the configuration."""
        # Validate password
        password = self.password_input.text().strip()
        if len(password) < VALHEIM_PASSWORD_MIN_LENGTH:
            QMessageBox.warning(self, "Invalid Password", 
                              f"🔒 Password must be at least {VALHEIM_PASSWORD_MIN_LENGTH} characters long for Valheim compatibility.")
            return
        
        # Validate server name
        server_name = self.server_name_input.text().strip()
        if not server_name:
            QMessageBox.warning(self, "Invalid Server Name", 
                              "🏰 Server name cannot be empty.")
            return
        
        # Validate world name
        world_name = self.world_name_input.text().strip()
        if not world_name:
            QMessageBox.warning(self, "Invalid World Name", 
                              "🗺️ World name cannot be empty.")
            return
        
        # Update configuration
        self.server_config.update({
            'world_name': world_name,
            'server_name': server_name,
            'password': password,
            'port': self.port_input.value(),
            'public_server': self.public_checkbox.isChecked(),
            'configure_firewall': self.firewall_checkbox.isChecked(),
            'enable_upnp': self.upnp_checkbox.isChecked()
        })
        
        # Save configuration to persistent storage
        config_manager.save_server_config('Valheim', self.server_config)
        
        self.accept()
    
    def get_config(self):
        """Get the server configuration."""
        return self.server_config


class ValheimServerSetupWindow(BaseServerSetupWindow):
    """
    Valheim-specific server setup window with Viking-themed messaging.
    
    This class extends the base setup window to provide Valheim-specific
    installation steps, configuration options, and user guidance. It handles
    the complete server setup process from SteamCMD installation through
    server launch and verification.
    
    Key Features:
    - Valheim-specific installation steps and messaging
    - UPnP port forwarding for ports 2456-2458
    - World generation and persistence information
    - Viking-themed status messages for better user experience
    - Integration with Valheim automation scripts
    """
    
    def __init__(self, game):
        """
        Initialize the Valheim setup window.
        
        Args:
            game: Game object containing Valheim metadata and configuration
        """
        self.port_checkbox = None
        self.server_config = None  # Initialize server configuration
        super().__init__(game)
    
    def get_setup_steps(self):
        """
        Define the setup steps specific to Valheim server installation.
        
        Checks if Valheim is already installed and skips installation steps
        if it exists, going directly to the configuration step.
        
        Returns a list of setup steps with Viking-themed descriptions and
        appropriate confirmation prompts for the Valheim installation process.
        
        Returns:
            list: List of setup step dictionaries containing step configuration
        """
        # Check if Valheim server is already installed
        if is_valheim_server_installed():
            # Skip installation steps, go directly to configuration
            return [
                {
                    'name': 'Configure & Launch Existing Server',
                    'description': 'Valheim dedicated server is already installed! Configure your Viking realm settings and launch your server. Your existing world data and configurations will be preserved.',
                    'function': self.configure_and_launch_server,
                    'requires_confirmation': False,
                    'confirmation_text': None,
                    'interactive': True
                }
            ]
        
        # Full installation process for new installations
        return [
            {
                'name': 'Install SteamCMD',
                'description': 'SteamCMD is required to download and manage Steam-based game servers. This step will download and install SteamCMD if it is not already present on your system. SteamCMD is used by many games and will be preserved for future server installations.',
                'function': download_steamcmd,
                'requires_confirmation': True,
                'confirmation_text': 'This will download and install SteamCMD (~10MB download). Do you want to proceed?'
            },
            {
                'name': 'Install Valheim Server',
                'description': f'Download and install the Valheim Dedicated Server files from Steam. The Valheim server is relatively lightweight (~{VALHEIM_DOWNLOAD_SIZE_GB}GB) compared to other survival games. This includes all necessary files for hosting up to {VALHEIM_MAX_PLAYERS} Viking warriors in your procedurally generated world.',
                'function': install_or_update_valheim_server,
                'requires_confirmation': True,
                'confirmation_text': f'This will download the Valheim server files (~{VALHEIM_DOWNLOAD_SIZE_GB}GB download). The server supports up to {VALHEIM_MAX_PLAYERS} concurrent players. Do you want to proceed?'
            },
            {
                'name': 'Configure Viking Realm',
                'description': 'Configure final server settings including network access and launch your Viking realm. Your server will create a default world called "Dedicated" where players can begin their Norse adventure, build settlements, and face the challenges of Valheim together.',
                'function': self.configure_and_launch_server,
                'requires_confirmation': False,  # We'll handle confirmation in the final step
                'confirmation_text': None,
                'interactive': True  # Mark this as an interactive step that shouldn't run in worker thread
            }
        ]
    
    def get_game_specific_ui_elements(self):
        """
        Return Valheim-specific UI elements for the current setup step.
        
        Provides step-specific UI components including configuration information
        and instructions for the final setup step. Shows different content based
        on whether the server is already installed.
        
        Returns:
            list: List of QWidget elements for the current step
        """
        elements = []
        
        # Check if this is the configuration step (either first step for existing install or last for new install)
        is_config_step = (
            (len(self.setup_steps) == SETUP_STEP_INCREMENT and self.current_step == SETUP_STEP_EXISTING_INDEX) or  # Existing installation
            (len(self.setup_steps) > SETUP_STEP_INCREMENT and self.current_step == SETUP_STEP_NEW_CONFIG_INDEX)      # New installation
        )
        
        if is_config_step:
            # Show different header based on installation status
            if is_valheim_server_installed():
                # Server already installed
                explanation = QLabel("🏰 Configure Existing Viking Realm")
                explanation.setFont(QFont('Segoe UI', FONT_SIZE_EXPLANATION_HEADER, QFont.Bold))
                explanation.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin: {EXPLANATION_MARGIN_STANDARD}px {TITLE_PADDING_HORIZONTAL}px;")
                explanation.setAlignment(Qt.AlignCenter)
                elements.append(explanation)
                
                # Status info for existing installation
                status_info = QLabel("✅ Valheim dedicated server is already installed and ready!")
                status_info.setFont(QFont('Segoe UI', FONT_SIZE_EXPLANATION_STATUS, QFont.Bold))
                status_info.setStyleSheet(f"color: #2ecc71; margin: {LAYOUT_SPACING_SMALL}px {TITLE_PADDING_HORIZONTAL}px;")
                status_info.setWordWrap(True)
                elements.append(status_info)
                
                config_info = QLabel("⚙️ Configure your server settings and launch your Viking realm:")
                config_info.setFont(QFont('Segoe UI', FONT_SIZE_EXPLANATION_CONFIG, QFont.Bold))
                config_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin: {LAYOUT_SPACING_SMALL}px {TITLE_PADDING_HORIZONTAL}px;")
                config_info.setWordWrap(True)
                elements.append(config_info)
            else:
                # New installation
                explanation = QLabel("🏰 Viking Realm Configuration")
                explanation.setFont(QFont('Segoe UI', FONT_SIZE_EXPLANATION_HEADER, QFont.Bold))
                explanation.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin: {EXPLANATION_MARGIN_STANDARD}px {TITLE_PADDING_HORIZONTAL}px;")
                explanation.setAlignment(Qt.AlignCenter)
                elements.append(explanation)
                
                # Configuration info
                config_info = QLabel("⚙️ When you click 'Continue', you'll be able to customize your server settings:")
                config_info.setFont(QFont('Segoe UI', FONT_SIZE_EXPLANATION_CONFIG, QFont.Bold))
                config_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin: {LAYOUT_SPACING_SMALL}px {TITLE_PADDING_HORIZONTAL}px;")
                config_info.setWordWrap(True)
                elements.append(config_info)
            
            # Configuration options list
            options_text = """
🗺️ <b>World Name:</b> Choose a custom name for your Viking world<br>
🏰 <b>Server Name:</b> Set the display name for your server<br>
🔒 <b>Password:</b> Protect your server with a custom password<br>
🌐 <b>Port Settings:</b> Configure network port (default: 2456)<br>
📡 <b>Visibility:</b> Make server public or private<br>
🛡️ <b>Firewall:</b> Automatically configure Windows Firewall<br>
🔄 <b>Port Forwarding:</b> Auto-configure router with UPnP
            """
            
            options_label = QLabel(options_text)
            options_label.setFont(QFont('Segoe UI', FONT_SIZE_EXPLANATION_OPTIONS))
            options_label.setStyleSheet(f"""
                color: {Colors.TEXT_PRIMARY}; 
                margin: {LAYOUT_SPACING_SMALL}px {EXPLANATION_MARGIN_STANDARD}px; 
                padding: {EXPLANATION_PADDING_STANDARD}px; 
                background-color: {Colors.BACKGROUND_MEDIUM}; 
                border-radius: {BORDER_RADIUS_STANDARD}px;
                border: {BORDER_WIDTH_STANDARD}px solid {Colors.GRAY_MEDIUM};
            """)
            options_label.setWordWrap(True)
            elements.append(options_label)
            
            # Preview current defaults
            defaults_info = QLabel("� Default configuration preview:")
            defaults_info.setFont(QFont('Segoe UI', FONT_SIZE_EXPLANATION_CONFIG, QFont.Bold))
            defaults_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin: {EXPLANATION_MARGIN_STANDARD}px {TITLE_PADDING_HORIZONTAL}px {TITLE_PADDING_HORIZONTAL}px {TITLE_PADDING_HORIZONTAL}px;")
            elements.append(defaults_info)
            
            defaults_text = f"""
• World: "DedicatedWorld" | Server: "Valheim Server"<br>
• Port: {VALHEIM_DEFAULT_PORT_BASE} | Password: Protected | Public: Yes<br>
• Firewall & UPnP: Enabled (can be customized)
            """
            
            defaults_label = QLabel(defaults_text)
            defaults_label.setFont(QFont('Segoe UI', FONT_SIZE_EXPLANATION_DEFAULTS))
            defaults_label.setStyleSheet(f"""
                color: {Colors.TEXT_SECONDARY}; 
                margin: {TITLE_PADDING_HORIZONTAL}px {EXPLANATION_MARGIN_STANDARD}px {EXPLANATION_MARGIN_STANDARD}px {EXPLANATION_MARGIN_STANDARD}px; 
                padding: {EXPLANATION_PADDING_SMALL}px; 
                background-color: {Colors.BACKGROUND_MEDIUM}; 
                border-radius: {BORDER_RADIUS_SMALL}px;
                font-style: italic;
            """)
            defaults_label.setWordWrap(True)
            elements.append(defaults_label)
            
            # Action instruction - different text based on installation status
            if is_valheim_server_installed():
                action_text = "🚀 Click 'Continue' to configure and launch your existing Viking realm!"
            else:
                action_text = "🚀 Click 'Continue' to open the configuration dialog and customize your Viking realm!"
            
            action_info = QLabel(action_text)
            action_info.setFont(QFont('Segoe UI', FONT_SIZE_EXPLANATION_ACTION, QFont.Bold))
            action_info.setStyleSheet(f"""
                color: #2ecc71; 
                margin: {EXPLANATION_MARGIN_STANDARD}px {TITLE_PADDING_HORIZONTAL}px; 
                padding: {EXPLANATION_PADDING_LARGE}px;
                background-color: rgba(46, 204, 113, 0.1);
                border-radius: {BORDER_RADIUS_STANDARD}px;
                border: {BORDER_WIDTH_STANDARD}px solid #2ecc71;
            """)
            action_info.setWordWrap(True)
            action_info.setAlignment(Qt.AlignCenter)
            elements.append(action_info)
        
        return elements
    
    def configure_and_launch_server(self):
        """
        Handle the configure and launch step preparation.
        
        Opens the configuration dialog for the user to set up their Valheim server
        settings including server name, password, world configuration, and network options.
        
        Returns:
            bool: True to proceed to final step completion
        """
        self.log_message("🏰 Ready to configure your Viking realm...")
        self.log_message("⚙️ Opening server configuration dialog...")
        self.log_message("📋 Please complete the configuration form to customize your server...")
        
        # Show configuration dialog directly on main thread
        # Since this method is called from the UI thread, it's safe to create the dialog here
        config_dialog = ValheimConfigDialog(self)
        
        if config_dialog.exec_() == QDialog.Accepted:
            # Store the configuration for use in final step
            self.server_config = config_dialog.get_config()
            self.log_message("✅ Server configuration completed!")
            self.log_message("📊 Configuration Summary:")
            self.log_message(f"   🗺️ World: {self.server_config['world_name']}")
            self.log_message(f"   🏰 Server: {self.server_config['server_name']}")
            self.log_message(f"   🌐 Port: {self.server_config['port']}")
            self.log_message(f"   📡 Public: {'Yes' if self.server_config['public_server'] else 'No'}")
            self.log_message(f"   🛡️ Firewall: {'Enabled' if self.server_config['configure_firewall'] else 'Disabled'}")
            self.log_message(f"   🔄 UPnP: {'Enabled' if self.server_config['enable_upnp'] else 'Disabled'}")
            self.log_message("⚔️ Preparing for Norse adventure and server launch...")
            return True
        else:
            self.log_message("❌ Server configuration cancelled.")
            self.log_message("ℹ️ Please configure your server to continue.")
            self.log_message("💡 Click 'Continue' again to reopen the configuration dialog.")
            return False
    
    def handle_final_step_completion(self):
        """
        Handle Valheim-specific final step completion.
        
        Performs the actual server configuration including:
        - Firewall configuration (if selected)
        - UPnP port forwarding setup (if selected)
        - Server configuration file creation
        - Server startup with user settings
        
        Returns:
            bool: True if server setup and launch succeeded, False otherwise
        """
        self.log_message("🚀 Launching your Viking realm...")
        self.log_message("⚡ Summoning Odin's power for server configuration...")
        
        # Get configuration (set during configure_and_launch_server)
        if not hasattr(self, 'server_config'):
            self.log_message("❌ No server configuration found!")
            return False
        
        config = self.server_config
        success = True
        
        # Configure firewall if selected
        if config['configure_firewall']:
            self.log_message("🛡️ Configuring Windows Firewall for Valheim...")
            self.log_message(f"🔓 Adding firewall rules for ports {config['port']}-{config['port']+2} UDP...")
            try:
                firewall_success = configure_valheim_firewall(config['port'])
                if firewall_success:
                    self.log_message("✅ Firewall configured successfully!")
                    self.log_message("🔥 Valheim traffic is now allowed through Windows Firewall!")
                else:
                    self.log_message("⚠️ Firewall configuration failed!")
                    self.log_message("🛠️ You may need to manually allow Valheim through Windows Firewall")
            except Exception as e:
                self.log_message(f"❌ Firewall configuration error: {str(e)}")
                self.log_message("ℹ️ Server will continue without firewall configuration")
        
        # Configure port forwarding if selected
        if config['enable_upnp']:
            self.log_message("🌐 Configuring UPnP port forwarding for external Vikings...")
            self.log_message(f"📡 Opening portals (ports {config['port']}-{config['port']+2} UDP) through your router...")
            try:
                port_success = setup_upnp_port_forwarding(config['port'])
                if port_success:
                    self.log_message("✅ Port forwarding configured successfully!")
                    self.log_message("🌍 External Vikings can now reach your realm!")
                else:
                    self.log_message("⚠️ Port forwarding failed, but fear not!")
                    self.log_message(f"🛠️ You can configure it manually: Forward UDP ports {config['port']}-{config['port']+2}")
                    self.log_message(f"📋 Main port: {config['port']} UDP, Query port: {config['port']+1} UDP, Additional: {config['port']+2} UDP")
            except Exception as e:
                self.log_message(f"❌ Port forwarding error: {str(e)}")
                self.log_message("ℹ️ Server will be accessible locally")
        else:
            self.log_message("🏠 Port forwarding skipped - realm will be accessible locally only.")
            self.log_message("ℹ️ Vikings on your local network can still join the adventure!")
        
        # Create server configuration file
        self.log_message("📄 Creating server configuration files...")
        try:
            config_success = create_valheim_server_config(config)
            if config_success:
                self.log_message("✅ Server configuration files created!")
            else:
                self.log_message("⚠️ Could not create configuration files, using defaults")
        except Exception as e:
            self.log_message(f"❌ Configuration file error: {str(e)}")
            self.log_message("ℹ️ Server will use default configuration")
        
        # Start the server
        self.log_message("🔥 Igniting the hearth and starting Valheim dedicated server...")
        self.log_message("🗡️ Preparing weapons, tools, and Viking provisions...")
        try:
            server_success = start_valheim_server(
                world_name=config['world_name'],
                server_name=config['server_name'],
                password=config['password'],
                public_server=config['public_server'],
                port=config['port']
            )
            if server_success:
                self.log_message("🎉 Valheim dedicated server started successfully!")
                self.log_message("🖥️ The server is now running in a separate command prompt window!")
                self.log_message("🏰 Your Viking realm is now active and ready for adventure!")
                self.log_message("⚔️ Up to 10 warriors can now join your Norse world!")
                self.log_message(f"🗺️ World '{config['world_name']}' is ready for exploration!")
                self.log_message(f"🏰 Server '{config['server_name']}' is broadcasting on port {config['port']}")
                self.log_message("💾 Player progress and world changes will be automatically saved.")
                self.log_message("🔧 To stop the server: Close the server console window or press Ctrl+C in it.")
                if config['public_server']:
                    self.log_message("🌐 Server is visible in the public server list!")
                self.log_message("🌟 May the gods guide your Viking adventures!")
                self.log_message("=" * 60)
            else:
                self.log_message("❌ Failed to start Valheim server!")
                self.log_message("🛠️ Check the error messages above for troubleshooting.")
                success = False
        except Exception as e:
            self.log_message(f"❌ Server startup error: {str(e)}")
            self.log_message("🔧 Please check your configuration and try again.")
            success = False
        
        return success
    
    def add_control_buttons(self, layout):
        """Add control buttons - using base implementation (no custom delete button)"""
        # Use the base implementation which doesn't include delete functionality
        super().add_control_buttons(layout)
