"""
Rust Dedicated Server Management Script

This module provides a comprehensive interface for managing Rust dedicated servers.
It leverages the shared utility functions while providing Rust-specific configuration
and maintaining compatibility with the existing application architecture.

The script handles all aspects of Rust server management including:
- SteamCMD installation and management
- Rust server installation and updates with progress tracking
- UPnP port forwarding configuration for multiple ports
- Server startup with extensive configuration options
- Clean uninstallation with data preservation options
- Rust-specific world generation and save management

Features:
- Support for up to 300 concurrent players
- Procedural world generation with configurable size and seed
- Oxide/uMod plugin framework integration
- Comprehensive server configuration options
- Performance optimization settings
- Administrative tools and commands
"""

# ================== RUST SERVER CONSTANTS ==================
# Rust server networking and port configuration
RUST_DEFAULT_PORT = 28015                # Primary game port for Rust server
RUST_QUERY_PORT = 28016                  # Steam query port for server browser
RUST_RCON_PORT = 28016                   # RCON port (same as query for Rust)
RUST_APP_PORT = 28082                    # Rust+ companion app port

# Player and server limits
RUST_MAX_PLAYERS_DEFAULT = 100           # Default maximum players for Rust server
RUST_MAX_PLAYERS_LIMIT = 300             # Maximum players supported by Rust
RUST_MIN_PLAYERS = 1                     # Minimum players (for private servers)

# World generation constants
RUST_DEFAULT_WORLD_SIZE = 3000           # Default world size for map generation
RUST_MIN_WORLD_SIZE = 1000               # Minimum world size
RUST_MAX_WORLD_SIZE = 4000               # Maximum world size
RUST_DEFAULT_SEED = 12345                # Default world generation seed
RUST_MAX_SEED = 2147483647               # Maximum seed value (32-bit signed int)

# Steam configuration
RUST_STEAM_APP_ID = "258550"             # SteamCMD App ID for Rust Dedicated Server

# Server performance and timing
RUST_DEFAULT_SAVE_INTERVAL = 600         # Default auto-save interval in seconds
RUST_MIN_SAVE_INTERVAL = 60              # Minimum save interval
RUST_MAX_SAVE_INTERVAL = 3600            # Maximum save interval (1 hour)
RUST_DEFAULT_TICKRATE = 30               # Default server tick rate

# File and directory constants
RUST_EXECUTABLE_NAME = "RustDedicated.exe"  # Rust server executable name
RUST_CONFIG_FILE = "server.cfg"             # Main server configuration file
RUST_USERS_FILE = "users.cfg"               # User permissions file
RUST_BANS_FILE = "bans.cfg"                 # Banned users file

# Default values and fallbacks
DEFAULT_SERVER_NAME = "My Rust Server"      # Default server display name
DEFAULT_SERVER_DESCRIPTION = "A Rust Server"  # Default server description
DEFAULT_SERVER_URL = ""                     # Default server website URL
DEFAULT_SERVER_BANNER_URL = ""              # Default server banner image URL

# Display formatting
SEPARATOR_LINE_LENGTH = 60               # Length of separator lines for output formatting
CONFIRMATION_SEPARATOR_LENGTH = 50       # Length of separator lines for confirmation prompts

import os
import sys
from pathlib import Path

# Import shared utilities from the parent utils directory
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
utils_dir = parent_dir / "utils"
sys.path.insert(0, str(utils_dir))

from utils.server_startup_script_utils import (
    SteamCMDUtils, UPnPUtils, ServerUtils, GameConfig
)

# Rust-specific game configuration
RUST_CONFIG = GameConfig.RUST

# Extract values for easier access
RUST_APPID = RUST_CONFIG['app_id']
RUST_PORT = RUST_CONFIG['default_port']
SERVER_DIR, EXECUTABLE_NAME = ServerUtils.get_server_paths(RUST_CONFIG['name'])

def download_steamcmd(progress_callback=None, status_callback=None):
    """
    Download and install SteamCMD with progress tracking.
    
    This function provides a Rust-specific interface to the shared SteamCMD
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

def install_or_update_rust_server(progress_callback=None, status_callback=None):
    """
    Install or update the Rust dedicated server using SteamCMD.
    
    Downloads the latest Rust dedicated server files from Steam. This function
    handles both initial installation and updates to existing installations.
    Rust servers require significant disk space and download time.
    
    Args:
        progress_callback (callable, optional): Function to call with installation 
            progress percentage (0-100). Updates provided during download phases.
        status_callback (callable, optional): Function to call with detailed 
            status messages about the installation process.
    
    Returns:
        bool: True if server was successfully installed/updated, False otherwise
        
    Note:
        Rust server files are approximately 2-3 GB and may take significant time
        to download depending on internet connection speed. The server supports
        incremental updates, so subsequent updates are typically much smaller.
        
    Example:
        # Install with progress tracking
        def on_progress(percent):
            print(f"Installation progress: {percent}%")
            
        def on_status(message):
            print(f"Status: {message}")
            
        success = install_or_update_rust_server(on_progress, on_status)
        if success:
            print("Rust server ready!")
        else:
            print("Installation failed")
    """
    return SteamCMDUtils.install_or_update_server(
        app_id=RUST_APPID,
        server_dir=SERVER_DIR,
        server_executable_name=EXECUTABLE_NAME,
        progress_callback=progress_callback,
        status_callback=status_callback
    )

def setup_upnp_port_forwarding(port=RUST_DEFAULT_PORT):
    """
    Configure UPnP port forwarding for Rust server ports.
    
    Rust requires multiple ports to be forwarded for full functionality:
    - Main game port (default 28015, UDP)
    - Query port (28016, UDP) for server browser visibility
    - RCON port (28016, TCP) for remote administration
    - Rust+ app port (28082, TCP) for companion app
    
    Args:
        port (int): Base port number for the server (default: 28015)
    
    Returns:
        bool: True if port forwarding was successfully configured, False otherwise
        
    Note:
        This function attempts to configure all necessary ports automatically.
        If UPnP is not supported by your router, manual port forwarding will
        be required. The function will attempt to remove existing rules before
        adding new ones to avoid conflicts.
        
    Example:
        # Use default port
        success = setup_upnp_port_forwarding()
        
        # Use custom port
        success = setup_upnp_port_forwarding(28115)
        if success:
            print("Rust server ports forwarded successfully!")
    """
    # Rust uses multiple ports that need forwarding
    ports_to_forward = [
        (port, 'UDP'),              # Main game port
        (port + 1, 'UDP'),          # Query port
        (port + 1, 'TCP'),          # RCON port (same number, different protocol)
        (28082, 'TCP')              # Rust+ app port (fixed)
    ]
    
    return UPnPUtils.setup_port_forwarding(
        ports=ports_to_forward,
        description='Rust Server'
    )

def start_rust_server(server_name=DEFAULT_SERVER_NAME, max_players=RUST_MAX_PLAYERS_DEFAULT,
                     world_size=RUST_DEFAULT_WORLD_SIZE, seed=RUST_DEFAULT_SEED,
                     port=RUST_DEFAULT_PORT, save_interval=RUST_DEFAULT_SAVE_INTERVAL,
                     tickrate=RUST_DEFAULT_TICKRATE, pve_mode=False, secure=True):
    """
    Start the Rust dedicated server with comprehensive configuration.
    
    Launches the Rust server executable with all required command line arguments
    for dedicated server operation. The server will run in headless mode without
    graphics rendering, suitable for server environments.
    
    Args:
        server_name (str): Display name for the server in browser
        max_players (int): Maximum number of concurrent players (1-300)
        world_size (int): Size of the generated world (1000-4000)
        seed (int): World generation seed for consistent map generation
        port (int): Server port number (default: 28015)
        save_interval (int): Auto-save interval in seconds (60-3600)
        tickrate (int): Server tick rate (20, 30, or 60)
        pve_mode (bool): Enable PvE mode (no player vs player damage)
        secure (bool): Enable VAC (Valve Anti-Cheat) protection
    
    Returns:
        bool: True if server was successfully started, False otherwise
        
    Note:
        Rust servers require significant system resources, especially RAM and CPU.
        Recommended minimum: 8GB RAM, 4-core CPU for 100 players. World size
        affects memory usage and generation time. Larger worlds require more resources.
        
    Example:
        success = start_rust_server(
            server_name="My Survival Server",
            max_players=150,
            world_size=3500,
            seed=98765,
            pve_mode=False
        )
        if success:
            print("Rust server is now running!")
            print(f"Server: '{server_name}' with {max_players} player slots")
            print(f"World size: {world_size}, Seed: {seed}")
        else:
            print("Failed to start server - check configuration")
    """
    # Validate parameters
    max_players = max(RUST_MIN_PLAYERS, min(max_players, RUST_MAX_PLAYERS_LIMIT))
    world_size = max(RUST_MIN_WORLD_SIZE, min(world_size, RUST_MAX_WORLD_SIZE))
    seed = max(1, min(seed, RUST_MAX_SEED))
    save_interval = max(RUST_MIN_SAVE_INTERVAL, min(save_interval, RUST_MAX_SAVE_INTERVAL))
    
    server_executable_path = os.path.join(SERVER_DIR, EXECUTABLE_NAME)
    
    # Rust dedicated server command line arguments
    server_args = [
        "-batchmode",                    # Run in batch mode (no UI)
        "-nographics",                   # Run without graphics (headless mode)
        f"+server.hostname", f'"{server_name}"',  # Server name in quotes
        f"+server.maxplayers", str(max_players),  # Maximum players
        f"+server.worldsize", str(world_size),    # World generation size
        f"+server.seed", str(seed),               # World generation seed
        f"+server.port", str(port),               # Server port
        f"+server.saveinterval", str(save_interval),  # Auto-save interval
        f"+fps.limit", str(tickrate),             # Server tick rate
        "+server.identity", "rust_server",        # Server identity folder
    ]
    
    # Add PvE mode if enabled
    if pve_mode:
        server_args.extend(["+server.pve", "true"])
    
    # Add VAC security if enabled
    if secure:
        server_args.extend(["+server.secure", "true"])
    else:
        server_args.extend(["+server.secure", "false"])
    
    print(f"Starting Rust server with configuration:")
    print(f"  Server Name: {server_name}")
    print(f"  Max Players: {max_players}")
    print(f"  World Size: {world_size}")
    print(f"  Seed: {seed}")
    print(f"  Port: {port}")
    print(f"  PvE Mode: {pve_mode}")
    print(f"  VAC Secure: {secure}")
    print(f"  Save Interval: {save_interval} seconds")
    print(f"  Tick Rate: {tickrate} FPS")
    
    return ServerUtils.start_server(
        server_executable_path=server_executable_path,
        working_directory=SERVER_DIR,
        server_args=server_args
    )

def uninstall_steamcmd():
    """
    Uninstall SteamCMD from the system.
    
    Removes the SteamCMD installation directory and all associated files.
    This is a shared utility function that affects all games using SteamCMD.
    
    Returns:
        bool: True if SteamCMD was successfully uninstalled, False otherwise
        
    Warning:
        This will affect all games that use SteamCMD for server management.
        Only uninstall SteamCMD if you're removing all server installations.
    """
    return SteamCMDUtils.uninstall_steamcmd()

def uninstall_rust_server():
    """
    Uninstall the Rust dedicated server.
    
    Removes the Rust server installation directory and all server files.
    This includes world data, player data, configuration files, and plugins.
    
    Returns:
        bool: True if server was successfully uninstalled, False otherwise
        
    Warning:
        This will permanently delete all world data, player progress, and
        server configurations. Ensure you have backups of important data
        before uninstalling.
        
    Note:
        This function preserves SteamCMD installation for other games.
        Only the Rust-specific server files are removed.
    """
    return ServerUtils.uninstall_server(SERVER_DIR)

def is_rust_server_installed():
    """
    Check if Rust dedicated server is installed.
    
    Verifies the presence of the main Rust server executable and essential
    files required for server operation.
    
    Returns:
        bool: True if Rust server is properly installed, False otherwise
        
    Note:
        This function checks for the existence of key files but does not
        validate the integrity of the installation. Use SteamCMD validation
        if you suspect file corruption.
    """
    server_executable_path = os.path.join(SERVER_DIR, EXECUTABLE_NAME)
    return os.path.exists(server_executable_path)

def remove_port_forward_rule(port=RUST_DEFAULT_PORT):
    """
    Remove UPnP port forwarding rules for Rust server.
    
    Removes all port forwarding rules that were created for the Rust server.
    This includes the main game port, query port, RCON port, and app port.
    
    Args:
        port (int): Base port number that was used for port forwarding
    
    Returns:
        bool: True if port forwarding rules were successfully removed, False otherwise
        
    Note:
        This function attempts to remove all Rust-related port forwarding rules.
        Some routers may require manual removal of port forwarding rules.
    """
    # Remove all Rust-related ports
    ports_to_remove = [
        (port, 'UDP'),              # Main game port
        (port + 1, 'UDP'),          # Query port
        (port + 1, 'TCP'),          # RCON port
        (28082, 'TCP')              # Rust+ app port
    ]
    
    return UPnPUtils.remove_port_forwarding(ports_to_remove)

def get_rust_world_info():
    """
    Get information about the current Rust world.
    
    Retrieves details about the currently generated or saved world including
    size, seed, and save location. This information is useful for backup
    and server management purposes.
    
    Returns:
        dict: Dictionary containing world information, or None if no world exists
        
    Note:
        Rust worlds are procedurally generated based on size and seed.
        The same size and seed will always generate the same world layout.
    """
    world_info = {
        'server_identity': 'rust_server',
        'save_directory': os.path.join(SERVER_DIR, 'server', 'rust_server'),
        'config_file': os.path.join(SERVER_DIR, RUST_CONFIG_FILE)
    }
    
    # Check if save directory exists
    if os.path.exists(world_info['save_directory']):
        world_info['has_save_data'] = True
        world_info['save_size_mb'] = ServerUtils.get_directory_size(world_info['save_directory'])
    else:
        world_info['has_save_data'] = False
        world_info['save_size_mb'] = 0
    
    return world_info

def start_rust_server_interactive():
    """
    Interactive command-line interface for starting a Rust server.
    
    Provides a user-friendly command-line interface for configuring and
    starting a Rust server with custom settings. Prompts for all major
    configuration options with sensible defaults.
    
    This function is useful for manual server setup and testing but is
    not typically used by the GUI application.
    
    Returns:
        bool: True if server was successfully started, False otherwise
    """
    print("=" * SEPARATOR_LINE_LENGTH)
    print("🦀 Rust Dedicated Server Configuration")
    print("=" * SEPARATOR_LINE_LENGTH)
    
    try:
        # Get server configuration from user
        server_name = input(f"Server Name [{DEFAULT_SERVER_NAME}]: ").strip() or DEFAULT_SERVER_NAME
        
        max_players_input = input(f"Max Players [{RUST_MAX_PLAYERS_DEFAULT}]: ").strip()
        max_players = int(max_players_input) if max_players_input else RUST_MAX_PLAYERS_DEFAULT
        max_players = max(RUST_MIN_PLAYERS, min(max_players, RUST_MAX_PLAYERS_LIMIT))
        
        world_size_input = input(f"World Size [{RUST_DEFAULT_WORLD_SIZE}]: ").strip()
        world_size = int(world_size_input) if world_size_input else RUST_DEFAULT_WORLD_SIZE
        world_size = max(RUST_MIN_WORLD_SIZE, min(world_size, RUST_MAX_WORLD_SIZE))
        
        seed_input = input(f"World Seed [{RUST_DEFAULT_SEED}]: ").strip()
        seed = int(seed_input) if seed_input else RUST_DEFAULT_SEED
        seed = max(1, min(seed, RUST_MAX_SEED))
        
        port_input = input(f"Server Port [{RUST_DEFAULT_PORT}]: ").strip()
        port = int(port_input) if port_input else RUST_DEFAULT_PORT
        
        pve_input = input("PvE Mode? [y/N]: ").strip().lower()
        pve_mode = pve_input.startswith('y')
        
        print("\n" + "=" * CONFIRMATION_SEPARATOR_LENGTH)
        print("📋 Server Configuration Summary:")
        print(f"   🏷️  Server Name: {server_name}")
        print(f"   👥 Max Players: {max_players}")
        print(f"   🗺️  World Size: {world_size}")
        print(f"   🎲 Seed: {seed}")
        print(f"   🌐 Port: {port}")
        print(f"   ⚔️  PvE Mode: {'Yes' if pve_mode else 'No'}")
        print("=" * CONFIRMATION_SEPARATOR_LENGTH)
        
        confirm = input("\nStart server with these settings? [Y/n]: ").strip().lower()
        if confirm and not confirm.startswith('y'):
            print("❌ Server start cancelled.")
            return False
        
        print(f"\n🚀 Starting Rust server...")
        success = start_rust_server(
            server_name=server_name,
            max_players=max_players,
            world_size=world_size,
            seed=seed,
            port=port,
            pve_mode=pve_mode
        )
        
        if success:
            print("🎉 Rust server started successfully!")
            print(f"🖥️  The server is now running in a separate console window!")
            print(f"🌍 Players can connect to: {port}")
            print(f"🗺️  World Size: {world_size} with seed {seed}")
            print(f"👥 Player Limit: {max_players}")
            print("💾 Progress will be automatically saved.")
            print("🔧 To stop the server: Close the server console window or use CTRL+C")
            if pve_mode:
                print("🕊️  PvE Mode: Player vs Player combat is disabled")
            else:
                print("⚔️  PvP Mode: Full player vs player combat enabled")
            print("🦀 Welcome to the world of Rust!")
            print("=" * SEPARATOR_LINE_LENGTH)
        else:
            print("❌ Failed to start Rust server!")
            print("🔧 Please check the error messages above for troubleshooting.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n❌ Configuration cancelled by user.")
        return False
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def configure_rust_firewall(port=RUST_DEFAULT_PORT):
    """
    Configure Windows Firewall rules for Rust server.
    
    Creates firewall rules to allow Rust server traffic through Windows Firewall.
    This includes rules for the game port, query port, RCON port, and app port.
    
    Args:
        port (int): Base port number for the server (default: 28015)
    
    Returns:
        bool: True if firewall rules were successfully created, False otherwise
        
    Note:
        This function requires administrator privileges to modify firewall rules.
        On non-Windows systems, this function will return True without action.
        Manual firewall configuration may be required on some systems.
    """
    if os.name != 'nt':  # Not Windows
        return True
    
    try:
        import subprocess
        
        # Define firewall rules for Rust
        rules = [
            {
                'name': f'Rust Server Game Port {port}',
                'port': port,
                'protocol': 'UDP',
                'description': 'Rust Dedicated Server - Game Traffic'
            },
            {
                'name': f'Rust Server Query Port {port + 1}',
                'port': port + 1,
                'protocol': 'UDP', 
                'description': 'Rust Dedicated Server - Query Port'
            },
            {
                'name': f'Rust Server RCON Port {port + 1}',
                'port': port + 1,
                'protocol': 'TCP',
                'description': 'Rust Dedicated Server - RCON'
            },
            {
                'name': 'Rust Server App Port 28082',
                'port': 28082,
                'protocol': 'TCP',
                'description': 'Rust Dedicated Server - Rust+ App'
            }
        ]
        
        success = True
        for rule in rules:
            try:
                # Create inbound rule
                cmd = [
                    'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                    f'name={rule["name"]}',
                    'dir=in',
                    'action=allow',
                    f'protocol={rule["protocol"]}',
                    f'localport={rule["port"]}',
                    'enable=yes'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"✅ Created firewall rule: {rule['name']}")
                
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Failed to create firewall rule {rule['name']}: {e}")
                success = False
                
        return success
        
    except Exception as e:
        print(f"❌ Firewall configuration error: {e}")
        return False

def create_rust_server_config(config):
    """
    Create Rust server configuration files.
    
    Generates the necessary configuration files for the Rust server based on
    the provided configuration dictionary. This includes server.cfg and other
    essential configuration files.
    
    Args:
        config (dict): Configuration dictionary containing server settings
    
    Returns:
        bool: True if configuration files were successfully created, False otherwise
        
    Note:
        Rust server configuration is primarily done through command line arguments,
        but some settings can be stored in configuration files for persistence.
    """
    try:
        # Ensure server directory exists
        os.makedirs(SERVER_DIR, exist_ok=True)
        
        # Create basic server.cfg file
        config_file_path = os.path.join(SERVER_DIR, RUST_CONFIG_FILE)
        
        config_content = f"""# Rust Dedicated Server Configuration
# Generated by Dedicated Server Automation

# Server Identity
server.hostname "{config.get('server_name', DEFAULT_SERVER_NAME)}"
server.identity "rust_server"

# Player Settings
server.maxplayers {config.get('max_players', RUST_MAX_PLAYERS_DEFAULT)}

# World Settings
server.worldsize {config.get('world_size', RUST_DEFAULT_WORLD_SIZE)}
server.seed {config.get('seed', RUST_DEFAULT_SEED)}

# Performance Settings
server.saveinterval {config.get('save_interval', RUST_DEFAULT_SAVE_INTERVAL)}
fps.limit {config.get('tickrate', RUST_DEFAULT_TICKRATE)}

# Security Settings
server.secure {str(config.get('secure', True)).lower()}

# Game Mode Settings
server.pve {str(config.get('pve_mode', False)).lower()}

# Network Settings
server.port {config.get('port', RUST_DEFAULT_PORT)}
"""
        
        with open(config_file_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ Created server configuration: {config_file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create server configuration: {e}")
        return False

# Main execution for standalone testing
if __name__ == '__main__':
    print("🦀 Rust Dedicated Server Management")
    print("This script provides Rust server management functionality.")
    print("For interactive setup, use start_rust_server_interactive()")
