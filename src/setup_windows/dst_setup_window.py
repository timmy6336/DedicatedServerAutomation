import os
import sys
# ================== DST SETUP CONSTANTS ==================
# UI styling constants
EXPLANATION_FONT_SIZE = 16               # Font size for main explanation text
CHECKBOX_FONT_SIZE = 14                  # Font size for checkbox labels
INFO_FONT_SIZE = 12                      # Font size for informational text
MARGIN_LARGE = 15                        # Large margin size for spacing
MARGIN_MEDIUM = 10                       # Medium margin size for spacing
MARGIN_SMALL = 5                         # Small margin size for spacing
PADDING_STANDARD = 10                    # Standard padding for elements

# Font configuration
FONT_FAMILY = 'Segoe UI'                 # Default font family for UI elements

# DST server configuration
DST_DEFAULT_MASTER_PORT = 11000          # Default port for DST Master shard
DST_DEFAULT_CAVES_PORT = 11001           # Default port for DST Caves shard

# UI layout and formatting
SEPARATOR_LINE_LENGTH = 50               # Length of separator lines in logs

from PyQt5.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton,
    QTextEdit, QWidget, QApplication, QLineEdit, QSpinBox,
    QGroupBox, QFormLayout, QMessageBox
)
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtCore import QUrl
from .base_setup_window import BaseServerSetupWindow
import os
import sys

# Import styles from parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from styles import Colors

# Import the startup script
sys.path.insert(0, os.path.join(parent_dir, "scripts"))
from scripts.dst_server_startup_script import (
    download_steamcmd,
    install_or_update_dst_server,
    setup_upnp_port_forwarding,
    start_dst_server,
    create_dst_configuration,
    validate_server_token
)

class DSTServerSetupWindow(BaseServerSetupWindow):
    """Don't Starve Together-specific server setup window"""
    
    def __init__(self, game):
        self.port_checkbox = None
        self.server_name_input = None
        self.server_description_input = None
        self.max_players_input = None
        self.server_password_input = None
        self.server_token_input = None
        self.enable_caves_checkbox = None
        super().__init__(game)
    
    def get_setup_steps(self):
        """Define the setup steps for Don't Starve Together"""
        return [
            {
            'name': '🛠️ Install SteamCMD',
            'description': (
                "<b>SteamCMD</b> is required to download and manage Steam-based game servers.<br>"
                "This step will download and install SteamCMD if it is not already present on your system."
            ),
            'function': download_steamcmd,
            'requires_confirmation': True,
            'confirmation_text': (
                "<b>This will download and install SteamCMD.</b><br>"
                "Do you want to proceed?"
            )
            },
            {
            'name': 'Install DST Server',
            'description': (
                "<b>⬇️ Download and install the Don't Starve Together Dedicated Server files from Steam.</b><br><br>"
                "<u>🌍 About Don't Starve Together:</u><br>"
                "Don't Starve Together is a multiplayer survival game where players must work together to survive in a strange and hostile world. Features crafting, base building, seasonal cycles, and challenging boss fights with up to 6 players cooperatively.<br><br>"
                "<u>🖥️ System Requirements for Dedicated Server:</u><br>"
                "<b>Minimum Requirements:</b><br>"
                "&bull; 🧠 RAM: 1GB (for 2-4 players)<br>"
                "&bull; 🖥️ CPU: 1.7GHz+ (single core sufficient)<br>"
                "&bull; 🎮 GPU: Not required (headless server)<br>"
                "&bull; 💾 Storage: 3GB available space<br>"
                "&bull; 🌐 Network: Broadband connection<br><br>"
                "<b>Recommended for 6 Players:</b><br>"
                "&bull; 🧠 RAM: 4GB+ for stable performance<br>"
                "&bull; 🖥️ CPU: 2.0GHz+ multi-core for Master + Caves<br>"
                "&bull; 🎮 GPU: Not required (dedicated server runs headless)<br>"
                "&bull; 💾 Storage: 5GB+ SSD for world saves and mods<br>"
                "&bull; 🚀 Upload Speed: 5+ Mbps for smooth multiplayer<br><br>"
                "<u>📦 Download Details:</u><br>"
                "&bull; 📁 Size: ~1-2GB server files<br>"
                "&bull; 💾 World Save Size: 50-200MB (grows with exploration)<br>"
                "&bull; 👥 Supports: Up to 6 concurrent players<br>"
                "&bull; 🏗️ Features: Dual-world system (Master + Caves), seasonal gameplay<br><br>"
                "<u>🎮 Unique DST Features:</u><br>"
                "&bull; 🌍 <b>Master World:</b> Surface world with seasons, bosses, biomes<br>"
                "&bull; 🕳️ <b>Caves World:</b> Underground world with unique resources and creatures<br>"
                "&bull; 🔗 <b>Linked Worlds:</b> Players can travel between surface and caves<br>"
                "&bull; 🎭 <b>Character Variety:</b> Multiple playable characters with unique abilities<br>"
                "&bull; 🧩 <b>Mod Support:</b> Extensive Steam Workshop integration<br><br>"
                "<i>⚠️ Note: DST runs two server processes simultaneously (Master + Caves) for the complete experience.</i>"
            ),
            'function': install_or_update_dst_server,
            'requires_confirmation': True,
            'confirmation_text': (
                "<b>This will download the Don't Starve Together server files (~2GB).</b><br>"
                "Do you want to proceed?"
            )
            },
            {
            'name': 'Configure & Launch Server',
            'description': (
                "<b>Configure server settings including server token and launch the DST dedicated server.</b><br><br>"
                "<u>🔑 Server Token Required:</u><br>"
                "Don't Starve Together requires a server token from Klei Entertainment to run dedicated servers. "
                "This token links your server to your Klei account and enables online features."
            ),
            'function': self.configure_and_launch_server,
            'requires_confirmation': False,
            'confirmation_text': None
            }
        ]
    
    def get_game_specific_ui_elements(self):
        """Return DST-specific UI elements for the current step"""
        elements = []
        
        # Only show elements for the final step (step 3: Configure & Launch Server)
        if self.current_step == 2:  # Step 3 (0-indexed)
            # Server token section
            token_group = QGroupBox("🔑 Server Token Configuration")
            token_layout = QVBoxLayout()
            
            # Token explanation
            token_explanation = QLabel(
                "<b>Server Token Required:</b><br>"
                "Don't Starve Together requires a server token from Klei Entertainment. "
                "Click the button below to get your token, then paste it in the field."
            )
            token_explanation.setWordWrap(True)
            token_explanation.setFont(QFont(FONT_FAMILY, INFO_FONT_SIZE))
            token_layout.addWidget(token_explanation)
            
            # Button to open token URL
            token_button = QPushButton("🌐 Get Server Token from Klei")
            token_button.clicked.connect(self.open_token_url)
            token_button.setFont(QFont(FONT_FAMILY, CHECKBOX_FONT_SIZE))
            token_layout.addWidget(token_button)
            
            # Token input
            token_form = QFormLayout()
            self.server_token_input = QLineEdit()
            self.server_token_input.setPlaceholderText("Paste your server token here...")
            self.server_token_input.setFont(QFont(FONT_FAMILY, INFO_FONT_SIZE))
            token_form.addRow("Server Token:", self.server_token_input)
            
            token_layout.addLayout(token_form)
            token_group.setLayout(token_layout)
            elements.append(token_group)
            
            # Server configuration section
            config_group = QGroupBox("⚙️ Server Configuration")
            config_layout = QFormLayout()
            
            # Server name
            self.server_name_input = QLineEdit("My DST Server")
            self.server_name_input.setFont(QFont(FONT_FAMILY, INFO_FONT_SIZE))
            config_layout.addRow("Server Name:", self.server_name_input)
            
            # Server description
            self.server_description_input = QLineEdit("A Don't Starve Together Server")
            self.server_description_input.setFont(QFont(FONT_FAMILY, INFO_FONT_SIZE))
            config_layout.addRow("Description:", self.server_description_input)
            
            # Max players
            self.max_players_input = QSpinBox()
            self.max_players_input.setRange(1, 6)
            self.max_players_input.setValue(6)
            self.max_players_input.setFont(QFont(FONT_FAMILY, INFO_FONT_SIZE))
            config_layout.addRow("Max Players:", self.max_players_input)
            
            # Server password (optional)
            self.server_password_input = QLineEdit()
            self.server_password_input.setPlaceholderText("Leave empty for no password")
            self.server_password_input.setFont(QFont(FONT_FAMILY, INFO_FONT_SIZE))
            config_layout.addRow("Password (Optional):", self.server_password_input)
            
            config_group.setLayout(config_layout)
            elements.append(config_group)
            
            # World configuration section
            world_group = QGroupBox("🌍 World Configuration")
            world_layout = QVBoxLayout()
            
            # Enable caves checkbox
            self.enable_caves_checkbox = QCheckBox("Enable Caves World")
            self.enable_caves_checkbox.setChecked(True)
            self.enable_caves_checkbox.setFont(QFont(FONT_FAMILY, CHECKBOX_FONT_SIZE))
            world_layout.addWidget(self.enable_caves_checkbox)
            
            caves_explanation = QLabel(
                "Caves provide additional content, resources, and gameplay. "
                "Disabling caves will only run the surface world (Master shard)."
            )
            caves_explanation.setWordWrap(True)
            caves_explanation.setFont(QFont(FONT_FAMILY, INFO_FONT_SIZE))
            world_layout.addWidget(caves_explanation)
            
            world_group.setLayout(world_layout)
            elements.append(world_group)
            
            # Port forwarding explanation
            port_explanation = QLabel("🌐 Network Configuration:")
            port_explanation.setFont(QFont(FONT_FAMILY, EXPLANATION_FONT_SIZE))
            elements.append(port_explanation)
            
            # Port forwarding checkbox
            self.port_checkbox = QCheckBox(
                f"Automatically configure port forwarding for DST server "
                f"(Ports: {DST_DEFAULT_MASTER_PORT}, {DST_DEFAULT_CAVES_PORT}, and authentication ports)"
            )
            self.port_checkbox.setChecked(True)
            self.port_checkbox.setFont(QFont(FONT_FAMILY, CHECKBOX_FONT_SIZE))
            elements.append(self.port_checkbox)
            
            port_info = QLabel(
                "⚠️ Port forwarding allows external players to connect to your server. "
                "If disabled, only local network players can join."
            )
            port_info.setWordWrap(True)
            port_info.setFont(QFont(FONT_FAMILY, INFO_FONT_SIZE))
            elements.append(port_info)
        
        return elements
    
    def open_token_url(self):
        """Open the Klei server token URL in the default browser"""
        url = "https://accounts.klei.com/account/game/servers?game=DontStarveTogether"
        QDesktopServices.openUrl(QUrl(url))
    
    def configure_and_launch_server(self):
        """Handle the configure and launch step - validate inputs and return True to proceed"""
        try:
            # Validate server token
            token = self.server_token_input.text().strip()
            is_valid, message = validate_server_token(token)
            
            if not is_valid:
                QMessageBox.warning(self, "Invalid Token", f"Server token validation failed: {message}")
                return False
            
            # Validate required fields
            server_name = self.server_name_input.text().strip()
            if not server_name:
                QMessageBox.warning(self, "Missing Information", "Please enter a server name.")
                return False
            
            self.log_message("🔧 Configuration validated successfully!")
            self.log_message("ℹ️ Click 'Continue' to configure and launch the DST server.")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Configuration Error", f"Error validating configuration: {str(e)}")
            return False
    
    def handle_final_step_completion(self):
        """Handle DST-specific final step completion - actually configure and start the server"""
        self.log_message("🚀 Starting DST server configuration and launch...")
        
        try:
            # Get configuration values
            token = self.server_token_input.text().strip()
            server_name = self.server_name_input.text().strip()
            server_description = self.server_description_input.text().strip()
            max_players = self.max_players_input.value()
            password = self.server_password_input.text().strip()
            enable_caves = self.enable_caves_checkbox.isChecked()
            
            # Debug: Log the token being used
            self.log_message(f"🔍 Debug: Token length: {len(token)}")
            self.log_message(f"🔍 Debug: Token (first 20 chars): {token[:20]}...")
            self.log_message(f"🔍 Debug: Token (last 20 chars): ...{token[-20:]}")
            
            # Create server configuration
            self.log_message("🔧 Creating DST server configuration...")
            config_success = create_dst_configuration(
                server_name,
                server_description,
                max_players,
                password,
                token,
                enable_caves
            )
            
            if not config_success:
                self.log_message("❌ Failed to create server configuration")
                return False
            
            self.log_message("✅ Server configuration created successfully!")
            
            # Setup port forwarding if requested
            if self.port_checkbox.isChecked():
                self.log_message("🌐 Setting up port forwarding...")
                try:
                    port_success = setup_upnp_port_forwarding()
                    if port_success:
                        self.log_message("✅ Port forwarding configured successfully!")
                    else:
                        self.log_message("⚠️ Port forwarding failed, but continuing...")
                except Exception as e:
                    self.log_message(f"⚠️ Port forwarding failed: {str(e)}")
                    self.log_message("You can configure port forwarding manually if needed.")
            
            # Start the server
            self.log_message("🚀 Starting DST server...")
            server_success = start_dst_server(enable_caves)
            
            if server_success:
                self.log_message("✅ DST server started successfully!")
                self.log_message(f"🌍 Server Name: {server_name}")
                self.log_message(f"👥 Max Players: {max_players}")
                self.log_message(f"🕳️ Caves Enabled: {'Yes' if enable_caves else 'No'}")
                self.log_message(f"🌐 Local Connection: localhost:{DST_DEFAULT_MASTER_PORT}")
                self.log_message("📝 External players can search for your server by name in the browser.")
                return True
            else:
                self.log_message("❌ Failed to start DST server")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Error during DST server configuration: {str(e)}")
            return False
