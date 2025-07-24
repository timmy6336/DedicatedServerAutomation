import os
from utils.server_startup_script_utils import (
    SteamCMDUtils, 
    UPnPUtils, 
    ServerUtils, 
    GameConfig
)

# Palworld-specific configuration
PALWORLD_CONFIG = GameConfig.PALWORLD
SERVER_DIR, EXECUTABLE_NAME = ServerUtils.get_server_paths(PALWORLD_CONFIG['name'])
PALWORLD_APPID = PALWORLD_CONFIG['app_id']
PALWORLD_PORT = PALWORLD_CONFIG['default_port']


def download_steamcmd(progress_callback=None, status_callback=None):
    """Download SteamCMD with progress tracking - delegated to SteamCMDUtils"""
    return SteamCMDUtils.download_steamcmd(progress_callback, status_callback)


def install_or_update_palworld_server(progress_callback=None, status_callback=None):
    """Install or update Palworld server with progress tracking - delegated to SteamCMDUtils"""
    return SteamCMDUtils.install_or_update_server(
        app_id=PALWORLD_APPID,
        server_dir=SERVER_DIR,
        server_executable_name=EXECUTABLE_NAME,
        progress_callback=progress_callback,
        status_callback=status_callback
    )


def setup_upnp_port_forwarding():
    """Set up UPnP port forwarding for Palworld server - delegated to UPnPUtils"""
    return UPnPUtils.setup_port_forwarding(
        port=PALWORLD_PORT,
        description='Palworld Server'
    )


def start_palworld_server():
    """Start the Palworld dedicated server - delegated to ServerUtils"""
    server_executable_path = os.path.join(SERVER_DIR, EXECUTABLE_NAME)
    return ServerUtils.start_server(
        server_executable_path=server_executable_path,
        working_directory=SERVER_DIR
    )


def uninstall_steamcmd():
    """Remove SteamCMD if installed - delegated to SteamCMDUtils"""
    return SteamCMDUtils.uninstall_steamcmd()


def uninstall_palworld_server():
    """Remove Palworld Dedicated Server if installed - delegated to ServerUtils"""
    return ServerUtils.uninstall_server(SERVER_DIR)


def remove_port_forward_rule():
    """Remove UPnP port forwarding rule for Palworld - delegated to UPnPUtils"""
    return UPnPUtils.remove_port_forwarding(PALWORLD_PORT)


if __name__ == "__main__":
    # Example usage - these are commented out for safety
    # uninstall_palworld_server()
    # uninstall_steamcmd()
    pass

