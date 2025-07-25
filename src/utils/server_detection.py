# ================== SERVER DETECTION CONSTANTS ==================
# Network and connectivity constants
GOOGLE_DNS_IP = "8.8.8.8"               # Google DNS server for connectivity testing
HTTP_PORT = 80                           # Standard HTTP port for connectivity tests
HTTP_SUCCESS_CODE = 200                  # HTTP success response code
NETWORK_TIMEOUT_SECONDS = 2              # Reduced timeout for network requests (was 3)
IP_ADDRESS_INDEX = 0                     # Index for IP address in socket address tuple
PUBLIC_IP_CACHE_DURATION = 300           # Cache public IP for 5 minutes (seconds)

# Error messages
IP_UNABLE_TO_DETERMINE = "Unable to determine"  # Error message for IP detection failures

# Server port defaults
VALHEIM_DEFAULT_SERVER_PORT = 2456       # Default port for Valheim dedicated server
VALHEIM_QUERY_PORT = 2457                # Valheim server query port
VALHEIM_RCON_PORT = 2458                 # Valheim remote console port
PALWORLD_DEFAULT_SERVER_PORT = 8211      # Default port for Palworld dedicated server
RUST_DEFAULT_SERVER_PORT = 28015         # Default port for Rust dedicated server
RUST_QUERY_PORT = 28016                  # Rust server query port
RUST_RCON_PORT = 28016                   # Rust remote console port
RUST_APP_PORT = 28082                    # Rust+ companion app port
MINECRAFT_DEFAULT_SERVER_PORT = 25565    # Default port for Minecraft server
SATISFACTORY_DEFAULT_SERVER_PORT = 7777  # Default port for Satisfactory server

import psutil
import socket
import requests
import subprocess
import platform
import time

# Global cache for public IP to avoid repeated network calls
_public_ip_cache = None
_public_ip_cache_time = 0

def get_local_ip():
    """
    Get the local/private IP address of the machine.
    
    Uses socket connection to determine the local IP address that would
    be used to connect to external networks. This is typically the IP
    address assigned by your router (e.g., 192.168.1.x).
    
    Returns:
        str: Local IP address (e.g., "192.168.1.100") or error message
    """
    try:
        # Create a socket connection to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to a remote address (doesn't actually send data)
            s.connect((GOOGLE_DNS_IP, HTTP_PORT))
            local_ip = s.getsockname()[IP_ADDRESS_INDEX]
        return local_ip
    except Exception:
        return IP_UNABLE_TO_DETERMINE

def get_public_ip():
    """
    Get the public/external IP address with intelligent caching.
    
    Determines the public IP address that external users would use to
    connect to your server. Uses caching to reduce network requests
    and improve performance. Tries multiple services for reliability.
    
    Caching behavior:
    - Cache duration: 5 minutes (300 seconds)
    - Returns cached result if still valid
    - Falls back to backup services if primary fails
    - Caches failures to avoid repeated attempts
    
    Returns:
        str: Public IP address (e.g., "203.0.113.42") or error message
    """
    global _public_ip_cache, _public_ip_cache_time
    
    current_time = time.time()
    
    # Return cached IP if it's still valid (within cache duration)
    if (_public_ip_cache is not None and 
        _public_ip_cache != IP_UNABLE_TO_DETERMINE and
        current_time - _public_ip_cache_time < PUBLIC_IP_CACHE_DURATION):
        return _public_ip_cache
    
    try:
        # Try only the fastest service first
        try:
            response = requests.get("https://api.ipify.org", timeout=NETWORK_TIMEOUT_SECONDS)
            if response.status_code == HTTP_SUCCESS_CODE:
                public_ip = response.text.strip()
                _public_ip_cache = public_ip
                _public_ip_cache_time = current_time
                return public_ip
        except Exception:
            pass
        
        # Fallback to second service if first fails
        try:
            response = requests.get("https://ipinfo.io/ip", timeout=NETWORK_TIMEOUT_SECONDS)
            if response.status_code == HTTP_SUCCESS_CODE:
                public_ip = response.text.strip()
                _public_ip_cache = public_ip
                _public_ip_cache_time = current_time
                return public_ip
        except Exception:
            pass
        
        # Cache the failure to avoid repeated attempts for a short time
        _public_ip_cache = IP_UNABLE_TO_DETERMINE
        _public_ip_cache_time = current_time
        return IP_UNABLE_TO_DETERMINE
        
    except Exception:
        _public_ip_cache = IP_UNABLE_TO_DETERMINE
        _public_ip_cache_time = current_time
        return IP_UNABLE_TO_DETERMINE

def is_valheim_server_running():
    """
    Check if Valheim dedicated server is currently running.
    
    Scans system processes to detect if a Valheim server instance is active.
    Uses optimized process scanning that checks only process names (not command lines)
    for better performance. Handles cross-platform executable naming.
    
    Process detection strategy:
    - Checks exact process name matches first (fastest)
    - Falls back to partial name matching if needed
    - Handles Windows (.exe) and Linux naming conventions
    - Gracefully handles access denied and zombie processes
    
    Returns:
        bool: True if Valheim server process is running, False otherwise
    """
    try:
        # Look for Valheim server processes with optimized search
        valheim_processes = [
            "valheim_server.exe",
            "valheim_server",
            "valheim_server.sh"
        ]
        
        # Use attrs=['pid', 'name'] only to reduce memory overhead
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            try:
                process_name = proc.info['name']
                if process_name:
                    process_name_lower = process_name.lower()
                    # Quick check for exact matches first (most common case)
                    if any(valheim_proc.lower() == process_name_lower for valheim_proc in valheim_processes):
                        return True
                    # Then check for partial matches
                    if 'valheim' in process_name_lower and 'server' in process_name_lower:
                        return True
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        return False
    except Exception:
        return False

def get_valheim_server_port():
    """
    Detect the port that Valheim server is currently using.
    
    Scans all listening network connections to find which port the Valheim
    server is bound to. Uses optimized scanning that gets all connections
    once instead of checking each port individually.
    
    Port detection strategy:
    - Scans all listening TCP connections once
    - Checks Valheim ports in priority order (game, query, RCON)
    - Returns the first matching port found
    - Falls back to default port if none detected
    
    Valheim uses multiple ports:
    - 2456: Main game server port (default)
    - 2457: Query port for server info
    - 2458: RCON port for remote admin
    
    Returns:
        int: Port number the Valheim server is using (or default 2456)
    """
    try:
        # Get all listening connections at once to avoid multiple scans
        listening_ports = set()
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_LISTEN and conn.laddr:
                listening_ports.add(conn.laddr.port)
        
        # Check for Valheim ports in order of priority
        valheim_ports = [VALHEIM_DEFAULT_SERVER_PORT, VALHEIM_QUERY_PORT, VALHEIM_RCON_PORT]
        for port in valheim_ports:
            if port in listening_ports:
                return port
        
        # If not found, return default
        return VALHEIM_DEFAULT_SERVER_PORT
    except Exception:
        return VALHEIM_DEFAULT_SERVER_PORT

def is_palworld_server_running():
    """
    Check if Palworld dedicated server is currently running.
    
    Scans system processes to detect if a Palworld server instance is active.
    Palworld has multiple executable variants (Test, Shipping) so this function
    checks for all known Palworld server process names.
    
    Process detection strategy:
    - Checks for exact executable name matches (fastest)
    - Handles multiple Palworld server variants
    - Falls back to partial name matching for edge cases
    - Uses optimized process scanning for better performance
    
    Known Palworld executables:
    - PalServer.exe (main executable)
    - PalServer-Win64-Test-Cmd.exe (test build)
    - PalServer-Win64-Shipping-Cmd.exe (shipping build)
    
    Returns:
        bool: True if Palworld server process is running, False otherwise
    """
    try:
        # Look for Palworld server processes with optimized search
        palworld_processes = [
            "PalServer.exe",
            "PalServer-Win64-Test-Cmd.exe", 
            "PalServer-Win64-Shipping-Cmd.exe"
        ]
        
        # Use attrs=['pid', 'name'] only to reduce memory overhead
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            try:
                process_name = proc.info['name']
                if process_name:
                    process_name_lower = process_name.lower()
                    # Quick check for exact matches first (most common case)
                    if any(palworld_proc.lower() == process_name_lower for palworld_proc in palworld_processes):
                        return True
                    # Then check for partial matches
                    if 'palworld' in process_name_lower and 'server' in process_name_lower:
                        return True
                    if 'palserver' in process_name_lower:
                        return True
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        return False
    except Exception:
        return False

def get_palworld_server_port():
    """Get the port that Palworld server is running on - optimized version"""
    try:
        # Check if default port is in use efficiently
        for conn in psutil.net_connections(kind='inet'):
            if (conn.laddr and 
                conn.laddr.port == PALWORLD_DEFAULT_SERVER_PORT and 
                conn.status == psutil.CONN_LISTEN):
                return PALWORLD_DEFAULT_SERVER_PORT
        
        # If not found, return default
        return PALWORLD_DEFAULT_SERVER_PORT
    except Exception:
        return PALWORLD_DEFAULT_SERVER_PORT

def is_rust_server_running():
    """
    Check if Rust dedicated server is currently running.
    
    Scans system processes to detect if a Rust server instance is active.
    Rust servers run as RustDedicated.exe on Windows and may have variations
    on other platforms. Uses optimized process scanning for better performance.
    
    Process detection strategy:
    - Checks for exact executable name matches (fastest)
    - Handles multiple Rust server variants and platforms
    - Falls back to partial name matching for edge cases
    - Uses optimized process scanning for better performance
    
    Known Rust executables:
    - RustDedicated.exe (Windows)
    - RustDedicated (Linux)
    - rust_server (alternative naming)
    
    Returns:
        bool: True if Rust server process is running, False otherwise
    """
    try:
        # Look for Rust server processes with optimized search
        rust_processes = [
            "RustDedicated.exe",
            "RustDedicated",
            "rust_server.exe",
            "rust_server"
        ]
        
        # Use attrs=['pid', 'name'] only to reduce memory overhead
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            try:
                process_name = proc.info['name']
                if process_name:
                    process_name_lower = process_name.lower()
                    # Quick check for exact matches first (most common case)
                    if any(rust_proc.lower() == process_name_lower for rust_proc in rust_processes):
                        return True
                    # Then check for partial matches
                    if 'rust' in process_name_lower and 'dedicated' in process_name_lower:
                        return True
                    if 'rustdedicated' in process_name_lower:
                        return True
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        return False
    except Exception:
        return False

def get_rust_server_port():
    """
    Detect the port that Rust server is currently using.
    
    Scans all listening network connections to find which port the Rust
    server is bound to. Uses optimized scanning that gets all connections
    once instead of checking each port individually.
    
    Port detection strategy:
    - Scans all listening TCP and UDP connections once
    - Checks Rust ports in priority order (game, query, RCON, app)
    - Returns the first matching port found
    - Falls back to default port if none detected
    
    Rust uses multiple ports:
    - 28015: Main game server port (default, UDP)
    - 28016: Query port for server browser (UDP) / RCON (TCP)
    - 28082: Rust+ companion app port (TCP)
    
    Returns:
        int: Port number the Rust server is using (or default 28015)
    """
    try:
        # Get all listening connections at once to avoid multiple scans
        listening_ports = set()
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_LISTEN and conn.laddr:
                listening_ports.add(conn.laddr.port)
        
        # Check for Rust ports in order of priority
        rust_ports = [RUST_DEFAULT_SERVER_PORT, RUST_QUERY_PORT, RUST_RCON_PORT, RUST_APP_PORT]
        for port in rust_ports:
            if port in listening_ports:
                return port
        
        # If not found, return default
        return RUST_DEFAULT_SERVER_PORT
    except Exception:
        return RUST_DEFAULT_SERVER_PORT

def get_server_status_info(game_name, skip_public_ip=False):
    """
    Get comprehensive server status information for any supported game.
    
    This is the main entry point for server status detection. It gathers
    complete information about a game server including running status,
    network configuration, and connection details.
    
    Supports multiple detection modes:
    - Full mode: Gets local IP, public IP, port, and connection info
    - Fast mode: Skips public IP lookup for immediate response
    
    Information returned:
    - is_running: Whether the server process is active
    - local_ip: Local/private IP address for LAN connections
    - public_ip: Public IP address for internet connections
    - port: Port number the server is using
    - connection_string: Ready-to-use connection string for clients
    
    Performance considerations:
    - Uses caching for public IP (5-minute cache)
    - Optimized process and network scanning
    - Fast mode provides instant local status
    
    Args:
        game_name (str): Name of the game to check ("valheim", "palworld", etc.)
        skip_public_ip (bool): If True, skips public IP lookup for faster response
        
    Returns:
        dict: Comprehensive server status information
    """
    game_name_lower = game_name.lower()
    
    status_info = {
        'is_running': False,
        'local_ip': get_local_ip(),
        'public_ip': IP_UNABLE_TO_DETERMINE if skip_public_ip else get_public_ip(),
        'port': None,
        'connection_string': None
    }
    
    if game_name_lower == "palworld":
        status_info['is_running'] = is_palworld_server_running()
        if status_info['is_running']:
            status_info['port'] = get_palworld_server_port()
            if status_info['local_ip'] != IP_UNABLE_TO_DETERMINE:
                status_info['connection_string'] = f"{status_info['local_ip']}:{status_info['port']}"
    
    elif game_name_lower == "valheim":
        status_info['is_running'] = is_valheim_server_running()
        if status_info['is_running']:
            status_info['port'] = get_valheim_server_port()
            if status_info['local_ip'] != IP_UNABLE_TO_DETERMINE:
                status_info['connection_string'] = f"{status_info['local_ip']}:{status_info['port']}"
    
    elif game_name_lower == "rust":
        status_info['is_running'] = is_rust_server_running()
        if status_info['is_running']:
            status_info['port'] = get_rust_server_port()
            if status_info['local_ip'] != IP_UNABLE_TO_DETERMINE:
                status_info['connection_string'] = f"{status_info['local_ip']}:{status_info['port']}"
    
    return status_info

def get_server_status_info_fast(game_name):
    """
    Get server status information quickly without public IP lookup.
    
    This is a convenience function that calls get_server_status_info()
    with skip_public_ip=True for immediate response. Perfect for UI
    updates where you want instant feedback and can update public IP later.
    
    Use this when:
    - You need immediate server status for UI updates
    - Public IP is not immediately needed
    - You want to avoid network delays
    - You're doing rapid status checks
    
    Args:
        game_name (str): Name of the game to check
        
    Returns:
        dict: Server status info with local information only
    """
    return get_server_status_info(game_name, skip_public_ip=True)
