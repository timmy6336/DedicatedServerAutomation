"""
Valheim Dedicated Server Management Script

This module provides a simplified interface for managing Valheim dedicated servers.
It acts as a thin wrapper around the shared utility functions, providing game-specific
configuration and maintaining backward compatibility with existing code.

The script delegates all complex operations to the server_startup_script_utils module,
which contains reusable functionality that can be shared across multiple games.

Features:
- SteamCMD installation and management
- Valheim server installation and updates with progress tracking
- UPnP port forwarding configuration
- Server startup and management
- Clean uninstallation with SteamCMD preservation
- Valheim-specific world and save management

This implementation demonstrates the power of the modular utility system by
reusing 100% of the core functionality while providing Valheim-specific configuration.
"""

import os
from utils.server_startup_script_utils import (
    SteamCMDUtils, 
    UPnPUtils, 
    ServerUtils, 
    GameConfig
)

# Valheim-specific configuration loaded from shared GameConfig
VALHEIM_CONFIG = GameConfig.VALHEIM
SERVER_DIR, EXECUTABLE_NAME = ServerUtils.get_server_paths(VALHEIM_CONFIG['name'])
VALHEIM_APPID = VALHEIM_CONFIG['app_id']
VALHEIM_PORT = VALHEIM_CONFIG['default_port']


def download_steamcmd(progress_callback=None, status_callback=None):
    """
    Download and install SteamCMD with progress tracking.
    
    This function provides a Valheim-specific interface to the shared SteamCMD
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


def install_or_update_valheim_server(progress_callback=None, status_callback=None):
    """
    Install or update Valheim dedicated server with progress tracking.
    
    Downloads and installs the Valheim dedicated server files using SteamCMD.
    If the server is already installed, this function will verify and update
    the installation as needed. Provides detailed progress tracking and status
    updates throughout the process.
    
    The Valheim server is relatively lightweight compared to other games and
    typically installs quickly. The server supports up to 10 players by default
    and includes built-in world persistence and backup capabilities.
    
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
        
        Valheim servers require approximately 2GB of disk space and 4GB of RAM
        for optimal performance with a full 10-player server.
        
    Example:
        # Install with progress tracking
        def on_progress(percent):
            print(f"Installation progress: {percent}%")
            
        def on_status(message):
            print(f"Status: {message}")
            
        success = install_or_update_valheim_server(on_progress, on_status)
        if success:
            print("Valheim server ready for Viking adventures!")
    """
    return SteamCMDUtils.install_or_update_server(
        app_id=VALHEIM_APPID,
        server_dir=SERVER_DIR,
        server_executable_name=EXECUTABLE_NAME,
        progress_callback=progress_callback,
        status_callback=status_callback
    )


def setup_upnp_port_forwarding():
    """
    Set up UPnP port forwarding for Valheim server.
    
    Attempts to automatically configure port forwarding on the local router
    using UPnP (Universal Plug and Play) protocol. This allows external players
    to connect to the server without manual router configuration.
    
    Valheim uses UDP port 2456 by default for game traffic, plus additional
    ports (2457, 2458) for Steam query and other features. This function
    configures the primary game port for external connectivity.
    
    Returns:
        bool: True if port forwarding was successfully configured, False otherwise
        
    Note:
        UPnP must be enabled on the router for this to work. Some routers
        have UPnP disabled by default for security reasons. If this function
        fails, users will need to manually configure port forwarding for:
        - UDP 2456 (primary game port)
        - UDP 2457 (Steam query port)
        - UDP 2458 (additional features)
        
    Example:
        success = setup_upnp_port_forwarding()
        if success:
            print("Port forwarding configured - Vikings can join from anywhere!")
        else:
            print("Port forwarding failed - manual router config needed")
    """
    return UPnPUtils.setup_port_forwarding(
        port=VALHEIM_PORT,
        description='Valheim Server'
    )


def start_valheim_server(world_name="DedicatedWorld", server_name="Valheim Server", 
                        password="valheim123", public_server=True, port=2456):
    """
    Start the Valheim dedicated server with proper configuration.
    
    Launches the Valheim server executable with all required command line arguments
    for dedicated server operation. The server will run in headless mode without
    graphics rendering, suitable for server environments.
    
    Args:
        world_name (str): Name of the world to create/load (default: "DedicatedWorld")
        server_name (str): Display name for the server (default: "Valheim Server")
        password (str): Server password - must be at least 5 characters (default: "valheim123")
        public_server (bool): Whether server appears in public server list (default: True)
        port (int): Server port number (default: 2456)
    
    Returns:
        bool: True if server was successfully started, False otherwise
        
    Note:
        Requires the server files to be installed first. The server will run
        in the background and must be stopped through the operating system's
        process manager or by closing the server console window.
        
        Valheim servers automatically save world data periodically and create
        backup files to prevent data loss. World files are stored in the
        server directory and can be backed up manually if desired.
        
    Example:
        success = start_valheim_server(
            world_name="MyWorld",
            server_name="My Viking Server", 
            password="strongpassword123"
        )
        if success:
            print("Valheim server is now running!")
            print(f"World: '{world_name}'")
            print("Players can connect and start their Viking adventure!")
        else:
            print("Failed to start server - check installation")
    """
    # Validate password length (Valheim requires at least 5 characters)
    if len(password) < 5:
        print("Error: Server password must be at least 5 characters long")
        return False
    
    server_executable_path = os.path.join(SERVER_DIR, EXECUTABLE_NAME)
    
    # Valheim dedicated server command line arguments
    server_args = [
        "-nographics",          # Run without graphics (headless mode)
        "-batchmode",           # Run in batch mode (no UI)
        "-port", str(port),     # Server port
        "-world", world_name,   # World name
        "-name", server_name,   # Server display name
        "-password", password,  # Server password
        "-savedir", SERVER_DIR  # Save directory for world files
    ]
    
    # Add public server flag if enabled
    if public_server:
        server_args.append("-public")
        server_args.append("1")
    else:
        server_args.append("-public")
        server_args.append("0")
    
    print(f"Starting Valheim server with configuration:")
    print(f"  World Name: {world_name}")
    print(f"  Server Name: {server_name}")
    print(f"  Port: {port}")
    print(f"  Public Server: {public_server}")
    print(f"  Password Protected: Yes")
    
    return ServerUtils.start_server(
        server_executable_path=server_executable_path,
        working_directory=SERVER_DIR,
        server_args=server_args
    )


def uninstall_steamcmd():
    """
    Remove SteamCMD installation from the system.
    
    Completely removes the SteamCMD installation directory and all associated
    files. This will affect all games that use SteamCMD, not just Valheim.
    
    Returns:
        bool: True if SteamCMD was successfully removed, False otherwise
        
    Warning:
        This will remove SteamCMD for all games. If you have other Steam-based
        dedicated servers (like Palworld), they will need SteamCMD to be 
        reinstalled. Consider using uninstall_valheim_server() instead to 
        keep SteamCMD for other games.
        
    Example:
        success = uninstall_steamcmd()
        if success:
            print("SteamCMD completely removed")
    """
    return SteamCMDUtils.uninstall_steamcmd()


def uninstall_valheim_server():
    """
    Remove Valheim dedicated server installation.
    
    Removes all Valheim server files and directories. This preserves SteamCMD
    installation so it can be reused for other Steam-based games or for
    reinstalling Valheim in the future.
    
    Returns:
        bool: True if server files were successfully removed, False otherwise
        
    Note:
        This only removes Valheim-specific files. SteamCMD and other game
        servers are left untouched. This is the recommended way to uninstall
        if you might install other Steam-based servers in the future.
        
        World save data and character progression will be permanently lost
        unless backed up separately. Consider backing up the worlds folder
        before uninstalling if you want to preserve game progress.
        
    Example:
        success = uninstall_valheim_server()
        if success:
            print("Valheim server removed (SteamCMD preserved)")
            print("World data has been deleted - backup if needed!")
    """
    return ServerUtils.uninstall_server(SERVER_DIR)


def remove_port_forward_rule():
    """
    Remove UPnP port forwarding rule for Valheim server.
    
    Attempts to remove the automatic port forwarding rules that were created
    by setup_upnp_port_forwarding(). This closes the external access to the
    server by removing the UDP port forwarding rule for port 2456.
    
    Returns:
        bool: True if port forwarding rules were successfully removed, False otherwise
        
    Note:
        This only affects UPnP-configured rules. Manually configured port
        forwarding rules on the router will need to be removed manually through
        the router's administration interface.
        
        After removing port forwarding, only players on the local network
        will be able to connect to the server.
        
    Example:
        success = remove_port_forward_rule()
        if success:
            print("Port forwarding removed - server now local-only")
        else:
            print("Could not remove port forwarding - check router manually")
    """
    return UPnPUtils.remove_port_forwarding(VALHEIM_PORT)


def get_valheim_world_info():
    """
    Get information about available Valheim worlds on the server.
    
    Scans the server directory for existing world files and returns
    information about available worlds. This can be useful for server
    management and world backup operations.
    
    Returns:
        dict: Dictionary containing world information, or empty dict if no worlds found
        
    Note:
        Valheim world files are stored in specific subdirectories and have
        particular naming conventions. This function helps identify and
        manage these world files for backup and administration purposes.
        
    Example:
        worlds = get_valheim_world_info()
        if worlds:
            print(f"Found {len(worlds)} world(s):")
            for world_name, info in worlds.items():
                print(f"  - {world_name}: {info['size']} MB")
        else:
            print("No worlds found - server will create default world on first run")
    """
    worlds = {}
    
    if not os.path.exists(SERVER_DIR):
        return worlds
    
    # Look for Valheim world directories (worlds are stored in subdirectories)
    for item in os.listdir(SERVER_DIR):
        item_path = os.path.join(SERVER_DIR, item)
        if os.path.isdir(item_path):
            # Check if this looks like a world directory
            world_files = [f for f in os.listdir(item_path) if f.endswith('.db') or f.endswith('.fwl')]
            if world_files:
                # Calculate total size of world files
                total_size = 0
                for world_file in world_files:
                    file_path = os.path.join(item_path, world_file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
                
                worlds[item] = {
                    'path': item_path,
                    'files': world_files,
                    'size_bytes': total_size,
                    'size': f"{total_size / (1024*1024):.2f}"  # Size in MB
                }
    
    return worlds


def start_valheim_server_interactive():
    """
    Start Valheim server with interactive configuration prompts.
    
    This function provides a user-friendly way to configure and start a Valheim
    server by prompting for custom settings. It validates user input and provides
    helpful defaults and guidance.
    
    Returns:
        bool: True if server was successfully started, False otherwise
        
    Example:
        success = start_valheim_server_interactive()
        if success:
            print("Your customized Valheim server is now running!")
    """
    print("=" * 60)
    print("           VALHEIM DEDICATED SERVER SETUP")
    print("=" * 60)
    print()
    
    # Get world name
    world_name = input("Enter world name (default: DedicatedWorld): ").strip()
    if not world_name:
        world_name = "DedicatedWorld"
    
    # Get server display name
    server_name = input("Enter server display name (default: Valheim Server): ").strip()
    if not server_name:
        server_name = "Valheim Server"
    
    # Get password with validation
    while True:
        password = input("Enter server password (minimum 5 characters): ").strip()
        if len(password) >= 5:
            break
        print("❌ Password must be at least 5 characters long. Please try again.")
    
    # Get port
    while True:
        port_input = input("Enter server port (default: 2456): ").strip()
        if not port_input:
            port = 2456
            break
        try:
            port = int(port_input)
            if 1024 <= port <= 65535:
                break
            else:
                print("❌ Port must be between 1024 and 65535. Please try again.")
        except ValueError:
            print("❌ Invalid port number. Please enter a number.")
    
    # Get public server setting
    while True:
        public_input = input("Make server public? (y/n, default: y): ").strip().lower()
        if not public_input or public_input in ['y', 'yes']:
            public_server = True
            break
        elif public_input in ['n', 'no']:
            public_server = False
            break
        else:
            print("❌ Please enter 'y' for yes or 'n' for no.")
    
    print()
    print("Configuration Summary:")
    print(f"  World Name: {world_name}")
    print(f"  Server Name: {server_name}")
    print(f"  Port: {port}")
    print(f"  Public Server: {'Yes' if public_server else 'No'}")
    print(f"  Password Protected: Yes")
    print()
    
    confirm = input("Start server with these settings? (y/n): ").strip().lower()
    if confirm in ['y', 'yes']:
        return start_valheim_server(world_name, server_name, password, public_server, port)
    else:
        print("Server startup cancelled.")
        return False


def configure_valheim_firewall(port=2456):
    """
    Configure Windows Firewall rules for Valheim server.
    
    Creates firewall rules to allow Valheim server traffic through Windows Firewall
    for the specified port range (port, port+1, port+2). This ensures that the
    server can receive connections from external players.
    
    Args:
        port (int): Base port number for Valheim server (default: 2456)
    
    Returns:
        bool: True if firewall rules were successfully created, False otherwise
    
    Note:
        This function requires administrator privileges to modify firewall rules.
        On Windows systems, it uses netsh commands to configure the firewall.
        
        Valheim uses three consecutive UDP ports:
        - port: Main game traffic
        - port+1: Steam query
        - port+2: Additional features
    
    Example:
        success = configure_valheim_firewall(2456)
        if success:
            print("Firewall configured for Valheim server")
        else:
            print("Failed to configure firewall - check admin privileges")
    """
    import subprocess
    import platform
    
    if platform.system().lower() != 'windows':
        print("Firewall configuration only supported on Windows")
        return False
    
    try:
        # Define the ports to configure
        ports = [port, port + 1, port + 2]
        
        for i, p in enumerate(ports):
            port_names = ["Game", "Query", "Additional"]
            rule_name = f"Valheim Server {port_names[i]} Port {p}"
            
            # Create inbound rule
            cmd_in = [
                "netsh", "advfirewall", "firewall", "add", "rule",
                f'name="{rule_name} (Inbound)"',
                "dir=in",
                "action=allow",
                "protocol=UDP",
                f"localport={p}",
                "profile=any"
            ]
            
            # Create outbound rule
            cmd_out = [
                "netsh", "advfirewall", "firewall", "add", "rule",
                f'name="{rule_name} (Outbound)"',
                "dir=out",
                "action=allow",
                "protocol=UDP",
                f"localport={p}",
                "profile=any"
            ]
            
            # Execute commands
            result_in = subprocess.run(cmd_in, capture_output=True, text=True)
            result_out = subprocess.run(cmd_out, capture_output=True, text=True)
            
            if result_in.returncode != 0 or result_out.returncode != 0:
                print(f"Warning: Failed to create firewall rule for port {p}")
                # Don't return False here, continue with other ports
        
        print(f"Firewall rules created for Valheim server ports {port}-{port+2}")
        return True
        
    except Exception as e:
        print(f"Error configuring firewall: {e}")
        return False


def create_valheim_server_config(config):
    """
    Create Valheim server configuration files.
    
    Creates or updates server configuration files based on the provided configuration.
    This includes creating batch files for easy server startup and any necessary
    configuration files for the Valheim server.
    
    Args:
        config (dict): Server configuration dictionary containing:
            - world_name: Name of the world
            - server_name: Display name of the server
            - password: Server password
            - port: Server port
            - public_server: Whether server is public
    
    Returns:
        bool: True if configuration files were successfully created, False otherwise
    
    Example:
        config = {
            'world_name': 'MyWorld',
            'server_name': 'My Server',
            'password': 'mypassword',
            'port': 2456,
            'public_server': True
        }
        success = create_valheim_server_config(config)
    """
    try:
        # Create a custom startup batch file
        batch_content = f'''@echo off
title {config['server_name']}
echo ================================================================
echo                    {config['server_name'].upper()}
echo ================================================================
echo.
echo Server Configuration:
echo   World Name: {config['world_name']}
echo   Server Name: {config['server_name']}
echo   Port: {config['port']}
echo   Public Server: {"Yes" if config['public_server'] else "No"}
echo   Password Protected: Yes
echo.

REM Navigate to server directory
cd /d "{SERVER_DIR}"

echo Starting Valheim dedicated server...
echo ================================================================

REM Start server with configuration
valheim_server.exe -nographics -batchmode -port {config['port']} -world "{config['world_name']}" -name "{config['server_name']}" -password "{config['password']}" -public {"1" if config['public_server'] else "0"} -savedir "{SERVER_DIR}"

echo.
echo ================================================================
echo Server has stopped.
echo ================================================================
pause
'''
        
        # Write the batch file
        batch_path = os.path.join(SERVER_DIR, "start_server_custom.bat")
        with open(batch_path, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print(f"Created custom startup script: {batch_path}")
        
        # Create a configuration info file
        config_info = f'''Valheim Server Configuration
============================
Generated: {os.path.basename(__file__)} on {os.path.basename(os.getcwd())}

World Name: {config['world_name']}
Server Name: {config['server_name']}
Port: {config['port']}
Additional Ports: {config['port']+1}, {config['port']+2}
Public Server: {"Yes" if config['public_server'] else "No"}
Password Protected: Yes

Connection Information:
- Players can connect by searching for "{config['server_name']}" in the server list
- Or by using IP:Port connection: <YOUR_IP>:{config['port']}
- Password is required to join

Files:
- World saves: Located in server directory
- Custom startup: start_server_custom.bat
- Default startup: valheim_server.exe

Network:
- Required ports (UDP): {config['port']}, {config['port']+1}, {config['port']+2}
- Firewall: Ensure Windows Firewall allows these ports
- Router: Port forwarding may be required for external access

For manual server management, use the start_server_custom.bat file
or run valheim_server.exe with the appropriate command line arguments.
'''
        
        config_path = os.path.join(SERVER_DIR, "server_config_info.txt")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_info)
        
        print(f"Created configuration info: {config_path}")
        return True
        
    except Exception as e:
        print(f"Error creating configuration files: {e}")
        return False


def setup_upnp_port_forwarding(port=2456):
    """
    Set up UPnP port forwarding for Valheim server with custom port.
    
    Enhanced version of the UPnP setup function that supports custom port configuration.
    Configures port forwarding for the specified port and the two additional ports
    that Valheim requires (port+1 and port+2).
    
    Args:
        port (int): Base port number for Valheim server (default: 2456)
    
    Returns:
        bool: True if port forwarding was successfully configured, False otherwise
    
    Note:
        This function configures three consecutive UDP ports for full Valheim
        server functionality. UPnP must be enabled on the router.
    
    Example:
        success = setup_upnp_port_forwarding(2456)
        if success:
            print("UPnP configured for ports 2456-2458")
    """
    try:
        # Configure the main port and two additional ports
        success_count = 0
        ports = [port, port + 1, port + 2]
        descriptions = ["Valheim Game", "Valheim Query", "Valheim Additional"]
        
        for i, p in enumerate(ports):
            result = UPnPUtils.setup_port_forwarding(
                port=p,
                description=descriptions[i]
            )
            if result:
                success_count += 1
                print(f"UPnP configured for port {p} ({descriptions[i]})")
            else:
                print(f"Warning: UPnP failed for port {p}")
        
        # Return True if at least the main port was configured
        return success_count > 0
        
    except Exception as e:
        print(f"Error configuring UPnP: {e}")
        return False


if __name__ == "__main__":
    """
    Script entry point for direct execution.
    
    When run directly, this script provides a safe way to test individual
    functions. The uninstall functions are commented out for safety to
    prevent accidental data loss during development and testing.
    
    Uncomment the desired function calls for testing, but be aware that
    uninstall operations will permanently remove files including world data.
    """
    # Example usage - these are commented out for safety
    # print("Valheim Server Management Script")
    # print("Available worlds:", get_valheim_world_info())
    # uninstall_valheim_server()
    # uninstall_steamcmd()
    pass
