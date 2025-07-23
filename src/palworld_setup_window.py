import os
from scripts import palworld_server_startup_script as startup_script
import sys
import subprocess
import threading
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, 
                           QTextEdit, QHBoxLayout, QMessageBox, QCheckBox)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from styles import (
    MAIN_WINDOW_STYLE, 
    BUTTON_STYLE,
    Colors, 
    Layout
)

class InstallationWorker(QThread):
    """Worker thread for handling installations without blocking the UI"""
    progress_updated = pyqtSignal(int)  # Progress percentage
    status_updated = pyqtSignal(str)    # Status message
    finished = pyqtSignal(bool)         # Success/failure
    
    def __init__(self, task_type):
        super().__init__()
        self.task_type = task_type  # "steamcmd" or "palworld"
    
    def run(self):
        try:
            if self.task_type == "steamcmd":
                self.install_steamcmd()
            elif self.task_type == "palworld":
                self.install_palworld()
        except Exception as e:
            self.status_updated.emit(f"Error: {str(e)}")
            self.finished.emit(False)
    
    def install_steamcmd(self):
        """Install SteamCMD with progress updates"""
        # Import the actual installation function
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scripts_dir = os.path.join(script_dir, "scripts")
        
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        
        try:
            
            self.status_updated.emit("Checking SteamCMD installation...")
            self.progress_updated.emit(10)
            
            self.status_updated.emit("Downloading SteamCMD...")
            self.progress_updated.emit(30)
            
            # Call the actual download function
            startup_script.download_steamcmd()
            
            self.progress_updated.emit(80)
            self.status_updated.emit("Extracting SteamCMD...")
            
            self.progress_updated.emit(100)
            self.status_updated.emit("SteamCMD installation completed!")
            self.finished.emit(True)
            
        except Exception as e:
            self.status_updated.emit(f"SteamCMD installation failed: {str(e)}")
            self.finished.emit(False)
    
    def install_palworld(self):
        """Install Palworld server with progress updates"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scripts_dir = os.path.join(script_dir, "scripts")
        
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        
        try:
            
            self.status_updated.emit("Checking Palworld server installation...")
            self.progress_updated.emit(10)
            
            self.status_updated.emit("Installing Palworld dedicated server...")
            self.progress_updated.emit(30)
            
            # Call the actual installation function
            startup_script.install_or_update_palworld_server()
            
            self.progress_updated.emit(80)
            self.status_updated.emit("Finalizing installation...")
            
            self.progress_updated.emit(100)
            self.status_updated.emit("Palworld server installation completed!")
            self.finished.emit(True)
            
        except Exception as e:
            self.status_updated.emit(f"Palworld server installation failed: {str(e)}")
            self.finished.emit(False)

class PalworldServerSetupWindow(QWidget):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.current_step = 0
        self.steps = ["steamcmd", "palworld", "port_forward"]
        self.worker = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(f'{self.game.name} - Dedicated Server Setup')
        self.setFixedSize(800, 600)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(Layout.MARGIN_LARGE, Layout.MARGIN_LARGE, Layout.MARGIN_LARGE, Layout.MARGIN_LARGE)
        main_layout.setSpacing(Layout.SPACING_LARGE)
        
        # Header
        self.add_header(main_layout)
        
        # Progress section
        self.add_progress_section(main_layout)
        
        # Status/Log section
        self.add_status_section(main_layout)
        
        # Control buttons
        self.add_control_buttons(main_layout)
        
        self.setLayout(main_layout)
        
        # Start the first step
        self.start_current_step()
    
    def add_header(self, layout):
        """Add header with game info"""
        header_layout = QHBoxLayout()
        
        # Game image (if available)
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, self.game.image_url)
            if not os.path.exists(image_path):
                image_path = os.path.join(script_dir, "images", "palworld_image.jpg")
            
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(100, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                image_label = QLabel()
                image_label.setPixmap(scaled_pixmap)
                image_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {Colors.BACKGROUND_LIGHT};
                        border: 2px solid {Colors.BORDER};
                        border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
                        padding: 5px;
                    }}
                """)
                header_layout.addWidget(image_label)
        except Exception:
            pass
        
        # Title and description
        title_layout = QVBoxLayout()
        
        title_label = QLabel(f"{self.game.name} Dedicated Server Setup")
        title_label.setFont(QFont('Segoe UI', 20, QFont.Bold))
        title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        title_layout.addWidget(title_label)
        
        desc_label = QLabel("Setting up your dedicated server environment...")
        desc_label.setFont(QFont('Segoe UI', 12))
        desc_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        title_layout.addWidget(desc_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
    
    def add_progress_section(self, layout):
        """Add progress bar and step indicator"""
        # Step indicator
        self.step_label = QLabel("Step 1/3: Installing SteamCMD")
        self.step_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        self.step_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-bottom: 10px;")
        layout.addWidget(self.step_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {Colors.BORDER};
                border-radius: {Layout.BORDER_RADIUS_SMALL}px;
                background-color: {Colors.BACKGROUND_LIGHT};
                text-align: center;
                font-weight: bold;
                color: {Colors.TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                background-color: {Colors.ACCENT};
                border-radius: {Layout.BORDER_RADIUS_SMALL}px;
            }}
        """)
        layout.addWidget(self.progress_bar)
    
    def add_status_section(self, layout):
        """Add status text area for logs"""
        status_label = QLabel("Installation Log:")
        status_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        status_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-top: 15px;")
        layout.addWidget(status_label)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        self.status_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Colors.BACKGROUND_LIGHT};
                border: 2px solid {Colors.BORDER};
                border-radius: {Layout.BORDER_RADIUS_SMALL}px;
                color: {Colors.TEXT_SECONDARY};
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                padding: 10px;
            }}
        """)
        layout.addWidget(self.status_text)
    
    def add_control_buttons(self, layout):
        """Add control buttons"""
        button_layout = QHBoxLayout()
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.setFont(QFont('Segoe UI', 12))
        self.close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BORDER};
                color: {Colors.TEXT_PRIMARY};
                border: none;
                border-radius: {Layout.BORDER_RADIUS_SMALL}px;
                padding: 10px 20px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #505050;
            }}
        """)
        self.close_button.clicked.connect(self.close)
        self.close_button.setEnabled(False)  # Disabled during installation
        
        # Next/Finish button
        self.next_button = QPushButton("Next")
        self.next_button.setFont(QFont('Segoe UI', 12, QFont.Bold))
        self.next_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT};
                color: white;
                border: none;
                border-radius: {Layout.BORDER_RADIUS_SMALL}px;
                padding: 10px 20px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {Colors.BORDER};
                color: {Colors.TEXT_DISABLED};
            }}
        """)
        self.next_button.clicked.connect(self.next_step)
        self.next_button.setEnabled(False)  # Enabled when step completes
        
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        button_layout.addWidget(self.next_button)
        
        layout.addLayout(button_layout)
    
    def start_current_step(self):
        """Start the current installation step"""
        step = self.steps[self.current_step]
        
        if step == "steamcmd":
            self.step_label.setText("Step 1/3: Installing SteamCMD")
            self.log_message("Starting SteamCMD installation...")
            self.start_installation("steamcmd")
            
        elif step == "palworld":
            self.step_label.setText("Step 2/3: Installing Palworld Server")
            self.log_message("Starting Palworld server installation...")
            self.start_installation("palworld")
            
        elif step == "port_forward":
            self.step_label.setText("Step 3/3: Port Forwarding Setup")
            self.setup_port_forwarding()
    
    def start_installation(self, task_type):
        """Start installation in worker thread"""
        self.progress_bar.setValue(0)
        self.next_button.setEnabled(False)
        
        self.worker = InstallationWorker(task_type)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.status_updated.connect(self.log_message)
        self.worker.finished.connect(self.on_installation_finished)
        self.worker.start()
    
    def setup_port_forwarding(self):
        """Handle port forwarding setup"""
        self.progress_bar.setValue(50)
        self.log_message("Port forwarding setup...")
        
        # Add checkbox for port forwarding
        self.port_checkbox = QCheckBox("Enable automatic port forwarding (UPnP)")
        self.port_checkbox.setFont(QFont('Segoe UI', 12))
        self.port_checkbox.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin: 10px;")
        self.port_checkbox.setChecked(True)
        
        port_info = QLabel("This will automatically configure your router to forward port 8211 for the Palworld server.")
        port_info.setFont(QFont('Segoe UI', 10))
        port_info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin: 5px 10px;")
        port_info.setWordWrap(True)
        
        # Add to main layout (insert before buttons)
        main_layout = self.layout()
        main_layout.insertWidget(main_layout.count() - 1, self.port_checkbox)
        main_layout.insertWidget(main_layout.count() - 1, port_info)
        
        self.progress_bar.setValue(100)
        self.next_button.setText("Finish & Start Server")
        self.next_button.setEnabled(True)
    
    def configure_port_forwarding(self, enabled):
        """Configure port forwarding"""
        if enabled:
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                scripts_dir = os.path.join(script_dir, "scripts")
                
                if scripts_dir not in sys.path:
                    sys.path.insert(0, scripts_dir)
                
                self.log_message("Configuring UPnP port forwarding...")
                startup_script.setup_upnp_port_forwarding()
                self.log_message("Port forwarding configured successfully!")
                
            except Exception as e:
                self.log_message(f"Port forwarding failed: {str(e)}")
        else:
            self.log_message("Port forwarding skipped.")
    
    def on_installation_finished(self, success):
        """Handle installation completion"""
        if success:
            self.log_message("Installation completed successfully!")
            self.next_button.setEnabled(True)
        else:
            self.log_message("Installation failed. Please check the logs.")
            self.close_button.setEnabled(True)
    
    def next_step(self):
        """Move to next step or finish"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.start_current_step()
        else:
            # All steps complete - handle port forwarding and start the server
            self.log_message("Setup completed! Finalizing server setup...")
            
            # Configure port forwarding if selected
            if hasattr(self, 'port_checkbox') and self.port_checkbox.isChecked():
                self.configure_port_forwarding(True)
            else:
                self.log_message("Port forwarding skipped.")
            
            # Start the server
            self.start_server()
    
    def start_server(self):
        """Start the Palworld dedicated server"""
        try:
            self.log_message("Launching Palworld dedicated server...")
            success = startup_script.start_palworld_server()
            
            if success:
                self.log_message("Palworld dedicated server started successfully!")
                self.log_message("Your server is now running and ready for players to connect.")
                
                # Update UI to show completion
                self.step_label.setText("Setup Complete - Server Running!")
                self.next_button.setText("Close")
                self.next_button.clicked.disconnect()  # Remove previous connection
                self.next_button.clicked.connect(self.close)
                self.close_button.setEnabled(True)
                
            else:
                self.log_message("Failed to start Palworld server. Please check the installation.")
                self.close_button.setEnabled(True)
                
        except Exception as e:
            self.log_message(f"Error starting server: {str(e)}")
            self.close_button.setEnabled(True)
    
    def log_message(self, message):
        """Add message to status log"""
        self.status_text.append(f"[{self.get_timestamp()}] {message}")
        # Auto-scroll to bottom
        cursor = self.status_text.textCursor()
        cursor.movePosition(cursor.End)
        self.status_text.setTextCursor(cursor)
    
    def get_timestamp(self):
        """Get current timestamp for logs"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, 'Close Window', 
                                       'Installation is in progress. Are you sure you want to close?',
                                       QMessageBox.Yes | QMessageBox.No, 
                                       QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.worker.terminate()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
