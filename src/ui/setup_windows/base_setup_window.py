"""
Base Setup Window Framework

This module provides the foundation for all game-specific server setup windows
in the Dedicated Server Automation application. It implements a standardized
step-by-step installation process with progress tracking, status updates, and
comprehensive error handling.

Key Features:
- Multi-step installation wizard with progress tracking
- Background thread processing to maintain UI responsiveness  
- Consistent UI layout and styling across all games
- Automatic success window auto-close functionality
- Real-time progress and status updates during installation
- Comprehensive error handling and user feedback
- Support for game-specific customization through inheritance

Architecture:
- BaseServerSetupWindow: Main window class with standard UI components
- InstallationWorker: Background thread for non-blocking operations
- Step-based progression system with customizable steps per game
- Extensible design allowing game-specific UI elements and behaviors

Threading Model:
- Main thread handles all UI updates and user interactions
- Worker threads handle long-running operations (downloads, installations)
- Signal/slot communication ensures thread-safe UI updates
- Proper resource cleanup and thread lifecycle management

Usage:
Game-specific setup windows inherit from BaseServerSetupWindow and override:
- get_setup_steps(): Define installation steps for the specific game
- get_game_specific_ui_elements(): Add custom UI elements if needed  
- handle_final_step_completion(): Implement final setup and server launch
- Any other methods requiring game-specific behavior

The base class handles all standard functionality including window management,
progress tracking, UI layout, threading, and user interaction patterns.
"""

# ================== BASE SETUP WINDOW CONSTANTS ==================
# Progress tracking constants
PROGRESS_START_PERCENT = 10              # Initial progress percentage when installation starts
PROGRESS_COMPLETE_PERCENT = 100          # Progress percentage when installation completes

# Window sizing constants
MIN_WINDOW_WIDTH = 900                   # Minimum window width for usability
MIN_WINDOW_HEIGHT = 700                  # Minimum window height for usability
DEFAULT_WINDOW_WIDTH = 1200              # Default window width
DEFAULT_WINDOW_HEIGHT = 900              # Default window height

# UI styling constants
SCROLLBAR_WIDTH = 12                     # Width of custom scrollbars
PROGRESS_BAR_MIN_HEIGHT = 20             # Minimum height for progress bars
ICON_WIDTH = 100                         # Width for scaled game icons
ICON_HEIGHT = 60                         # Height for scaled game icons

# Auto-close timing
AUTO_CLOSE_DELAY_MS = 3000               # Delay in milliseconds before auto-closing successful setup (3 seconds)

# Font configuration
FONT_FAMILY = 'Segoe UI'                 # Default font family
TITLE_FONT_SIZE = 24                     # Font size for window titles
DESCRIPTION_FONT_SIZE = 14               # Font size for descriptions
LARGE_DESCRIPTION_FONT_SIZE = 16         # Font size for large description text

# Layout spacing
MARGIN_BOTTOM_STANDARD = 10              # Standard bottom margin
MARGIN_TOP_LARGE = 20                    # Large top margin
PADDING_STANDARD = 15                    # Standard padding for containers

# Progress bar configuration
PROGRESS_BAR_MIN = 0                     # Minimum progress bar value
PROGRESS_BAR_MAX = 100                   # Maximum progress bar value

# Keyboard shortcuts
FULLSCREEN_SHORTCUT = "F11"              # Keyboard shortcut for fullscreen toggle

import os
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, 
                           QTextEdit, QHBoxLayout, QMessageBox, QCheckBox, QScrollArea)
from PyQt5.QtGui import QFont, QPixmap, QKeySequence
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QShortcut
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
    
    def __init__(self, task_callback, task_name):
        super().__init__()
        self.task_callback = task_callback
        self.task_name = task_name
    
    def run(self):
        try:
            # Create callback functions that emit signals
            def progress_callback(percent):
                self.progress_updated.emit(percent)
            
            def status_callback(message):
                self.status_updated.emit(message)
            
            # Try calling with callbacks first (new functions)
            try:
                success = self.task_callback(
                    progress_callback=progress_callback,
                    status_callback=status_callback
                )
            except TypeError:
                # Fallback for functions that don't support callbacks (old functions)
                self.status_updated.emit(f"Starting {self.task_name}...")
                self.progress_updated.emit(PROGRESS_START_PERCENT)
                success = self.task_callback()
                if success:
                    self.progress_updated.emit(PROGRESS_COMPLETE_PERCENT)
                    self.status_updated.emit(f"{self.task_name} completed successfully!")
            
            self.finished.emit(success)
                
        except Exception as e:
            self.status_updated.emit(f"{self.task_name} failed: {str(e)}")
            self.finished.emit(False)

class BaseServerSetupWindow(QWidget):
    """
    Base class for all game server setup windows providing standardized UI and functionality.
    
    This class implements a complete step-by-step installation wizard with progress tracking,
    status updates, and thread-safe operations. Game-specific setup windows inherit from
    this class and override methods to provide game-specific behavior.
    
    Attributes:
        game: Game object containing metadata and configuration
        current_step (int): Index of the currently active setup step
        setup_steps (list): List of step dictionaries defining the installation process
        installation_thread (QThread): Background thread for long-running operations
        auto_close_timer (QTimer): Timer for automatic window closing after success
        ui_elements (dict): Dictionary containing UI element references
        
    Key UI Components:
        - Header with game title and icon
        - Progress bar and step indicator
        - Scrollable step description area
        - Real-time status update text area
        - Control buttons (Previous, Continue, Close)
        - Auto-close functionality for successful installations
    
    Threading Safety:
        All UI updates are performed on the main thread through Qt's signal/slot mechanism.
        Long-running operations execute in background threads to maintain responsiveness.
        Proper cleanup ensures no resource leaks or threading issues.
    """
    
    def __init__(self, game):
        """
        Initialize the base setup window.
        
        Args:
            game: Game object containing metadata, configuration, and image path
        """
        super().__init__()
        self.game = game
        self.current_step = 0
        self.worker = None
        self.setup_steps = self.get_setup_steps()  # Get steps from child class
        self.initUI()
    
    def get_setup_steps(self):
        """Return a list of setup steps - must be implemented by child classes
        
        Each step should be a dictionary with:
        {
            'name': 'Step name',
            'description': 'What this step does',
            'function': callable_function,
            'requires_confirmation': bool,
            'confirmation_text': 'Text to show for confirmation'
        }
        """
        raise NotImplementedError("Subclasses must implement get_setup_steps()")
    
    def get_game_specific_ui_elements(self):
        """Return game-specific UI elements like checkboxes or settings
        
        Should return a list of widgets to be added to the final step
        """
        return []  # Default to no elements
    
    def handle_final_step_completion(self):
        """Handle any final actions when setup is complete"""
        return True  # Default implementation returns success
    
    def initUI(self):
        self.setWindowTitle(f'{self.game.name} - Dedicated Server Setup')
        
        # Set up dynamic resizable window for setup
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)  # Minimum size for setup usability
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)  # Default size for setup windows
        
        # Set up fullscreen toggle keyboard shortcut
        self.fullscreen_shortcut = QShortcut(QKeySequence(FULLSCREEN_SHORTCUT), self)
        self.fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
        
        # Set up escape key to exit fullscreen  
        self.escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.escape_shortcut.activated.connect(self.exit_fullscreen)
        
        # Track fullscreen state
        self.is_fullscreen = False
        self.normal_geometry = None
        
        # Apply dark mode styling to the entire window
        self.setStyleSheet(f"""
            {MAIN_WINDOW_STYLE}
            QWidget {{
                background-color: {Colors.BACKGROUND_DARK};
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        
        # Create scroll area for the main content
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
                background-color: {Colors.BACKGROUND_MEDIUM};
                width: {SCROLLBAR_WIDTH}px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {Colors.GRAY_MEDIUM};
                border-radius: 6px;
                min-height: {PROGRESS_BAR_MIN_HEIGHT}px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {Colors.TEXT_SECONDARY};
            }}
        """)
        
        # Content widget for scroll area
        self.content_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(Layout.MARGIN_LARGE, Layout.MARGIN_LARGE, Layout.MARGIN_LARGE, Layout.MARGIN_LARGE)
        main_layout.setSpacing(Layout.SPACING_LARGE)
        
        # Header
        self.add_header(main_layout)
        
        # Progress section
        self.add_progress_section(main_layout)
        
        # Step description section
        self.add_step_description_section(main_layout)
        
        # Status/Log section
        self.add_status_section(main_layout)
        
        # Control buttons
        self.add_control_buttons(main_layout)
        
        # Set up the scroll area
        self.content_widget.setLayout(main_layout)
        scroll_area.setWidget(self.content_widget)
        
        # Main window layout just contains the scroll area
        window_layout = QVBoxLayout()
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(scroll_area)
        
        self.setLayout(window_layout)
        
        # Start the first step
        self.show_current_step()
    
    def add_header(self, layout):
        """Add header with game info"""
        header_layout = QHBoxLayout()
        
        # Game image (if available)
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level since we're now in setup_windows folder
            parent_dir = os.path.dirname(script_dir)
            image_path = os.path.join(parent_dir, self.game.image_url)
            if not os.path.exists(image_path):
                image_path = os.path.join(parent_dir, "images", f"{self.game.name.lower()}_image.jpg")
            
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(ICON_WIDTH, ICON_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                image_label = QLabel()
                image_label.setPixmap(scaled_pixmap)
                image_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {Colors.BACKGROUND_MEDIUM};
                        border: 2px solid {Colors.GRAY_MEDIUM};
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
        title_label.setFont(QFont(FONT_FAMILY, TITLE_FONT_SIZE, QFont.Bold))
        title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        title_layout.addWidget(title_label)
        
        desc_label = QLabel("Setting up your dedicated server environment...")
        desc_label.setFont(QFont(FONT_FAMILY, DESCRIPTION_FONT_SIZE))
        desc_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        title_layout.addWidget(desc_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
    
    def add_progress_section(self, layout):
        """Add progress bar and step indicator"""
        # Step indicator
        self.step_label = QLabel(f"Step 1/{len(self.setup_steps)}: Preparing...")
        self.step_label.setFont(QFont(FONT_FAMILY, DESCRIPTION_FONT_SIZE, QFont.Bold))
        self.step_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-bottom: {MARGIN_BOTTOM_STANDARD}px;")
        layout.addWidget(self.step_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(PROGRESS_BAR_MIN, PROGRESS_BAR_MAX)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {Colors.GRAY_MEDIUM};
                border-radius: {Layout.BORDER_RADIUS_SMALL}px;
                background-color: {Colors.BACKGROUND_MEDIUM};
                text-align: center;
                font-weight: bold;
                color: {Colors.TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                background-color: {Colors.PRIMARY_BLUE};
                border-radius: {Layout.BORDER_RADIUS_SMALL}px;
            }}
        """)
        layout.addWidget(self.progress_bar)
    
    def add_step_description_section(self, layout):
        """Add section that describes what the current step will do"""
        desc_label = QLabel("Step Description:")
        desc_label.setFont(QFont(FONT_FAMILY, LARGE_DESCRIPTION_FONT_SIZE, QFont.Bold))
        desc_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-top: {MARGIN_TOP_LARGE}px;")
        layout.addWidget(desc_label)
        
        self.step_description = QLabel("Preparing setup...")
        self.step_description.setFont(QFont(FONT_FAMILY, DESCRIPTION_FONT_SIZE))
        self.step_description.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.BACKGROUND_MEDIUM};
                border: 2px solid {Colors.GRAY_MEDIUM};
                border-radius: {Layout.BORDER_RADIUS_SMALL}px;
                color: {Colors.TEXT_SECONDARY};
                padding: {PADDING_STANDARD}px;
                margin-bottom: 10px;
            }}
        """)
        self.step_description.setWordWrap(True)
        self.step_description.setMinimumHeight(60)
        layout.addWidget(self.step_description)
    
    def add_status_section(self, layout):
        """Add status text area for logs"""
        status_label = QLabel("Installation Log:")
        status_label.setFont(QFont('Segoe UI', 16, QFont.Bold))
        status_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; margin-top: 20px;")
        layout.addWidget(status_label)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)  # Increased height for larger window
        self.status_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Colors.BACKGROUND_MEDIUM};
                border: 2px solid {Colors.GRAY_MEDIUM};
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
                background-color: {Colors.GRAY_MEDIUM};
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
        
        # Proceed button (changes based on step)
        self.proceed_button = QPushButton("Begin Setup")
        self.proceed_button.setFont(QFont('Segoe UI', 14, QFont.Bold))
        self.proceed_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.PRIMARY_BLUE};
                color: white;
                border: none;
                border-radius: {Layout.BORDER_RADIUS_MEDIUM}px;
                padding: 15px 25px;
                min-width: 120px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {Colors.SECONDARY_BLUE};
            }}
            QPushButton:disabled {{
                background-color: {Colors.GRAY_MEDIUM};
                color: {Colors.TEXT_SECONDARY};
            }}
        """)
        self.proceed_button.clicked.connect(self.proceed_with_step)
        
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        button_layout.addWidget(self.proceed_button)
        
        layout.addLayout(button_layout)
    
    def show_current_step(self):
        """Display information about the current step and ask for confirmation"""
        if self.current_step >= len(self.setup_steps):
            # All steps complete
            self.handle_setup_completion()
            return
        
        step = self.setup_steps[self.current_step]
        step_num = self.current_step + 1
        total_steps = len(self.setup_steps)
        
        # Update UI
        self.step_label.setText(f"Step {step_num}/{total_steps}: {step['name']}")
        self.step_description.setText(step['description'])
        self.progress_bar.setValue(0)
        
        # Add game-specific UI elements for the final step
        if self.current_step == len(self.setup_steps) - 1:  # Last step
            self.add_game_specific_elements()
        
        # Update button text
        if step.get('requires_confirmation', True):
            self.proceed_button.setText(f"Proceed with {step['name']}")
            self.proceed_button.setEnabled(True)
        else:
            self.proceed_button.setText("Continue")
            self.proceed_button.setEnabled(True)
        
        self.log_message(f"Ready to begin: {step['name']}")
        if 'confirmation_text' in step:
            self.log_message(step['confirmation_text'])
    
    def add_game_specific_elements(self):
        """Add game-specific UI elements to the layout"""
        if hasattr(self, '_game_elements_added'):
            return  # Already added
            
        try:
            game_elements = self.get_game_specific_ui_elements()
            if game_elements:
                # Find the main layout and insert elements before the status section
                main_layout = self.content_widget.layout()
                
                # Insert after step description (which should be at index 2)
                # Layout order: header(0), progress(1), step_description(2), [insert here], status(3), buttons(4)
                insert_index = 3  # Insert before status section
                
                for i, element in enumerate(game_elements):
                    main_layout.insertWidget(insert_index + i, element)
                
                self._game_elements_added = True
        except Exception as e:
            self.log_message(f"Failed to add game-specific elements: {str(e)}")
    
    def proceed_with_step(self):
        """Execute the current step"""
        if self.current_step >= len(self.setup_steps):
            return
        
        step = self.setup_steps[self.current_step]
        
        # Show confirmation if required
        if step.get('requires_confirmation', True) and 'confirmation_text' in step:
            reply = QMessageBox.question(self, 'Confirm Action', 
                                       step['confirmation_text'],
                                       QMessageBox.Yes | QMessageBox.No, 
                                       QMessageBox.Yes)
            if reply != QMessageBox.Yes:
                self.log_message(f"Step '{step['name']}' cancelled by user.")
                return
        
        # Disable button during execution
        self.proceed_button.setEnabled(False)
        self.proceed_button.setText("Processing...")
        
        # Handle interactive steps directly on main thread
        if step.get('interactive', False):
            self.log_message(f"Running interactive step: {step['name']}")
            try:
                success = step['function']()
                self.on_step_finished(success)
            except Exception as e:
                self.log_message(f"Error in interactive step: {str(e)}")
                self.on_step_finished(False)
        else:
            # Start the installation worker for non-interactive steps
            self.worker = InstallationWorker(step['function'], step['name'])
            self.worker.progress_updated.connect(self.progress_bar.setValue)
            self.worker.status_updated.connect(self.log_message)
            self.worker.finished.connect(self.on_step_finished)
            self.worker.start()
    
    def on_step_finished(self, success):
        """Handle step completion"""
        if success:
            self.log_message("Step completed successfully!")
            self.current_step += 1
            
            if self.current_step >= len(self.setup_steps):
                # All steps done, show final options
                self.show_final_step()
            else:
                # Move to next step
                self.proceed_button.setText("Next Step")
                self.proceed_button.setEnabled(True)
                self.proceed_button.clicked.disconnect()
                self.proceed_button.clicked.connect(self.go_to_next_step)
        else:
            self.log_message("Step failed. Please check the logs.")
            self.close_button.setEnabled(True)
            self.proceed_button.setText("Retry")
            self.proceed_button.setEnabled(True)
    
    def go_to_next_step(self):
        """Go to the next step and set up the proceed button correctly"""
        self.show_current_step()
        # Reconnect to proceed_with_step for the new step
        self.proceed_button.clicked.disconnect()
        self.proceed_button.clicked.connect(self.proceed_with_step)
    
    def show_final_step(self):
        """Show final step with game-specific options"""
        self.step_label.setText("Final Step: Configuration & Launch")
        self.step_description.setText("Configure final settings and launch your server.")
        self.progress_bar.setValue(100)
        
        # Add game-specific UI elements
        game_elements = self.get_game_specific_ui_elements()
        main_layout = self.layout()
        
        # Insert before the button layout (which is the last item)
        for element in game_elements:
            main_layout.insertWidget(main_layout.count() - 1, element)
        
        # Update button
        self.proceed_button.setText("Complete Setup & Start Server")
        self.proceed_button.setEnabled(True)
        self.proceed_button.clicked.disconnect()
        self.proceed_button.clicked.connect(self.complete_setup)
        
        self.log_message("Setup complete! Configure final options and start your server.")
    
    def complete_setup(self):
        """Complete the setup process"""
        self.log_message("Completing setup...")
        try:
            self.handle_final_step_completion()
        except Exception as e:
            self.log_message(f"Setup completion failed: {str(e)}")
            self.close_button.setEnabled(True)
    
    def handle_setup_completion(self):
        """Handle when all steps are complete"""
        self.log_message("🏁 All installation steps completed! Starting final configuration...")
        
        # Call the game-specific final step completion
        try:
            success = self.handle_final_step_completion()
            
            if success:
                self.step_label.setText("🎉 Setup Complete - Server Running!")
                self.step_description.setText("Your server setup is complete and the server is now running.")
                self.log_message("🎊 Final setup completed successfully!")
                self.log_message("✨ Window will close automatically in 3 seconds...")
                
                # Auto-close the window after successful setup
                QTimer.singleShot(AUTO_CLOSE_DELAY_MS, self.close)
            else:
                self.step_label.setText("⚠️ Setup Complete - Manual Action Required")
                self.step_description.setText("Setup completed but there were some issues. Check the logs above.")
                self.log_message("⚠️ Setup completed with warnings. Please review the logs.")
                
        except Exception as e:
            self.step_label.setText("❌ Setup Error")
            self.step_description.setText("Setup encountered an error during final configuration.")
            self.log_message(f"❌ Final setup failed: {str(e)}")
        
        # Update UI for completion
        self.progress_bar.setValue(100)
        self.proceed_button.setText("Close Setup")
        self.proceed_button.clicked.disconnect()
        self.proceed_button.clicked.connect(self.close)
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
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()
    
    def enter_fullscreen(self):
        """Enter fullscreen mode"""
        if not self.is_fullscreen:
            # Save current geometry
            self.normal_geometry = self.geometry()
            
            # Enter fullscreen
            self.showFullScreen()
            self.is_fullscreen = True
            
            # Update window title to show fullscreen status
            self.setWindowTitle(f'{self.game.name} - Server Setup - Fullscreen (Press F11 or Esc to exit)')
    
    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        if self.is_fullscreen:
            # Exit fullscreen
            self.showNormal()
            
            # Restore previous geometry if available
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            else:
                self.resize(1200, 900)  # Default size
                
            self.is_fullscreen = False
            
            # Restore normal window title
            self.setWindowTitle(f'{self.game.name} - Dedicated Server Setup')
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape and self.is_fullscreen:
            self.exit_fullscreen()
        else:
            super().keyPressEvent(event)
