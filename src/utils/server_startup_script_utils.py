"""
Utility functions for game server startup scripts.
Contains reusable functionality that can be shared across different game server implementations.
"""

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
    """Utilities for managing SteamCMD installation and operations"""
    
    STEAMCMD_URL = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
    
    @staticmethod
    def get_steamcmd_paths() -> Tuple[str, str]:
        """Get platform-appropriate SteamCMD directory and executable paths"""
        if platform.system().lower() == 'windows':
            steamcmd_dir = os.path.expandvars(r'%USERPROFILE%\SteamCMD')
            steamcmd_exe = os.path.join(steamcmd_dir, 'steamcmd.exe')
        else:
            steamcmd_dir = os.path.expanduser('~/SteamCMD')
            steamcmd_exe = os.path.join(steamcmd_dir, 'steamcmd.sh')
        
        return steamcmd_dir, steamcmd_exe
    
    @staticmethod
    def is_steamcmd_installed() -> bool:
        """Check if SteamCMD is already installed"""
        _, steamcmd_exe = SteamCMDUtils.get_steamcmd_paths()
        return os.path.exists(steamcmd_exe)
    
    @staticmethod
    def download_steamcmd(progress_callback: Optional[Callable[[int], None]] = None, 
                         status_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Download and install SteamCMD with progress tracking
        
        Args:
            progress_callback: Function to call with progress percentage (0-100)
            status_callback: Function to call with status messages
            
        Returns:
            bool: True if successful, False otherwise
        """
        if progress_callback:
            progress_callback(10)
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
                progress_callback(20)
                
            print("Downloading SteamCMD...")
            
            # Download with progress tracking
            def download_progress_hook(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(int((downloaded / total_size) * 60) + 20, 80)  # 20-80% for download
                    progress_callback(percent)
            
            try:
                urllib.request.urlretrieve(SteamCMDUtils.STEAMCMD_URL, steamcmd_zip, reporthook=download_progress_hook)
                
                if status_callback:
                    status_callback("Extracting SteamCMD...")
                if progress_callback:
                    progress_callback(85)
                    
                with zipfile.ZipFile(steamcmd_zip, 'r') as zip_ref:
                    zip_ref.extractall(steamcmd_dir)
                os.remove(steamcmd_zip)
                
                if status_callback:
                    status_callback("SteamCMD downloaded and extracted successfully!")
                if progress_callback:
                    progress_callback(100)
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
                progress_callback(100)
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
            progress_callback(10)
        if status_callback:
            status_callback(f"Checking server installation...")
            
        server_exe = os.path.join(server_dir, server_executable_name)
        if os.path.exists(server_exe):
            if status_callback:
                status_callback("Server already installed - skipping installation")
            if progress_callback:
                progress_callback(100)
            print("Server already installed. Skipping installation.")
            return True
        
        if status_callback:
            status_callback("Installing/updating server...")
        if progress_callback:
            progress_callback(20)
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
            "+login", "anonymous",
            "+force_install_dir", server_dir,
            "+app_update", app_id, "validate",
            "+quit"
        ]
        
        if status_callback:
            status_callback("Starting SteamCMD to download server files...")
        if progress_callback:
            progress_callback(30)
        
        try:
            # Use Popen for real-time output capture with unbuffered output
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                universal_newlines=True,
                bufsize=0,  # Unbuffered
                shell=True
            )
            
            progress_value = 30
            last_progress_update = 0
            lines_processed = 0
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                
                if output:
                    line = output.strip()
                    lines_processed += 1
                    print(line)  # Keep console output
                    
                    # Update progress more frequently based on line count
                    if lines_processed % 5 == 0:  # Every 5 lines
                        progress_value = min(progress_value + 1, 89)
                    
                    if status_callback:
                        progress_value = SteamCMDUtils._parse_steamcmd_output(line, progress_value, status_callback)
                    
                    # Force progress update every 10 lines or if significant progress change
                    if progress_callback and (lines_processed % 10 == 0 or abs(progress_value - last_progress_update) >= 2):
                        progress_callback(int(progress_value))
                        last_progress_update = progress_value
                
                # Force a small progress update even if no output (keeps UI responsive)
                elif lines_processed > 50 and progress_value < 85:  # After initial setup
                    progress_value = min(progress_value + 0.1, 89)
                    if progress_callback and abs(progress_value - last_progress_update) >= 1:
                        progress_callback(int(progress_value))
                        last_progress_update = progress_value
            
            return_code = process.poll()
            
            # Check if installation was actually successful by verifying the server files exist
            # SteamCMD sometimes returns non-zero exit codes even when successful
            server_exe_check = os.path.join(server_dir, server_executable_name)
            installation_successful = os.path.exists(server_exe_check)
            
            if installation_successful:
                if status_callback:
                    status_callback("Server installed/updated successfully!")
                if progress_callback:
                    progress_callback(100)
                print("Server installed/updated.")
                return True
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
            upnp.discoverdelay = 200
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
            upnp.discoverdelay = 200
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
        Start a server executable
        
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
        
        cmd = [server_executable_path]
        if server_args:
            cmd.extend(server_args)
        
        print(f"Starting server: {' '.join(cmd)}")
        try:
            subprocess.Popen(cmd, cwd=working_directory)
            
            # Get public IP for information
            try:
                public_ip = requests.get('https://api.ipify.org', timeout=5).text
                print(f"Server started successfully. Public IP: {public_ip}")
            except Exception:
                print("Server started. Could not retrieve public IP.")
            
            return True
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    @staticmethod
    def get_server_paths(game_name: str) -> Tuple[str, str]:
        """
        Get standard server installation paths for a given game
        
        Args:
            game_name: Name of the game (e.g., 'palworld')
            
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
                s.connect(("8.8.8.8", 80))
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
    
    # Add more games here as needed
    # VALHEIM = {
    #     'app_id': '896660',
    #     'name': 'Valheim',
    #     'default_port': 2456,
    #     'executable_name': 'valheim_server.exe' if platform.system().lower() == 'windows' else 'valheim_server',
    #     'server_dir_name': 'Valheim Dedicated Server'
    # }
