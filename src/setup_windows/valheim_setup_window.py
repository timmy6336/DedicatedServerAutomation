"""
Valheim Dedicated Server Setup Window

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
        self.setFixedSize(600, 700)
        self.setStyleSheet(f"background-color: {Colors.BACKGROUND_DARK};")
        
        # Server configuration values - load from persistent storage or use defaults
        saved_config = config_manager.load_server_config('Valheim')
        if saved_config:
            self.server_config = saved_config
        else:
            self.server_config = config_manager.get_default_valheim_config()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the configuration dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("🏰 Valheim Server Configuration")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Server Settings Group
        server_group = QGroupBox("⚔️ Server Settings")
        server_group.setFont(QFont('Segoe UI', 14, QFont.Bold))
        server_group.setStyleSheet(f"""
            QGroupBox {{
                color: {Colors.TEXT_PRIMARY};
                border: 2px solid {Colors.GRAY_MEDIUM};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        
        server_form = QFormLayout(server_group)
        server_form.setSpacing(15)
        
        # World Name
        self.world_name_input = QLineEdit(self.server_config['world_name'])
        self.world_name_input.setFont(QFont('Segoe UI', 12))
        self.world_name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BACKGROUND_MEDIUM};
                border: 2px solid {Colors.GRAY_MEDIUM};
                border-radius: 6px;
                padding: 8px;
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        server_form.addRow("🗺️ World Name:", self.world_name_input)
        
        # Server Name
        self.server_name_input = QLineEdit(self.server_config['server_name'])
        self.server_name_input.setFont(QFont('Segoe UI', 12))
        self.server_name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BACKGROUND_MEDIUM};
                border: 2px solid {Colors.GRAY_MEDIUM};
                border-radius: 6px;
                padding: 8px;
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        server_form.addRow("🏰 Server Name:", self.server_name_input)
        
        # Password
        self.password_input = QLineEdit(self.server_config['password'])
        self.password_input.setFont(QFont('Segoe UI', 12))
        self.password_input.setEchoMode(QLineEdit.Normal)  # Show password text instead of dots
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BACKGROUND_MEDIUM};
                border: 2px solid {Colors.GRAY_MEDIUM};
                border-radius: 6px;
                padding: 8px;
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        server_form.addRow("🔒 Password (min 5 chars):", self.password_input)
        
        # Port
        self.port_input = QSpinBox()
        self.port_input.setRange(1024, 65535)
        self.port_input.setValue(self.server_config['port'])
        self.port_input.setFont(QFont('Segoe UI', 12))
        self.port_input.setStyleSheet(f"""
            QSpinBox {{
                background-color: {Colors.BACKGROUND_MEDIUM};
                border: 2px solid {Colors.GRAY_MEDIUM};
                border-radius: 6px;
                padding: 8px;
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        server_form.addRow("🌐 Port:", self.port_input)
        
        # Public Server
        self.public_checkbox = QCheckBox("Make server visible in public server list")
        self.public_checkbox.setChecked(self.server_config['public_server'])
        self.public_checkbox.setFont(QFont('Segoe UI', 12))
        self.public_checkbox.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        server_form.addRow("📡 Visibility:", self.public_checkbox)
        
        layout.addWidget(server_group)
        
        # Network Settings Group
        network_group = QGroupBox("🌐 Network Configuration")
        network_group.setFont(QFont('Segoe UI', 14, QFont.Bold))
        network_group.setStyleSheet(f"""
            QGroupBox {{
                color: {Colors.TEXT_PRIMARY};
                border: 2px solid {Colors.GRAY_MEDIUM};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        
        network_form = QFormLayout(network_group)
        network_form.setSpacing(15)
        
        # Firewall Configuration
        self.firewall_checkbox = QCheckBox("Configure Windows Firewall rules for Valheim")
        self.firewall_checkbox.setChecked(self.server_config['configure_firewall'])
        self.firewall_checkbox.setFont(QFont('Segoe UI', 12))
        self.firewall_checkbox.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        network_form.addRow("🛡️ Firewall:", self.firewall_checkbox)
        
        # UPnP Configuration
        self.upnp_checkbox = QCheckBox("Enable automatic port forwarding (UPnP)")
        self.upnp_checkbox.setChecked(self.server_config['enable_upnp'])
        self.upnp_checkbox.setFont(QFont('Segoe UI', 12))
        self.upnp_checkbox.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        network_form.addRow("🔄 UPnP:", self.upnp_checkbox)
        
        layout.addWidget(network_group)
        
        # Information Text - Using QLabel instead of QTextEdit to avoid threading issues
        info_text = QLabel()
        info_text.setWordWrap(True)
        info_text.setMaximumHeight(120)
        info_text.setFont(QFont('Segoe UI', 10))
        info_text.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.BACKGROUND_MEDIUM};
                border: 2px solid {Colors.GRAY_MEDIUM};
                border-radius: 6px;
                padding: 8px;
                color: {Colors.TEXT_SECONDARY};
            }}
        """)
        info_text.setText(
            "📋 Configuration Notes:\n"
            "• Firewall: Allows Valheim traffic through Windows Firewall on ports 2456-2458 UDP\n"
            "• UPnP: Automatically configures router port forwarding for external access\n"
            "• Password: Must be at least 5 characters long for Valheim compatibility\n"
            "• Port Range: Valheim uses your specified port + 1 and +2 (e.g., 2456, 2457, 2458)"
        )
        layout.addWidget(info_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Advanced Button
        advanced_button = QPushButton("⚙️ Advanced Settings")
        advanced_button.setFont(QFont('Segoe UI', 12))
        advanced_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GRAY_MEDIUM};
                border: none;
                border-radius: 8px;
                color: {Colors.TEXT_PRIMARY};
                padding: 12px 20px;
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
        cancel_button.setFont(QFont('Segoe UI', 12))
        cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GRAY_MEDIUM};
                border: none;
                border-radius: 8px;
                color: {Colors.TEXT_PRIMARY};
                padding: 12px 20px;
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
        ok_button.setFont(QFont('Segoe UI', 12))
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
        if len(password) < 5:
            QMessageBox.warning(self, "Invalid Password", 
                              "🔒 Password must be at least 5 characters long for Valheim compatibility.")
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
                'description': 'Download and install the Valheim Dedicated Server files from Steam. The Valheim server is relatively lightweight (~2GB) compared to other survival games. This includes all necessary files for hosting up to 10 Viking warriors in your procedurally generated world.',
                'function': install_or_update_valheim_server,
                'requires_confirmation': True,
                'confirmation_text': 'This will download the Valheim server files (~2GB download). The server supports up to 10 concurrent players. Do you want to proceed?'
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
            (len(self.setup_steps) == 1 and self.current_step == 0) or  # Existing installation
            (len(self.setup_steps) > 1 and self.current_step == 2)      # New installation
        )
        
        if is_config_step:
            # Show different header based on installation status
            if is_valheim_server_installed():
                # Server already installed
                explanation = QLabel("🏰 Configure Existing Viking Realm")
                explanation.setFont(QFont('Segoe UI', 18, QFont.Bold))
                explanation.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin: 15px 5px;")
                explanation.setAlignment(Qt.AlignCenter)
                elements.append(explanation)
                
                # Status info for existing installation
                status_info = QLabel("✅ Valheim dedicated server is already installed and ready!")
                status_info.setFont(QFont('Segoe UI', 14, QFont.Bold))
                status_info.setStyleSheet(f"color: #2ecc71; margin: 10px 5px;")
                status_info.setWordWrap(True)
                elements.append(status_info)
                
                config_info = QLabel("⚙️ Configure your server settings and launch your Viking realm:")
                config_info.setFont(QFont('Segoe UI', 14, QFont.Bold))
                config_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin: 10px 5px;")
                config_info.setWordWrap(True)
                elements.append(config_info)
            else:
                # New installation
                explanation = QLabel("🏰 Viking Realm Configuration")
                explanation.setFont(QFont('Segoe UI', 18, QFont.Bold))
                explanation.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin: 15px 5px;")
                explanation.setAlignment(Qt.AlignCenter)
                elements.append(explanation)
                
                # Configuration info
                config_info = QLabel("⚙️ When you click 'Continue', you'll be able to customize your server settings:")
                config_info.setFont(QFont('Segoe UI', 14, QFont.Bold))
                config_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin: 10px 5px;")
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
            options_label.setFont(QFont('Segoe UI', 12))
            options_label.setStyleSheet(f"""
                color: {Colors.TEXT_PRIMARY}; 
                margin: 10px 15px; 
                padding: 15px; 
                background-color: {Colors.BACKGROUND_MEDIUM}; 
                border-radius: 8px;
                border: 2px solid {Colors.GRAY_MEDIUM};
            """)
            options_label.setWordWrap(True)
            elements.append(options_label)
            
            # Preview current defaults
            defaults_info = QLabel("� Default configuration preview:")
            defaults_info.setFont(QFont('Segoe UI', 14, QFont.Bold))
            defaults_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin: 15px 5px 5px 5px;")
            elements.append(defaults_info)
            
            defaults_text = """
• World: "DedicatedWorld" | Server: "Valheim Server"<br>
• Port: 2456 | Password: Protected | Public: Yes<br>
• Firewall & UPnP: Enabled (can be customized)
            """
            
            defaults_label = QLabel(defaults_text)
            defaults_label.setFont(QFont('Segoe UI', 11))
            defaults_label.setStyleSheet(f"""
                color: {Colors.TEXT_SECONDARY}; 
                margin: 5px 15px 15px 15px; 
                padding: 10px; 
                background-color: {Colors.BACKGROUND_MEDIUM}; 
                border-radius: 6px;
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
            action_info.setFont(QFont('Segoe UI', 13, QFont.Bold))
            action_info.setStyleSheet("""
                color: #2ecc71; 
                margin: 15px 5px; 
                padding: 12px;
                background-color: rgba(46, 204, 113, 0.1);
                border-radius: 8px;
                border: 2px solid #2ecc71;
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
