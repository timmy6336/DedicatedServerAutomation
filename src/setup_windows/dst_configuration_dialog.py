"""
DST Server Configuration Dialog

This module provides a comprehensive configuration interface for Don't Starve Together
dedicated servers. It allows users to modify all server settings including server
details, gameplay options, world generation settings, and administrative options.

The dialog automatically loads existing configuration and provides sensible defaults
for new configurations.

Features:
- Server identity configuration (name, description, password)
- Player and gameplay settings (max players, PvP, game mode)
- World generation presets and custom settings
- Server token management with validation
- Cave/surface world configuration
- Administrative settings (console, pause options)
- Real-time validation and helpful tooltips
"""

import os
import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QSpinBox, QCheckBox, QComboBox, QPushButton,
    QTextEdit, QTabWidget, QWidget, QMessageBox, QScrollArea,
    QFrame, QGridLayout, QSlider
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, pyqtSignal

# Import styles from parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from styles import Colors, Layout

# Import DST functions
sys.path.insert(0, os.path.join(parent_dir, "scripts"))
from scripts.dst_server_startup_script import (
    read_existing_dst_configuration,
    create_dst_configuration,
    validate_server_token,
    get_dst_config_path
)

class DSTConfigurationDialog(QDialog):
    """Comprehensive DST server configuration dialog"""
    
    configuration_saved = pyqtSignal(dict)  # Emitted when configuration is saved
    
    def __init__(self, parent=None, load_existing=True):
        super().__init__(parent)
        self.setWindowTitle("DST Server Configuration")
        self.setModal(True)
        self.resize(800, 600)
        
        # Configuration data
        self.config_data = {}
        
        # Load existing configuration if requested
        if load_existing:
            self.config_data = read_existing_dst_configuration()
        else:
            # Set defaults for new configuration
            self.config_data = {
                'server_name': 'DST Server',
                'server_description': 'A Don\'t Starve Together Server',
                'max_players': 6,
                'password': '',
                'server_token': '',
                'enable_caves': True,
                'pvp': False,
                'pause_when_empty': True,
                'console_enabled': True,
                'world_preset': 'SURVIVAL_TOGETHER',
                'game_mode': 'survival'
            }
        
        self.setup_ui()
        self.load_configuration_into_ui()
        
        # Apply consistent styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BACKGROUND_PRIMARY};
                color: {Colors.TEXT_PRIMARY};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {Colors.BORDER_COLOR};
                border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
                margin: 10px 0px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QLineEdit, QSpinBox, QComboBox {{
                padding: 8px;
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: {Layout.BORDER_RADIUS_SMALL}px;
                background-color: {Colors.BACKGROUND_SECONDARY};
                color: {Colors.TEXT_PRIMARY};
            }}
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border: 2px solid {Colors.ACCENT_COLOR};
            }}
            QCheckBox {{
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid {Colors.BORDER_COLOR};
                background-color: {Colors.BACKGROUND_SECONDARY};
            }}
            QCheckBox::indicator:checked {{
                background-color: {Colors.ACCENT_COLOR};
                border: 1px solid {Colors.ACCENT_COLOR};
            }}
            QPushButton {{
                background-color: {Colors.BUTTON_BACKGROUND};
                color: {Colors.BUTTON_TEXT};
                border: none;
                border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.BUTTON_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.BUTTON_PRESSED};
            }}
            QTabWidget::pane {{
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
            }}
            QTabBar::tab {{
                background-color: {Colors.BACKGROUND_SECONDARY};
                color: {Colors.TEXT_PRIMARY};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {Colors.ACCENT_COLOR};
                color: white;
            }}
        """)
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget for organized settings
        self.tab_widget = QTabWidget()
        
        # Server Settings Tab
        self.server_tab = self.create_server_settings_tab()
        self.tab_widget.addTab(self.server_tab, "🖥️ Server Settings")
        
        # Gameplay Settings Tab
        self.gameplay_tab = self.create_gameplay_settings_tab()
        self.tab_widget.addTab(self.gameplay_tab, "🎮 Gameplay")
        
        # World Settings Tab
        self.world_tab = self.create_world_settings_tab()
        self.tab_widget.addTab(self.world_tab, "🌍 World Settings")
        
        # Advanced Settings Tab
        self.advanced_tab = self.create_advanced_settings_tab()
        self.tab_widget.addTab(self.advanced_tab, "⚙️ Advanced")
        
        layout.addWidget(self.tab_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Test Token button
        self.test_token_button = QPushButton("🔍 Test Server Token")
        self.test_token_button.clicked.connect(self.test_server_token)
        button_layout.addWidget(self.test_token_button)
        
        button_layout.addStretch()
        
        # Cancel and Save buttons
        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("💾 Save Configuration")
        self.save_button.clicked.connect(self.save_configuration)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def create_server_settings_tab(self):
        """Create the server settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Server Identity Group
        identity_group = QGroupBox("Server Identity")
        identity_layout = QFormLayout(identity_group)
        
        self.server_name_input = QLineEdit()
        self.server_name_input.setMaxLength(64)
        self.server_name_input.setPlaceholderText("Enter server name (visible in server browser)")
        identity_layout.addRow("Server Name:", self.server_name_input)
        
        self.server_description_input = QTextEdit()
        self.server_description_input.setMaximumHeight(80)
        self.server_description_input.setPlaceholderText("Enter server description (visible in server browser)")
        identity_layout.addRow("Description:", self.server_description_input)
        
        self.server_password_input = QLineEdit()
        self.server_password_input.setEchoMode(QLineEdit.Password)
        self.server_password_input.setPlaceholderText("Leave empty for no password")
        identity_layout.addRow("Password:", self.server_password_input)
        
        layout.addWidget(identity_group)
        
        # Authentication Group
        auth_group = QGroupBox("Server Authentication")
        auth_layout = QFormLayout(auth_group)
        
        self.server_token_input = QLineEdit()
        self.server_token_input.setPlaceholderText("Get token from: https://accounts.klei.com/account/game/servers")
        auth_layout.addRow("Server Token:", self.server_token_input)
        
        # Token help label
        token_help = QLabel("ℹ️ Server token is required for online play. Get yours from Klei's website.")
        token_help.setWordWrap(True)
        token_help.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-style: italic;")
        auth_layout.addRow("", token_help)
        
        layout.addWidget(auth_group)
        
        # Player Settings Group
        player_group = QGroupBox("Player Settings")
        player_layout = QFormLayout(player_group)
        
        self.max_players_input = QSpinBox()
        self.max_players_input.setRange(1, 64)
        self.max_players_input.setSuffix(" players")
        player_layout.addRow("Max Players:", self.max_players_input)
        
        layout.addWidget(player_group)
        
        layout.addStretch()
        return widget
    
    def create_gameplay_settings_tab(self):
        """Create the gameplay settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Game Mode Group
        mode_group = QGroupBox("Game Mode & Rules")
        mode_layout = QFormLayout(mode_group)
        
        self.game_mode_combo = QComboBox()
        self.game_mode_combo.addItems([
            "survival", "wilderness", "endless", "lightsout"
        ])
        mode_layout.addRow("Game Mode:", self.game_mode_combo)
        
        self.pvp_checkbox = QCheckBox("Enable Player vs Player combat")
        mode_layout.addRow("", self.pvp_checkbox)
        
        self.pause_when_empty_checkbox = QCheckBox("Pause server when no players are online")
        mode_layout.addRow("", self.pause_when_empty_checkbox)
        
        layout.addWidget(mode_group)
        
        # World Configuration Group
        world_group = QGroupBox("World Configuration")
        world_layout = QFormLayout(world_group)
        
        self.enable_caves_checkbox = QCheckBox("Enable Caves world (recommended)")
        world_layout.addRow("", self.enable_caves_checkbox)
        
        caves_help = QLabel("ℹ️ Caves provide additional content and resources. Disabling saves server resources.")
        caves_help.setWordWrap(True)
        caves_help.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-style: italic;")
        world_layout.addRow("", caves_help)
        
        layout.addWidget(world_group)
        
        layout.addStretch()
        return widget
    
    def create_world_settings_tab(self):
        """Create the world settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # World Preset Group
        preset_group = QGroupBox("World Generation Preset")
        preset_layout = QFormLayout(preset_group)
        
        self.world_preset_combo = QComboBox()
        self.world_preset_combo.addItems([
            "SURVIVAL_TOGETHER",
            "SURVIVAL_TOGETHER_CLASSIC", 
            "SURVIVAL_DEFAULT_PLUS",
            "MOD_MISSING",
            "COMPLETE_DARKNESS",
            "DST_CAVE"
        ])
        preset_layout.addRow("World Preset:", self.world_preset_combo)
        
        preset_help = QLabel(
            "ℹ️ World presets determine resource abundance, creature spawns, and world generation settings.\n"
            "• SURVIVAL_TOGETHER: Balanced multiplayer experience\n"
            "• SURVIVAL_TOGETHER_CLASSIC: Original DST balance\n"
            "• SURVIVAL_DEFAULT_PLUS: More resources for larger groups"
        )
        preset_help.setWordWrap(True)
        preset_help.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-style: italic; font-size: 11px;")
        preset_layout.addRow("", preset_help)
        
        layout.addWidget(preset_group)
        
        # Season Settings Group (placeholder for future expansion)
        season_group = QGroupBox("Seasonal Settings")
        season_layout = QFormLayout(season_group)
        
        season_info = QLabel("🚧 Advanced seasonal and world customization coming in future updates!")
        season_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-style: italic;")
        season_layout.addRow("", season_info)
        
        layout.addWidget(season_group)
        
        layout.addStretch()
        return widget
    
    def create_advanced_settings_tab(self):
        """Create the advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Administrative Group
        admin_group = QGroupBox("Administrative Settings")
        admin_layout = QFormLayout(admin_group)
        
        self.console_enabled_checkbox = QCheckBox("Enable server console (recommended for administration)")
        admin_layout.addRow("", self.console_enabled_checkbox)
        
        layout.addWidget(admin_group)
        
        # Network Settings Group
        network_group = QGroupBox("Network Settings")
        network_layout = QFormLayout(network_group)
        
        network_info = QLabel(
            f"🌐 Master Server Port: {11000}\\n"
            f"🕳️ Caves Server Port: {11001}\\n"
            f"ℹ️ Ports are automatically configured and managed."
        )
        network_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-family: monospace;")
        network_layout.addRow("Port Configuration:", network_info)
        
        layout.addWidget(network_group)
        
        # Performance Group
        perf_group = QGroupBox("Performance & Optimization")
        perf_layout = QFormLayout(perf_group)
        
        perf_info = QLabel(
            "💡 Performance Tips:\\n"
            "• Lower max players for better performance\\n"
            "• Disable caves if you need to save server resources\\n"
            "• Enable 'pause when empty' to reduce idle CPU usage"
        )
        perf_info.setWordWrap(True)
        perf_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-style: italic; font-size: 11px;")
        perf_layout.addRow("", perf_info)
        
        layout.addWidget(perf_group)
        
        layout.addStretch()
        return widget
    
    def load_configuration_into_ui(self):
        """Load configuration data into UI elements"""
        # Server settings
        self.server_name_input.setText(self.config_data.get('server_name', ''))
        self.server_description_input.setPlainText(self.config_data.get('server_description', ''))
        self.server_password_input.setText(self.config_data.get('password', ''))
        self.server_token_input.setText(self.config_data.get('server_token', ''))
        self.max_players_input.setValue(self.config_data.get('max_players', 6))
        
        # Gameplay settings
        game_mode = self.config_data.get('game_mode', 'survival')
        index = self.game_mode_combo.findText(game_mode)
        if index >= 0:
            self.game_mode_combo.setCurrentIndex(index)
        
        self.pvp_checkbox.setChecked(self.config_data.get('pvp', False))
        self.pause_when_empty_checkbox.setChecked(self.config_data.get('pause_when_empty', True))
        self.enable_caves_checkbox.setChecked(self.config_data.get('enable_caves', True))
        
        # World settings
        world_preset = self.config_data.get('world_preset', 'SURVIVAL_TOGETHER')
        index = self.world_preset_combo.findText(world_preset)
        if index >= 0:
            self.world_preset_combo.setCurrentIndex(index)
        
        # Advanced settings
        self.console_enabled_checkbox.setChecked(self.config_data.get('console_enabled', True))
    
    def collect_configuration_from_ui(self):
        """Collect configuration data from UI elements"""
        return {
            'server_name': self.server_name_input.text().strip(),
            'server_description': self.server_description_input.toPlainText().strip(),
            'password': self.server_password_input.text(),
            'server_token': self.server_token_input.text().strip(),
            'max_players': self.max_players_input.value(),
            'game_mode': self.game_mode_combo.currentText(),
            'pvp': self.pvp_checkbox.isChecked(),
            'pause_when_empty': self.pause_when_empty_checkbox.isChecked(),
            'enable_caves': self.enable_caves_checkbox.isChecked(),
            'world_preset': self.world_preset_combo.currentText(),
            'console_enabled': self.console_enabled_checkbox.isChecked()
        }
    
    def test_server_token(self):
        """Test the server token validity"""
        token = self.server_token_input.text().strip()
        
        if not token:
            QMessageBox.warning(self, "No Token", "Please enter a server token to test.")
            return
        
        try:
            is_valid = validate_server_token(token)
            
            if is_valid:
                QMessageBox.information(
                    self, 
                    "Token Valid", 
                    "✅ Server token is valid and ready for use!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Token Invalid",
                    "❌ Server token appears to be invalid or malformed.\\n\\n"
                    "Please check your token and try again. Get a new token from:\\n"
                    "https://accounts.klei.com/account/game/servers"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Token Test Failed",
                f"❌ Failed to test server token: {str(e)}\\n\\n"
                "This might be a network issue or server problem."
            )
    
    def save_configuration(self):
        """Save the configuration"""
        config = self.collect_configuration_from_ui()
        
        # Validate required fields
        if not config['server_name']:
            QMessageBox.warning(self, "Missing Information", "Please enter a server name.")
            self.tab_widget.setCurrentIndex(0)  # Switch to server settings tab
            self.server_name_input.setFocus()
            return
        
        if not config['server_token']:
            reply = QMessageBox.question(
                self,
                "No Server Token",
                "You haven't entered a server token. The server will only work for offline/LAN play.\\n\\n"
                "Do you want to continue without a token?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.tab_widget.setCurrentIndex(0)  # Switch to server settings tab
                self.server_token_input.setFocus()
                return
        
        try:
            # Create the DST configuration
            success = create_dst_configuration(
                server_name=config['server_name'],
                server_description=config['server_description'],
                max_players=config['max_players'],
                password=config['password'],
                server_token=config['server_token'],
                enable_caves=config['enable_caves']
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "Configuration Saved",
                    "✅ DST server configuration has been saved successfully!\\n\\n"
                    "You can now start your DST server with the new settings."
                )
                
                # Emit the configuration data
                self.configuration_saved.emit(config)
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    "❌ Failed to save DST server configuration.\\n\\n"
                    "Please check the logs for more details."
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Configuration Error",
                f"❌ Error saving configuration: {str(e)}\\n\\n"
                "Please check your settings and try again."
            )

def show_dst_configuration_dialog(parent=None, load_existing=True):
    """Show the DST configuration dialog and return the result"""
    dialog = DSTConfigurationDialog(parent, load_existing)
    return dialog.exec_()

if __name__ == "__main__":
    # Test the dialog
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    dialog = DSTConfigurationDialog(load_existing=False)
    result = dialog.exec_()
    
    if result == QDialog.Accepted:
        print("Configuration saved!")
    else:
        print("Configuration cancelled.")
