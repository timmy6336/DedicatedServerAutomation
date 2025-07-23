import os
import sys
from PyQt5.QtWidgets import QCheckBox, QLabel
from PyQt5.QtGui import QFont
from .base_setup_window import BaseServerSetupWindow

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
                'description': 'Download and install the Palworld Dedicated Server files from Steam. This may take several minutes depending on your internet connection as the server files are quite large.',
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
            explanation.setFont(QFont('Segoe UI', 16, QFont.Bold))
            explanation.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin: 15px 5px;")
            elements.append(explanation)
            
            # Port forwarding checkbox
            self.port_checkbox = QCheckBox("Enable automatic port forwarding (UPnP)")
            self.port_checkbox.setFont(QFont('Segoe UI', 14))
            self.port_checkbox.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin: 10px 5px;")
            self.port_checkbox.setChecked(True)
            elements.append(self.port_checkbox)
            
            # Port forwarding info
            port_info = QLabel("This will automatically configure your router to forward port 8211 for the Palworld server. If you prefer to configure port forwarding manually, uncheck this option.")
            port_info.setFont(QFont('Segoe UI', 12))
            port_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin: 5px 15px; padding: 10px;")
            port_info.setWordWrap(True)
            elements.append(port_info)
            
            # Server start info
            server_info = QLabel("Clicking 'Continue' will configure the selected options and launch your Palworld dedicated server.")
            server_info.setFont(QFont('Segoe UI', 12))
            server_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin: 15px 5px; font-style: italic;")
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
                self.log_message("=" * 50)
                self.log_message("🎊 SETUP COMPLETED SUCCESSFULLY! 🎊")
                self.log_message("Your Palworld server is ready for players!")
                self.log_message("=" * 50)
            else:
                self.log_message("❌ Failed to start Palworld server. Please check the logs above.")
                success = False
        except Exception as e:
            self.log_message(f"❌ Error starting server: {str(e)}")
            success = False
            
        return success
