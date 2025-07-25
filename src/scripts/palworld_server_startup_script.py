"""
Palworld Dedicated Server Management Script

This module provides a simplified interface for managing Palworld dedicated servers.
It acts as a thin wrapper around the shared utility functions, providing game-specific
configuration and maintaining backward compatibility with existing code.

The script delegates all complex operations to the server_startup_script_utils module,
which contains reusable functionality that can be shared across multiple games.

Features:
- SteamCMD installation and management
- Palworld server installation and updates with progress tracking
- UPnP port forwarding configuration
- Server startup and management
- Clean uninstallation with SteamCMD preservation

This refactored version maintains 100% backward compatibility while leveraging
the new utility system for better maintainability and multi-game support.
"""

# ================== PALWORLD SERVER CONSTANTS ==================
# Palworld server configuration constants
PALWORLD_DEFAULT_SERVER_PORT = 8211     # Default port for Palworld dedicated server

import os
from utils.server_startup_script_utils import (
    SteamCMDUtils, 
    UPnPUtils, 
    ServerUtils, 
    GameConfig
)

# Palworld-specific configuration loaded from shared GameConfig
PALWORLD_CONFIG = GameConfig.PALWORLD
SERVER_DIR, EXECUTABLE_NAME = ServerUtils.get_server_paths(PALWORLD_CONFIG['name'])
PALWORLD_APPID = PALWORLD_CONFIG['app_id']
PALWORLD_PORT = PALWORLD_CONFIG['default_port']


def download_steamcmd(progress_callback=None, status_callback=None):
    """
    Download and install SteamCMD with progress tracking.
    
    This function provides a Palworld-specific interface to the shared SteamCMD
    download functionality. It delegates to SteamCMDUtils while maintaining
    the same function signature for backward compatibility.
    
    Args:
        progress_callback (callable, optional): Function to call with progress 
            percentage (0-100). Called periodically during download and extraction.
        status_callback (callable, optional): Function to call with status 
            messages. Provides detailed information about current operations.
    
    Returns:
        bool: True if SteamCMD was successfully downloaded/verified, False otherwise
        
    Example:
        # Basic usage
        success = download_steamcmd()
        
        # With progress tracking
        def on_progress(percent):
            print(f"Progress: {percent}%")
            
        def on_status(message):
            print(f"Status: {message}")
            
        success = download_steamcmd(on_progress, on_status)
    """
    return SteamCMDUtils.download_steamcmd(progress_callback, status_callback)


def install_or_update_palworld_server(progress_callback=None, status_callback=None):
    """
    Install or update Palworld dedicated server with progress tracking.
    
    Downloads and installs the Palworld dedicated server files using SteamCMD.
    If the server is already installed, this function will verify and update
    the installation as needed. Provides detailed progress tracking and status
    updates throughout the process.
    
    Args:
        progress_callback (callable, optional): Function to call with progress 
            percentage (0-100). Called frequently during download and installation.
        status_callback (callable, optional): Function to call with status 
            messages. Provides real-time information about installation steps.
    
    Returns:
        bool: True if server was successfully installed/updated, False otherwise
        
    Note:
        Requires SteamCMD to be installed first. Will fail if SteamCMD is not
        available. The function performs file-based success verification rather
        than relying solely on SteamCMD exit codes for better reliability.
        
    Example:
        # Install with progress tracking
        def on_progress(percent):
            print(f"Installation progress: {percent}%")
            
        def on_status(message):
            print(f"Status: {message}")
            
        success = install_or_update_palworld_server(on_progress, on_status)
        if success:
            print("Palworld server ready!")
    """
    return SteamCMDUtils.install_or_update_server(
        app_id=PALWORLD_APPID,
        server_dir=SERVER_DIR,
        server_executable_name=EXECUTABLE_NAME,
        progress_callback=progress_callback,
        status_callback=status_callback
    )


def setup_upnp_port_forwarding():
    """
    Set up UPnP port forwarding for Palworld server.
    
    Attempts to automatically configure port forwarding on the local router
    using UPnP (Universal Plug and Play) protocol. This allows external players
    to connect to the server without manual router configuration.
    
    The function configures both TCP and UDP forwarding for the standard
    Palworld server port (default port) to ensure optimal connectivity.
    
    Returns:
        bool: True if port forwarding was successfully configured, False otherwise
        
    Note:
        UPnP must be enabled on the router for this to work. Some routers
        have UPnP disabled by default for security reasons. If this function
        fails, users will need to manually configure port forwarding.
        
    Example:
        success = setup_upnp_port_forwarding()
        if success:
            print("Port forwarding configured - external players can connect")
        else:
            print("Port forwarding failed - manual router config needed")
    """
    return UPnPUtils.setup_port_forwarding(
        port=PALWORLD_PORT,
        description='Palworld Server'
    )


def start_palworld_server():
    """
    Start the Palworld dedicated server.
    
    Launches the Palworld server executable in a separate process. The server
    will continue running independently after this function returns. Also
    attempts to retrieve and display the public IP address for easy sharing
    with other players.
    
    Returns:
        bool: True if server was successfully started, False otherwise
        
    Note:
        Requires the server files to be installed first. The server will run
        in the background and must be stopped through the operating system's
        process manager or by closing the server console window.
        
    Example:
        success = start_palworld_server()
        if success:
            print("Server is now running!")
        else:
            print("Failed to start server - check installation")
    """
    server_executable_path = os.path.join(SERVER_DIR, EXECUTABLE_NAME)
    return ServerUtils.start_server(
        server_executable_path=server_executable_path,
        working_directory=SERVER_DIR
    )


def uninstall_steamcmd():
    """
    Remove SteamCMD installation from the system.
    
    Completely removes the SteamCMD installation directory and all associated
    files. This will affect all games that use SteamCMD, not just Palworld.
    
    Returns:
        bool: True if SteamCMD was successfully removed, False otherwise
        
    Warning:
        This will remove SteamCMD for all games. If you have other Steam-based
        dedicated servers, they will need SteamCMD to be reinstalled. Consider
        using uninstall_palworld_server() instead to keep SteamCMD for other games.
        
    Example:
        success = uninstall_steamcmd()
        if success:
            print("SteamCMD completely removed")
    """
    return SteamCMDUtils.uninstall_steamcmd()


def uninstall_palworld_server():
    """
    Remove Palworld dedicated server installation.
    
    Removes all Palworld server files and directories. This preserves SteamCMD
    installation so it can be reused for other Steam-based games or for
    reinstalling Palworld in the future.
    
    Returns:
        bool: True if server files were successfully removed, False otherwise
        
    Note:
        This only removes Palworld-specific files. SteamCMD and other game
        servers are left untouched. This is the recommended way to uninstall
        if you might install other Steam-based servers in the future.
        
    Example:
        success = uninstall_palworld_server()
        if success:
            print("Palworld server removed (SteamCMD preserved)")
    """
    return ServerUtils.uninstall_server(SERVER_DIR)


def remove_port_forward_rule():
    """
    Remove UPnP port forwarding rule for Palworld server.
    
    Attempts to remove the automatic port forwarding rules that were created
    by setup_upnp_port_forwarding(). This closes the external access to the
    server by removing both TCP and UDP forwarding rules.
    
    Returns:
        bool: True if port forwarding rules were successfully removed, False otherwise
        
    Note:
        This only affects UPnP-configured rules. Manually configured port
        forwarding rules on the router will need to be removed manually through
        the router's administration interface.
        
    Example:
        success = remove_port_forward_rule()
        if success:
            print("Port forwarding removed - server no longer externally accessible")
    """
    return UPnPUtils.remove_port_forwarding(PALWORLD_PORT)


if __name__ == "__main__":
    """
    Script entry point for direct execution.
    
    When run directly, this script provides a safe way to test individual
    functions. The uninstall functions are commented out for safety to
    prevent accidental data loss during development and testing.
    
    Uncomment the desired function calls for testing, but be aware that
    uninstall operations will permanently remove files.
    """
    # Example usage - these are commented out for safety
    # uninstall_palworld_server()
    # uninstall_steamcmd()
    pass

