"""
Example template for creating server startup scripts for other games.
This demonstrates how to use the server_startup_script_utils for any Steam-based game server.
"""

import os
import sys

# Add utils directory to path to access our utility modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
utils_dir = os.path.join(parent_dir, 'utils')
if utils_dir not in sys.path:
    sys.path.insert(0, utils_dir)

from server_startup_script_utils import (
    SteamCMDUtils, 
    UPnPUtils, 
    ServerUtils, 
    GameConfig
)

# Example: Valheim Dedicated Server Configuration
# You would create a new configuration in GameConfig for each game
VALHEIM_CONFIG = {
    'app_id': '896660',
    'name': 'Valheim',
    'default_port': 2456,
    'executable_name': 'valheim_server.exe',  # Windows
    'server_dir_name': 'Valheim Dedicated Server'
}

# Get standard paths for this game
SERVER_DIR, EXECUTABLE_NAME = ServerUtils.get_server_paths(VALHEIM_CONFIG['name'])
GAME_APPID = VALHEIM_CONFIG['app_id']
GAME_PORT = VALHEIM_CONFIG['default_port']


def download_steamcmd(progress_callback=None, status_callback=None):
    """Download SteamCMD - uses the shared utility"""
    return SteamCMDUtils.download_steamcmd(progress_callback, status_callback)


def install_or_update_game_server(progress_callback=None, status_callback=None):
    """Install or update the game server - uses the shared utility"""
    return SteamCMDUtils.install_or_update_server(
        app_id=GAME_APPID,
        server_dir=SERVER_DIR,
        server_executable_name=EXECUTABLE_NAME,
        progress_callback=progress_callback,
        status_callback=status_callback
    )


def setup_upnp_port_forwarding():
    """Set up UPnP port forwarding for the game server - uses the shared utility"""
    return UPnPUtils.setup_port_forwarding(
        port=GAME_PORT,
        description=f'{VALHEIM_CONFIG["name"]} Server'
    )


def start_game_server():
    """Start the game dedicated server - uses the shared utility"""
    server_executable_path = os.path.join(SERVER_DIR, EXECUTABLE_NAME)
    
    # Example: Some games might need special arguments
    server_args = []  # Add any game-specific arguments here
    
    return ServerUtils.start_server(
        server_executable_path=server_executable_path,
        working_directory=SERVER_DIR,
        server_args=server_args
    )


def uninstall_steamcmd():
    """Remove SteamCMD - uses the shared utility"""
    return SteamCMDUtils.uninstall_steamcmd()


def uninstall_game_server():
    """Remove the game server installation - uses the shared utility"""
    return ServerUtils.uninstall_server(SERVER_DIR)


def remove_port_forward_rule():
    """Remove UPnP port forwarding rule - uses the shared utility"""
    return UPnPUtils.remove_port_forwarding(GAME_PORT)


# Game-specific functions (if needed)
def configure_game_server():
    """
    Example function for game-specific configuration.
    Some games might need special configuration files, settings, etc.
    """
    # Example: Create/modify configuration files
    config_file_path = os.path.join(SERVER_DIR, 'server_config.ini')
    
    # This is where you'd add game-specific configuration logic
    print(f"Configuring {VALHEIM_CONFIG['name']} server...")
    
    # Example configuration (this would be game-specific)
    config_content = f"""
# {VALHEIM_CONFIG['name']} Server Configuration
server_name=My Dedicated Server
server_port={GAME_PORT}
world_name=MyWorld
password=mypassword
"""
    
    try:
        with open(config_file_path, 'w') as f:
            f.write(config_content)
        print(f"Configuration written to {config_file_path}")
        return True
    except Exception as e:
        print(f"Failed to write configuration: {e}")
        return False


def get_server_status():
    """
    Example function to check if the game server is running.
    This would need to be implemented per game.
    """
    # This is where you'd add game-specific process detection
    # You could extend the ServerUtils or NetworkUtils for this
    print(f"Checking {VALHEIM_CONFIG['name']} server status...")
    
    # Example: Check if the executable is running
    server_exe_path = os.path.join(SERVER_DIR, EXECUTABLE_NAME)
    if not os.path.exists(server_exe_path):
        return {"status": "not_installed", "running": False}
    
    # You could add process detection here using psutil or similar
    # For now, just check if files exist
    return {"status": "installed", "running": False}  # Placeholder


if __name__ == "__main__":
    # Example usage workflow
    print(f"Setting up {VALHEIM_CONFIG['name']} Dedicated Server")
    
    # Step 1: Download SteamCMD
    if download_steamcmd():
        print("✅ SteamCMD ready")
    
    # Step 2: Install the game server
    if install_or_update_game_server():
        print("✅ Game server installed")
    
    # Step 3: Configure the server (game-specific)
    if configure_game_server():
        print("✅ Server configured")
    
    # Step 4: Set up port forwarding
    if setup_upnp_port_forwarding():
        print("✅ Port forwarding configured")
    
    # Step 5: Start the server
    if start_game_server():
        print("✅ Server started")
    
    print("Setup complete!")
