"""
Game Server Automation Utilities

This module provides a comprehensive set of utility classes and functions for automating
the installation, configuration, and management of dedicated game servers. It serves as
the core backend for the server automation application, offering reusable functionality
that can be shared across multiple game implementations.

The module is organized into several utility classes, each handling a specific aspect
of server management:

Classes:
    SteamCMDUtils: Handles SteamCMD installation, server downloads, and updates
    UPnPUtils: Manages automatic port forwarding configuration via UPnP
    ServerUtils: Provides server startup, path management, and lifecycle operations
    NetworkUtils: Network connectivity testing and IP address resolution
    FileUtils: Safe file and directory operations with error handling
    GameConfig: Centralized game configuration and metadata storage

Key Features:
- Cross-platform compatibility (Windows/Linux)
- Progress tracking with callback support for UI integration
- Robust error handling and recovery mechanisms
- File-based verification for reliable success detection
- Smart SteamCMD management with preservation options
- Automatic network configuration via UPnP
- Comprehensive logging and status reporting

This refactored architecture separates concerns and promotes code reuse while
maintaining backward compatibility with existing game-specific scripts.
"""

# ============================================================================
# PROGRESS TRACKING CONSTANTS
# ============================================================================

# Progress percentage constants (0-100)
PROGRESS_MIN = 0                     # Minimum progress value
PROGRESS_MAX = 100                   # Maximum progress value (completion)
PROGRESS_INITIAL_SETUP = 10          # Progress after initial directory setup
PROGRESS_DOWNLOAD_START = 20         # Progress when download begins
PROGRESS_DOWNLOAD_WEIGHT = 60        # Weight allocation for download phase (20-80%)
PROGRESS_DOWNLOAD_MAX = 80           # Maximum progress during download phase
PROGRESS_EXTRACTION_START = 85       # Progress when extraction begins
PROGRESS_COMPLETE = 100              # Progress when installation completes

# SteamCMD installation progress stages
STEAMCMD_INITIAL_SETUP = 10          # Initial setup progress
STEAMCMD_EXTRACTION_COMPLETE = 100   # SteamCMD extraction complete
STEAMCMD_DOWNLOAD_START = 20         # SteamCMD download start
STEAMCMD_EXECUTION_START = 30        # SteamCMD execution start

# Server installation progress constants
SERVER_INITIAL_PROGRESS = 30         # Starting progress for server installation
SERVER_PROGRESS_INIT = 0             # Initial server progress value
SERVER_PROGRESS_FREQUENCY = 3        # Update progress every N lines
SERVER_PROGRESS_INCREMENT = 1        # Progress increment per update
SERVER_PROGRESS_MAXIMUM = 89         # Maximum progress during installation
SERVER_PROGRESS_NEAR_COMPLETE = 85   # Progress threshold for near completion
SERVER_TIMEOUT_INCREMENT = 0.5       # Incremental progress during timeouts
SERVER_PERIODIC_UPDATE_LINES = 20    # Lines threshold for periodic updates
SERVER_MAX_OUTPUT_LINES = 20         # Maximum output lines to keep in memory

# Timing constants (seconds)
SELECT_TIMEOUT_SECONDS = 1.0         # Timeout for process output selection
PROGRESS_UPDATE_INTERVAL = 5.0       # Interval for forced progress updates
UPNP_DISCOVERY_DELAY_MS = 200        # UPnP discovery delay in milliseconds

# Network constants
GOOGLE_DNS_IP = "8.8.8.8"           # Google DNS server for connectivity tests
GOOGLE_DNS_PORT = 80                 # Port for Google DNS connectivity test

# Buffer and processing constants
PROCESS_BUFFER_SIZE = 0              # Unbuffered process output (immediate)
PROGRESS_UPDATE_FREQUENCY = 5        # Force update every N lines
PROGRESS_TIME_THRESHOLD = 5.0        # Time threshold for forced updates
PROGRESS_CHANGE_THRESHOLD = 1        # Minimum progress change for updates

# SteamCMD error codes
STEAMCMD_ERROR_CODE_8 = 8            # SteamCMD error code 8 (download error)

# Progress scaling constants for different phases
DOWNLOAD_PROGRESS_SCALE = 0.6        # Scale factor for download progress (60%)
EXTRACTION_PROGRESS_ADD = 3          # Progress increment for extraction
VALIDATION_PROGRESS_ADD = 2          # Progress increment for validation
COMPLETION_PROGRESS_ADD = 5          # Progress increment for completion
STEAMCMD_PROGRESS_SCALE_BASE = 30    # Base progress for SteamCMD scaling
STEAMCMD_PROGRESS_SCALE_MAX = 90     # Maximum scaled progress for SteamCMD

import shutil
import os
import subprocess
import urllib.request
import zipfile
import requests
import platform
import socket
import re
from typing import Callable, Optional, Tuple, Union


class SteamCMDUtils:
    """
    Utilities for managing SteamCMD installation and operations.
    
    This class provides comprehensive SteamCMD management functionality including
    automated download, installation, server management, and cleanup operations.
    All methods are static for easy access without instantiation.
    
    SteamCMD is Valve's command-line version of the Steam client used for downloading
    and updating dedicated servers. This class abstracts the complexity of SteamCMD
    operations and provides robust error handling and progress tracking.
    
    Key Features:
    - Cross-platform SteamCMD installation (Windows/Linux)
    - Progress tracking with callback support for UI integration
    - Robust download and extraction with error recovery
    - Server installation and update management
    - File-based success verification for reliability
    - Clean uninstallation with optional preservation
    
    Attributes:
        STEAMCMD_URL (str): Official SteamCMD download URL from Valve
    """
    
    STEAMCMD_URL = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
    
    @staticmethod
    def get_steamcmd_paths() -> Tuple[str, str]:
        """
        Get platform-appropriate SteamCMD directory and executable paths.
        
        Determines the correct installation directory and executable name for
        SteamCMD based on the current operating system. Uses standard user
        directories to avoid permission issues.
        
        Returns:
            Tuple[str, str]: A tuple containing (steamcmd_directory, steamcmd_executable)
                - On Windows: (%USERPROFILE%\\SteamCMD, steamcmd.exe)
                - On Linux: (~/SteamCMD, steamcmd.sh)
                
        Example:
            steamcmd_dir, steamcmd_exe = SteamCMDUtils.get_steamcmd_paths()
            print(f"SteamCMD will be installed at: {steamcmd_dir}")
        """
        if platform.system().lower() == 'windows':
            steamcmd_dir = os.path.expandvars(r'%USERPROFILE%\SteamCMD')
            steamcmd_exe = os.path.join(steamcmd_dir, 'steamcmd.exe')
        else:
            steamcmd_dir = os.path.expanduser('~/SteamCMD')
            steamcmd_exe = os.path.join(steamcmd_dir, 'steamcmd.sh')
        
        return steamcmd_dir, steamcmd_exe
    
    @staticmethod
    def is_steamcmd_installed() -> bool:
        """
        Check if SteamCMD is already installed on the system.
        
        Verifies the presence of the SteamCMD executable at the expected
        location based on the current platform. This is a quick check
        that doesn't verify the integrity of the installation.
        
        Returns:
            bool: True if SteamCMD executable exists, False otherwise
            
        Note:
            This method only checks for the existence of the executable file.
            It does not verify that SteamCMD is functional or up to date.
            
        Example:
            if SteamCMDUtils.is_steamcmd_installed():
                print("SteamCMD is ready to use")
            else:
                print("SteamCMD needs to be installed")
        """
        _, steamcmd_exe = SteamCMDUtils.get_steamcmd_paths()
        return os.path.exists(steamcmd_exe)
    
    @staticmethod
    def download_steamcmd(progress_callback: Optional[Callable[[int], None]] = None, 
                         status_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Download and install SteamCMD with comprehensive progress tracking.
        
        Downloads the official SteamCMD distribution from Valve's CDN, extracts it
        to the appropriate platform-specific directory, and sets up the installation.
        If SteamCMD is already present, the function will skip the download process.
        
        This method provides detailed progress tracking through callback functions,
        making it suitable for integration with GUI progress bars and status displays.
        The download includes automatic error handling and cleanup on failure.
        
        Args:
            progress_callback (callable, optional): Function to call with progress 
                percentage (0-100). Called frequently during download and extraction.
                Signature: progress_callback(percent: int) -> None
            status_callback (callable, optional): Function to call with descriptive
                status messages. Provides real-time information about current operations.
                Signature: status_callback(message: str) -> None
                
        Returns:
            bool: True if SteamCMD was successfully downloaded/installed or already
                exists, False if download or extraction failed.
                
        Raises:
            No exceptions are raised; all errors are handled internally and reported
            through the status_callback if provided.
            
        Progress Phases:
            - 10%: Initial setup and directory creation
            - 20-80%: File download (with continuous updates)
            - 85%: Download complete, starting extraction
            - 100%: Installation complete
            
        Example:
            def on_progress(percent):
                print(f"Download progress: {percent}%")
                
            def on_status(message):
                print(f"Status: {message}")
                
            success = SteamCMDUtils.download_steamcmd(on_progress, on_status)
            if success:
                print("SteamCMD is ready for use!")
        """
        if progress_callback:
            progress_callback(PROGRESS_INITIAL_SETUP)
        if status_callback:
            status_callback("Checking SteamCMD installation...")
            
        steamcmd_dir, steamcmd_exe = SteamCMDUtils.get_steamcmd_paths()
        
        if not os.path.exists(steamcmd_dir):
            os.makedirs(steamcmd_dir)
        
        steamcmd_zip = os.path.join(steamcmd_dir, 'steamcmd.zip')
        
        if not os.path.exists(steamcmd_exe):
            if status_callback:
                status_callback("Downloading SteamCMD...")
            if progress_callback:
                progress_callback(PROGRESS_DOWNLOAD_START)
                
            print("Downloading SteamCMD...")
            
            # Download with progress tracking
            def download_progress_hook(block_num, block_size, total_size):
                if progress_callback and total_size > PROGRESS_MIN:
                    downloaded = block_num * block_size
                    percent = min(int((downloaded / total_size) * PROGRESS_DOWNLOAD_WEIGHT) + PROGRESS_DOWNLOAD_START, PROGRESS_DOWNLOAD_MAX)  # 20-80% for download
                    progress_callback(percent)
            
            try:
                urllib.request.urlretrieve(SteamCMDUtils.STEAMCMD_URL, steamcmd_zip, reporthook=download_progress_hook)
                
                if status_callback:
                    status_callback("Extracting SteamCMD...")
                if progress_callback:
                    progress_callback(PROGRESS_EXTRACTION_START)
                    
                with zipfile.ZipFile(steamcmd_zip, 'r') as zip_ref:
                    zip_ref.extractall(steamcmd_dir)
                os.remove(steamcmd_zip)
                
                if status_callback:
                    status_callback("SteamCMD downloaded and extracted successfully!")
                if progress_callback:
                    progress_callback(PROGRESS_COMPLETE)
                print("SteamCMD downloaded and extracted.")
                return True
                
            except Exception as e:
                if status_callback:
                    status_callback(f"Failed to download SteamCMD: {str(e)}")
                print(f"Failed to download SteamCMD: {e}")
                return False
        else:
            if status_callback:
                status_callback("SteamCMD already present - skipping download")
            if progress_callback:
                progress_callback(STEAMCMD_EXTRACTION_COMPLETE)
            print("SteamCMD already present.")
            return True
    
    @staticmethod
    def install_or_update_server(app_id: str, 
                               server_dir: str,
                               server_executable_name: str,
                               progress_callback: Optional[Callable[[int], None]] = None,
                               status_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Generic function to install or update a Steam-based game server
        
        Args:
            app_id: Steam application ID for the server
            server_dir: Directory where server should be installed
            server_executable_name: Name of the server executable to check for completion
            progress_callback: Function to call with progress percentage (0-100)
            status_callback: Function to call with status messages
            
        Returns:
            bool: True if successful, False otherwise
        """
        if progress_callback:
            progress_callback(STEAMCMD_INITIAL_SETUP)
        if status_callback:
            status_callback("Checking server installation...")
            
        server_exe = os.path.join(server_dir, server_executable_name)
        if os.path.exists(server_exe):
            if status_callback:
                status_callback("Server already installed - skipping installation")
            if progress_callback:
                progress_callback(PROGRESS_COMPLETE)
            print("Server already installed. Skipping installation.")
            return True
        
        if status_callback:
            status_callback("Installing/updating server...")
        if progress_callback:
            progress_callback(STEAMCMD_DOWNLOAD_START)
        print(f"Installing/updating server (App ID: {app_id})...")
        
        _, steamcmd_exe = SteamCMDUtils.get_steamcmd_paths()
        if not os.path.exists(steamcmd_exe):
            if status_callback:
                status_callback("SteamCMD not found! Please install SteamCMD first.")
            print("SteamCMD not found! Run SteamCMDUtils.download_steamcmd() first.")
            return False
        
        # Ensure server directory exists
        if not os.path.exists(server_dir):
            os.makedirs(server_dir)
        
        cmd = [
            steamcmd_exe,
            "+force_install_dir", server_dir,
            "+login", "anonymous",
            "+app_update", app_id, "validate",
            "+quit"
        ]
        
        if status_callback:
            status_callback("Starting SteamCMD to download server files...")
        if progress_callback:
            progress_callback(STEAMCMD_EXECUTION_START)
        
        try:
            import select
            import time
            
            # Use Popen for real-time output capture with unbuffered output
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                universal_newlines=True,
                bufsize=PROCESS_BUFFER_SIZE,  # Unbuffered
                shell=True
            )
            
            import time
            progress_value = SERVER_INITIAL_PROGRESS
            last_progress_update = SERVER_PROGRESS_INIT
            last_update_time = time.time()
            lines_processed = SERVER_PROGRESS_INIT
            recent_output_lines = []  # Track recent output for error detection
            
            while True:
                current_time = time.time()
                
                # Check if process is still running
                if process.poll() is not None:
                    # Process finished, read any remaining output
                    remaining_output = process.stdout.read()
                    if remaining_output:
                        for line in remaining_output.strip().split('\n'):
                            if line.strip():
                                print(line.strip())
                                if status_callback:
                                    progress_value = SteamCMDUtils._parse_steamcmd_output(line.strip(), progress_value, status_callback)
                    break
                
                if platform.system().lower() == 'windows':
                    # Windows: Simple approach with readline and timeout handling
                    try:
                        output = process.stdout.readline()
                    except (OSError, IOError):
                        output = None
                else:
                    # Unix-like systems can use select for non-blocking read
                    ready, _, _ = select.select([process.stdout], [], [], SELECT_TIMEOUT_SECONDS)  # 1 second timeout
                    output = None
                    if ready:
                        output = process.stdout.readline()
                
                if output:
                    line = output.strip()
                    if line:  # Only process non-empty lines
                        lines_processed += 1
                        recent_output_lines.append(line)  # Track recent output
                        if len(recent_output_lines) > SERVER_MAX_OUTPUT_LINES:  # Keep only last 20 lines
                            recent_output_lines.pop(0)
                        
                        print(line)  # Keep console output
                        
                        # Update progress more frequently based on line count
                        if lines_processed % SERVER_PROGRESS_FREQUENCY == 0:  # Every 3 lines instead of 5
                            progress_value = min(progress_value + SERVER_PROGRESS_INCREMENT, SERVER_PROGRESS_MAXIMUM)
                        
                        if status_callback:
                            progress_value = SteamCMDUtils._parse_steamcmd_output(line, progress_value, status_callback)
                        
                        # Force progress update every 5 lines OR every 5 seconds OR significant progress change
                        time_since_update = current_time - last_update_time
                        if progress_callback and (lines_processed % PROGRESS_UPDATE_FREQUENCY == 0 or 
                                                time_since_update >= PROGRESS_UPDATE_INTERVAL or 
                                                abs(progress_value - last_progress_update) >= PROGRESS_CHANGE_THRESHOLD):
                            progress_callback(int(progress_value))
                            last_progress_update = progress_value
                            last_update_time = current_time
                
                # Force a progress update every 5 seconds even if no output (keeps UI responsive)
                else:
                    time_since_update = current_time - last_update_time
                    if time_since_update >= 5.0:  # Every 5 seconds
                        if lines_processed > 20 and progress_value < 85:  # After some initial setup
                            progress_value = min(progress_value + 0.5, 89)
                        if progress_callback:
                            progress_callback(int(progress_value))
                            last_progress_update = progress_value
                            last_update_time = current_time
                        
                        # Update status to show we're still working
                        if status_callback and lines_processed > 20:
                            status_callback("🔄 Installation in progress... (this may take a while)")
            
            return_code = process.poll()
            
            # Check for specific Steam error patterns in the output
            steam_error_detected = False
            error_details = ""
            
            # Look for specific error patterns in recent output lines
            if return_code == 8:
                steam_error_detected = True
                error_details = "SteamCMD reported an error during download (exit code 8)"
            elif any("Error! App" in line and "state is 0x" in line for line in recent_output_lines):
                steam_error_detected = True
                error_details = "Steam reported application state error (download corruption)"
            elif any("stopping" in line and "progress:" in line for line in recent_output_lines):
                steam_error_detected = True  
                error_details = "Download was interrupted before completion"
            
            # Check if installation was actually successful by verifying the server files exist
            server_exe_check = os.path.join(server_dir, server_executable_name)
            installation_successful = os.path.exists(server_exe_check)
            
            if installation_successful:
                if status_callback:
                    status_callback("Server installed/updated successfully!")
                if progress_callback:
                    progress_callback(100)
                print("Server installed/updated.")
                return True
            elif steam_error_detected:
                if status_callback:
                    status_callback(f"❌ Steam download error detected: {error_details}")
                    status_callback("💡 Suggestion: Try running the installation again - Steam downloads can sometimes fail due to network issues")
                print(f"Steam download failed: {error_details}")
                print("Suggestion: Retry the installation - this is often a temporary network issue")
                return False
            else:
                if status_callback:
                    status_callback(f"Installation incomplete - server files not found (SteamCMD exit code: {return_code})")
                print(f"Failed to install/update server. Exit code: {return_code}")
                return False
                
        except Exception as e:
            if status_callback:
                status_callback(f"Error during installation: {str(e)}")
            print(f"Error during installation: {e}")
            return False
    
    @staticmethod
    def _parse_steamcmd_output(line: str, progress_value: float, status_callback: Callable[[str], None]) -> float:
        """Parse SteamCMD output for meaningful status updates and progress"""
        
        # Check for error conditions first
        if "Error!" in line and "state is 0x" in line:
            status_callback(f"❌ Steam Error: {line}")
            # Don't increment progress on errors
            return progress_value
        elif "stopping" in line and "progress:" in line:
            status_callback(f"⚠️ Download interrupted: {line}")
            return progress_value
        elif "Please use force_install_dir before logon!" in line:
            status_callback("❌ SteamCMD command order error detected")
            return progress_value
        
        # Parse SteamCMD output for meaningful status updates
        if "Downloading" in line or "downloading" in line:
            status_callback(f"📥 {line}")
            progress_value = min(progress_value + 3, 85)
        elif "Verifying" in line or "verifying" in line:
            status_callback(f"✓ {line}")
            progress_value = min(progress_value + 2, 90)
        elif "Update state" in line:
            if "0x81" in line:  # Common Steam update state
                status_callback("🔄 Preparing download...")
            elif "0x61" in line:
                status_callback("🔄 Download in progress...")
                progress_value = min(progress_value + 2, 80)
            elif "0x101" in line:
                status_callback("🔄 Committing changes...")
                progress_value = min(progress_value + 3, 88)
            elif "0x461" in line:
                status_callback("⚠️ Download stopping...")
                # Don't increment progress when stopping
            else:
                status_callback(f"📊 {line}")
        elif "Success" in line or "success" in line:
            status_callback("✅ Download completed successfully!")
            progress_value = 95
        elif "Logged in OK" in line:
            status_callback("🔑 Logged into Steam successfully")
            progress_value = min(progress_value + 5, 50)
        elif "AppCacheVersion" in line:
            status_callback("📋 Loading app information...")
            progress_value = min(progress_value + 3, 55)
        elif "fully installed" in line or "Up-To-Date" in line:
            status_callback("✅ Server files are up to date!")
            progress_value = 95
        elif "preallocating" in line:
            status_callback("💾 Allocating disk space...")
            progress_value = min(progress_value + 2, 85)
        elif "%" in line and ("downloaded" in line or "progress" in line):
            # Try to extract percentage if available
            try:
                import re
                match = re.search(r'(\d+)%', line)
                if match:
                    percent = int(match.group(1))
                    adjusted_percent = min(30 + int(percent * 0.6), 90)  # Scale to 30-90%
                    progress_value = adjusted_percent
                    status_callback(f"📥 Downloading: {percent}%")
            except Exception:
                status_callback(f"📥 {line}")
                progress_value = min(progress_value + 1, 85)
        elif "Installing" in line or "installing" in line:
            status_callback(f"⚙️ {line}")
            progress_value = min(progress_value + 2, 88)
        elif "Mounting" in line or "mounting" in line:
            status_callback(f"🔧 {line}")
            progress_value = min(progress_value + 1, 70)
        elif line and not line.startswith("Steam>") and len(line.strip()) > 3:
            # Generic progress for any meaningful output
            progress_value = min(progress_value + 0.3, 90)
        
        return progress_value
    
    @staticmethod
    def uninstall_steamcmd() -> bool:
        """Remove SteamCMD installation"""
        steamcmd_dir, _ = SteamCMDUtils.get_steamcmd_paths()
        
        if os.path.exists(steamcmd_dir):
            try:
                shutil.rmtree(steamcmd_dir)
                print(f"SteamCMD uninstalled from {steamcmd_dir}.")
                return True
            except Exception as e:
                print(f"Failed to uninstall SteamCMD: {e}")
                return False
        else:
            print("SteamCMD is not installed.")
            return False


class UPnPUtils:
    """Utilities for UPnP port forwarding management"""
    
    @staticmethod
    def setup_port_forwarding(port: int, description: str = "Game Server") -> bool:
        """
        Set up UPnP port forwarding for a given port
        
        Args:
            port: Port number to forward
            description: Description for the port forwarding rule
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import miniupnpc
            
            upnp = miniupnpc.UPnP()
            upnp.discoverdelay = UPNP_DISCOVERY_DELAY_MS
            upnp.discover()
            upnp.selectigd()
            local_ip = upnp.lanaddr
            upnp.addportmapping(port, 'TCP', local_ip, port, description, '')
            upnp.addportmapping(port, 'UDP', local_ip, port, description, '')
            print(f"UPnP port forwarding set for {port} TCP/UDP to {local_ip}")
            return True
        except ImportError:
            print("miniupnpc not installed. Skipping UPnP port forwarding.")
            return False
        except Exception as e:
            print(f"UPnP port forwarding failed: {e}")
            return False
    
    @staticmethod
    def remove_port_forwarding(port: int) -> bool:
        """
        Remove UPnP port forwarding for a given port
        
        Args:
            port: Port number to remove forwarding for
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import miniupnpc
            
            upnp = miniupnpc.UPnP()
            upnp.discoverdelay = UPNP_DISCOVERY_DELAY_MS
            upnp.discover()
            upnp.selectigd()
            
            tcp_removed = False
            udp_removed = False
            
            # Try removing TCP rule
            try:
                tcp_removed = upnp.deleteportmapping(port, 'TCP', '')
                if tcp_removed:
                    print(f"UPnP TCP port forwarding rule for {port} removed.")
                else:
                    print(f"No UPnP TCP port forwarding rule for {port} found to remove.")
            except Exception as e:
                if "Invalid Args" in str(e):
                    print(f"No UPnP TCP port forwarding rule for {port} found (or router doesn't support removal).")
                    tcp_removed = False
                else:
                    print(f"Failed to remove UPnP TCP port forwarding rule: {e}")
                    tcp_removed = False
            
            # Try removing UDP rule
            try:
                udp_removed = upnp.deleteportmapping(port, 'UDP', '')
                if udp_removed:
                    print(f"UPnP UDP port forwarding rule for {port} removed.")
                else:
                    print(f"No UPnP UDP port forwarding rule for {port} found to remove.")
            except Exception as e:
                if "Invalid Args" in str(e):
                    print(f"No UPnP UDP port forwarding rule for {port} found (or router doesn't support removal).")
                    udp_removed = False
                else:
                    print(f"Failed to remove UPnP UDP port forwarding rule: {e}")
                    udp_removed = False
            
            return tcp_removed or udp_removed
            
        except ImportError:
            print("miniupnpc not installed. Cannot remove UPnP port forwarding rule.")
            return False
        except Exception as e:
            print(f"Failed to initialize UPnP for removing port forwarding rule: {e}")
            return False


class ServerUtils:
    """Utilities for server process management"""
    
    @staticmethod
    def start_server(server_executable_path: str, 
                    working_directory: Optional[str] = None,
                    server_args: Optional[list] = None) -> bool:
        """
        Start a server executable in a separate command prompt window
        
        Args:
            server_executable_path: Full path to the server executable
            working_directory: Working directory for the server (defaults to executable directory)
            server_args: Additional arguments to pass to the server
            
        Returns:
            bool: True if server started successfully, False otherwise
        """
        if not os.path.exists(server_executable_path):
            print(f"Server executable not found: {server_executable_path}")
            return False
        
        if working_directory is None:
            working_directory = os.path.dirname(server_executable_path)
        
        # Build the command for the server
        server_cmd = [server_executable_path]
        if server_args:
            server_cmd.extend(server_args)
        
        # Create a temporary batch file to run the server
        # This avoids complex quoting issues with the 'start' command
        import tempfile
        
        # Create temporary batch file
        batch_content = f'''@echo off
title Valheim Dedicated Server - {os.path.basename(server_executable_path)}
cd /d "{working_directory}"
echo Starting Valheim server...
echo Working directory: {working_directory}
echo Command: {' '.join(f'"{arg}"' if ' ' in str(arg) else str(arg) for arg in server_cmd)}
echo.
'''
        
        # Add the actual server command with proper quoting for each argument
        # Each argument that contains spaces or special characters should be individually quoted
        quoted_args = []
        for arg in server_cmd:
            arg_str = str(arg)
            # Quote arguments that contain spaces or special characters
            if ' ' in arg_str or any(char in arg_str for char in ['&', '|', '<', '>', '^', '%']):
                quoted_args.append(f'"{arg_str}"')
            else:
                quoted_args.append(arg_str)
        
        batch_content += ' '.join(quoted_args) + '\n'
        
        # Add pause at the end to keep window open if server crashes
        batch_content += '''
echo.
echo Server has stopped.
echo Press any key to close this window...
pause >nul
'''
        
        # Write to temporary batch file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as batch_file:
            batch_file.write(batch_content)
            batch_file_path = batch_file.name
        
        # Start the batch file in a new command prompt window
        # Use a single string command for shell=True to avoid argument parsing issues
        start_cmd = f'cmd /c start "Valheim Server" "{batch_file_path}"'
        
        print(f"Starting server in new window using batch file: {batch_file_path}")
        print(f"Working directory: {working_directory}")
        print(f"Server command: {' '.join(str(arg) for arg in server_cmd)}")
        try:
            subprocess.Popen(start_cmd, shell=True)
            print("Server started successfully in a new command prompt window.")
            print("The server console will remain open in a separate window.")
            print("To stop the server, close the server console window or use Ctrl+C in it.")
            print(f"Note: Temporary batch file created at: {batch_file_path}")
            
            return True
        except Exception as e:
            print(f"Failed to start server: {e}")
            # Clean up batch file if start failed
            try:
                os.unlink(batch_file_path)
            except OSError:
                pass  # Ignore cleanup errors
            return False
    
    @staticmethod
    def get_server_paths(game_name: str) -> Tuple[str, str]:
        """
        Get standard server installation paths for a given game
        
        Args:
            game_name: Name of the game (e.g., 'palworld', 'valheim')
            
        Returns:
            Tuple of (server_directory, executable_name)
        """
        game_name_lower = game_name.lower()
        
        if platform.system().lower() == 'windows':
            base_dir = os.path.expandvars(r'%USERPROFILE%\Steam\steamapps\common')
            exe_extension = '.exe'
        else:
            base_dir = os.path.expanduser('~/Steam/steamapps/common')
            exe_extension = ''
        
        # Game-specific paths
        if game_name_lower == 'palworld':
            server_dir = os.path.join(base_dir, 'Palworld Dedicated Server')
            executable_name = f'PalServer{exe_extension}'
        elif game_name_lower == 'valheim':
            server_dir = os.path.join(base_dir, 'Valheim dedicated server')
            if platform.system().lower() == 'windows':
                executable_name = 'valheim_server.exe'
            else:
                executable_name = 'valheim_server.sh'
        else:
            # Generic fallback
            server_dir = os.path.join(base_dir, f'{game_name} Dedicated Server')
            executable_name = f'{game_name}Server{exe_extension}'
        
        return server_dir, executable_name
    
    @staticmethod
    def uninstall_server(server_directory: str) -> bool:
        """
        Remove a server installation
        
        Args:
            server_directory: Directory containing the server files
            
        Returns:
            bool: True if successful, False otherwise
        """
        if os.path.exists(server_directory):
            try:
                shutil.rmtree(server_directory)
                print(f"Server uninstalled from {server_directory}.")
                return True
            except Exception as e:
                print(f"Failed to uninstall server: {e}")
                return False
        else:
            print("Server is not installed.")
            return False


class NetworkUtils:
    """Utilities for network-related operations"""
    
    @staticmethod
    def get_local_ip() -> str:
        """Get the local IP address of the machine"""
        try:
            # Connect to a remote address to determine the local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect((GOOGLE_DNS_IP, GOOGLE_DNS_PORT))
                local_ip = s.getsockname()[0]
            return local_ip
        except Exception:
            return "Unable to determine"
    
    @staticmethod
    def get_public_ip() -> str:
        """Get the public IP address"""
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text.strip()
        except Exception:
            return "Unable to determine"
    
    @staticmethod
    def is_port_in_use(port: int, host: str = 'localhost') -> bool:
        """
        Check if a port is currently in use
        
        Args:
            port: Port number to check
            host: Host to check (default: localhost)
            
        Returns:
            bool: True if port is in use, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                return result == 0
        except Exception:
            return False


class FileUtils:
    """Utilities for file and directory operations"""
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> bool:
        """
        Ensure a directory exists, creating it if necessary
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            bool: True if directory exists or was created successfully
        """
        try:
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            return True
        except Exception as e:
            print(f"Failed to create directory {directory_path}: {e}")
            return False
    
    @staticmethod
    def safe_remove_directory(directory_path: str) -> bool:
        """
        Safely remove a directory and all its contents
        
        Args:
            directory_path: Path to the directory to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(directory_path):
                shutil.rmtree(directory_path)
                return True
            return True  # Directory doesn't exist, so "removal" is successful
        except Exception as e:
            print(f"Failed to remove directory {directory_path}: {e}")
            return False
    
    @staticmethod
    def is_server_installed(server_directory: str, executable_name: str) -> bool:
        """
        Check if a server is properly installed by verifying key files exist
        
        Args:
            server_directory: Directory where server should be installed
            executable_name: Name of the main server executable
            
        Returns:
            bool: True if server appears to be installed
        """
        if not os.path.exists(server_directory):
            return False
        
        executable_path = os.path.join(server_directory, executable_name)
        return os.path.exists(executable_path)


# Game-specific configuration constants
class GameConfig:
    """Configuration constants for supported games"""
    
    PALWORLD = {
        'app_id': '2394010',
        'name': 'Palworld',
        'default_port': 8211,
        'executable_name': 'PalServer.exe' if platform.system().lower() == 'windows' else 'PalServer',
        'server_dir_name': 'Palworld Dedicated Server'
    }
    
    VALHEIM = {
        'app_id': '896660',
        'name': 'Valheim',
        'default_port': 2456,
        'executable_name': 'valheim_server.exe' if platform.system().lower() == 'windows' else 'valheim_server.sh',
        'server_dir_name': 'Valheim dedicated server'
    }
