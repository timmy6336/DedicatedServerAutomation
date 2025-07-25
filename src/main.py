"""
Dedicated Server Automation Application
Main entry point for the PyQt5-based GUI application that manages dedicated game servers.

This application provides a modern interface for:
- Managing multiple game server installations
- Automated server setup with progress tracking
- Real-time server status monitoring
- UPnP port forwarding configuration
- Multi-platform support (Windows/Linux)

Author: Dedicated Server Automation Team
Version: 1.0
License: MIT
"""

import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow


def main():
    """
    Main application entry point.
    
    Initializes the PyQt5 application, creates the main window,
    and starts the event loop.
    
    Returns:
        int: Application exit code (0 for success, non-zero for error)
    """
    # Create the QApplication instance
    # This is required for any PyQt5 GUI application
    app = QApplication(sys.argv)
    
    # Create and configure the main application window
    window = MainWindow()
    
    # Display the window to the user
    window.showMaximized()
    
    # Start the Qt event loop and wait for the application to exit
    # exec_() blocks until the user closes the application
    return app.exec_()


if __name__ == '__main__':
    """
    Script entry point when run directly (not imported).
    
    Calls main() and exits with the returned exit code.
    This allows the application to properly report success/failure
    to the operating system.
    """
    sys.exit(main())
