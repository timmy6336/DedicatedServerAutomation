import os
import sys
# ================== PALWORLD SETUP CONSTANTS ==================
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

# Palworld server configuration
PALWORLD_DEFAULT_PORT = 8211             # Default port for Palworld server

# UI layout and formatting
SEPARATOR_LINE_LENGTH = 50               # Length of separator lines in logs

from PyQt5.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton,
    QTextEdit, QWidget, QApplication
)
from PyQt5.QtGui import QFont
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
from scripts.palworld_server_startup_script import (
    download_steamcmd,
    install_or_update_palworld_server,
    setup_upnp_port_forwarding,
    start_palworld_server
)

class PalworldServerSetupWindow(BaseServerSetupWindow):
    """Palworld-specific server setup window"""
    
    def __init__(self, game):
        self.port_checkbox = None
        super().__init__(game)
    
    def get_setup_steps(self):
        """Define the setup steps for Palworld"""
        return [
            {
                'name': 'Install SteamCMD',
                'description': 'SteamCMD is required to download and manage Steam-based game servers. This step will download and install SteamCMD if it is not already present on your system.',
                'function': download_steamcmd,
                'requires_confirmation': True,
                'confirmation_text': 'This will download and install SteamCMD. Do you want to proceed?'
            },
            {
                'name': 'Install Palworld Server',
                'description': '''Download and install the Palworld Dedicated Server files from Steam.

<b>🎮 About Palworld:</b><br>
Palworld is a creature-collecting survival game where players catch, train, and battle mysterious creatures called "Pals" while building bases, crafting items, and exploring an open world. Features both cooperative and competitive multiplayer gameplay with up to 32 players.

<b>📊 System Requirements for Dedicated Server:</b><br>
<u>Minimum Requirements:</u><br>
• <b>RAM:</b> 8GB (for 4-8 players)<br>
• <b>CPU:</b> 4-core 2.5GHz (Intel i5-4430 / AMD FX-6300)<br>
• <b>GPU:</b> Not required (headless server)<br>
• <b>Storage:</b> 8GB available space<br>
• <b>Network:</b> Broadband connection<br>

<u>Recommended for 32 Players:</u><br>
• <b>RAM:</b> 16-32GB dedicated to server<br>
• <b>CPU:</b> 8-core 3.5GHz+ (Intel i7-9700K / AMD Ryzen 7 3700X)<br>
• <b>GPU:</b> Not required (dedicated server runs headless)<br>
• <b>Storage:</b> 20GB+ SSD for world saves and Pal data<br>
• <b>Upload Speed:</b> 20+ Mbps for large multiplayer sessions<br>

<b>📦 Download Details:</b><br>
• <b>Size:</b> ~4-6GB server files<br>
• <b>World Save Size:</b> 500MB-2GB (grows with bases and Pals)<br>
• <b>Supports:</b> Up to 32 concurrent players<br>
• <b>Features:</b> Pal catching, base building, crafting, multiplayer raids<br>

<b>⚠️ Performance Note:</b> Palworld servers are resource-intensive due to AI Pal management and complex base systems. More RAM is strongly recommended for stable performance.''',
                'function': install_or_update_palworld_server,
                'requires_confirmation': True,
                'confirmation_text': 'This will download the Palworld server files (several GB). Do you want to proceed?'
            },
            {
                'name': 'Configure & Launch Server',
                'description': 'Configure final server settings including port forwarding and start the Palworld dedicated server.',
                'function': self.configure_and_launch_server,
                'requires_confirmation': False,  # We'll handle confirmation in the final step
                'confirmation_text': None
            }
        ]
    
    def get_game_specific_ui_elements(self):
        """Return Palworld-specific UI elements for the current step"""
        elements = []
        
        # Only show elements for the final step (step 3: Configure & Launch Server)
        if self.current_step == 2:  # Step 3 (0-indexed)
            # Port forwarding explanation
            explanation = QLabel("Final Configuration Options:")
            explanation.setFont(QFont(FONT_FAMILY, EXPLANATION_FONT_SIZE, QFont.Bold))
            explanation.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin: {MARGIN_LARGE}px {MARGIN_SMALL}px;")
            elements.append(explanation)
            
            # Port forwarding checkbox
            self.port_checkbox = QCheckBox("Enable automatic port forwarding (UPnP)")
            self.port_checkbox.setFont(QFont(FONT_FAMILY, CHECKBOX_FONT_SIZE))
            self.port_checkbox.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin: {MARGIN_MEDIUM}px {MARGIN_SMALL}px;")
            self.port_checkbox.setChecked(True)
            elements.append(self.port_checkbox)
            
            # Port forwarding info
            port_info = QLabel(f"This will automatically configure your router to forward port {PALWORLD_DEFAULT_PORT} for the Palworld server. If you prefer to configure port forwarding manually, uncheck this option.")
            port_info.setFont(QFont(FONT_FAMILY, INFO_FONT_SIZE))
            port_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin: {MARGIN_SMALL}px {MARGIN_LARGE}px; padding: {PADDING_STANDARD}px;")
            port_info.setWordWrap(True)
            elements.append(port_info)
            
            # Server start info
            server_info = QLabel("Clicking 'Continue' will configure the selected options and launch your Palworld dedicated server.")
            server_info.setFont(QFont(FONT_FAMILY, INFO_FONT_SIZE))
            server_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin: {MARGIN_LARGE}px {MARGIN_SMALL}px; font-style: italic;")
            server_info.setWordWrap(True)
            elements.append(server_info)
        
        return elements
    
    def configure_and_launch_server(self):
        """Handle the configure and launch step - just return True to proceed to final completion"""
        self.log_message("🔧 Ready to configure and launch server...")
        self.log_message("ℹ️ Click 'Continue' to proceed with your selected options.")
        return True
    
    def handle_final_step_completion(self):
        """Handle Palworld-specific final step completion - actually configure and start the server"""
        self.log_message("🚀 Starting server configuration and launch...")
        success = True
        
        # Configure port forwarding if selected
        if self.port_checkbox and self.port_checkbox.isChecked():
            self.log_message("Configuring UPnP port forwarding...")
            try:
                port_success = setup_upnp_port_forwarding()
                if port_success:
                    self.log_message("✅ Port forwarding configured successfully!")
                else:
                    self.log_message("⚠️ Port forwarding failed, but you can configure it manually.")
            except Exception as e:
                self.log_message(f"⚠️ Port forwarding failed: {str(e)}")
                self.log_message("You can configure port forwarding manually if needed.")
        else:
            self.log_message("ℹ️ Port forwarding skipped (you selected not to configure it automatically).")
        
        # Start the server
        self.log_message("🚀 Starting Palworld dedicated server...")
        try:
            server_success = start_palworld_server()
            if server_success:
                self.log_message("🎉 Palworld dedicated server started successfully!")
                self.log_message("✅ Your server is now running and ready for players to connect.")
                self.log_message("🌐 Check the game details page for connection information.")
                self.log_message("=" * SEPARATOR_LINE_LENGTH)
                self.log_message("🎊 SETUP COMPLETED SUCCESSFULLY! 🎊")
                self.log_message("Your Palworld server is ready for players!")
                self.log_message("=" * SEPARATOR_LINE_LENGTH)
            else:
                self.log_message("❌ Failed to start Palworld server. Please check the logs above.")
                success = False
        except Exception as e:
            self.log_message(f"❌ Error starting server: {str(e)}")
            success = False
            
        return success
