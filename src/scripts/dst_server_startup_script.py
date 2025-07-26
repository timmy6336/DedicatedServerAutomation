"""
Don't Starve Together Dedicated Server Management Script

This module provides a simplified interface for managing Don't Starve Together dedicated servers.
It handles the unique requirements of DST including dual-shard setup (Master + Caves),
server token management, and Klei-specific configuration.

Features:
- SteamCMD installation and management
- DST server installation and updates with progress tracking
- Server token validation and configuration
- Master and Caves shard setup
- World generation configuration
- Mod support configuration
- Server startup and management

Don't Starve Together requires both Master and Caves shards to run simultaneously
for the full game experience.
"""

# ================== DST SERVER CONSTANTS ==================
DST_DEFAULT_MASTER_PORT = 11000         # Default port for Master shard
DST_DEFAULT_CAVES_PORT = 11001          # Default port for Caves shard
DST_STEAM_MASTER_PORT = 27018           # Steam authentication port for Master
DST_STEAM_CAVES_PORT = 27019            # Steam authentication port for Caves
DST_AUTH_MASTER_PORT = 8768             # Authentication port for Master
DST_AUTH_CAVES_PORT = 8769              # Authentication port for Caves
DST_STEAM_DIR_NAME = "Dont Starve Together Dedicated Server"  # Steam directory name

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from utils.server_startup_script_utils import (
    SteamCMDUtils, 
    UPnPUtils, 
    ServerUtils, 
    GameConfig
)
from utils.logging_utils import get_logger, OperationTimer

# Initialize enhanced logging for DST operations
logger = get_logger("DST_Server")

# DST-specific configuration
DST_CONFIG = {
    'name': 'Dont Starve Together',
    'app_id': '343050',
    'default_port': DST_DEFAULT_MASTER_PORT,
    'executable': 'dontstarve_dedicated_server_nullrenderer.exe'
}

SERVER_DIR, EXECUTABLE_NAME = ServerUtils.get_server_paths(DST_CONFIG['name'])
DST_APPID = DST_CONFIG['app_id']

def get_dst_config_path():
    """Get the DST configuration directory path"""
    user_profile = os.environ.get('USERPROFILE', '')
    config_path = os.path.join(user_profile, 'Documents', 'Klei', 'DoNotStarveTogether', 'MyDediServer')
    return config_path

def download_steamcmd():
    """Download and install SteamCMD if not already present"""
    return SteamCMDUtils.download_steamcmd()

def _check_system_requirements():
    """Check and log system requirements for DST server"""
    try:
        import psutil
        
        # Check available disk space
        if os.path.exists(os.path.dirname(SERVER_DIR)):
            usage = psutil.disk_usage(os.path.dirname(SERVER_DIR))
            free_gb = usage.free / (1024**3)
            
            logger.info(f"Available disk space: {free_gb:.2f} GB")
            
            if free_gb < 5.0:  # DST needs ~4GB + buffer
                logger.warning(f"⚠️ Low disk space warning: Only {free_gb:.2f} GB free (minimum 5GB recommended)")
                if free_gb < 2.0:
                    logger.error(f"❌ Insufficient disk space: {free_gb:.2f} GB free (minimum 2GB required)")
                    raise Exception(f"Insufficient disk space: {free_gb:.2f} GB available, minimum 2GB required")
        
        # Check memory
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        logger.info(f"Available memory: {available_gb:.2f} GB")
        
        if available_gb < 1.0:
            logger.warning(f"⚠️ Low memory warning: Only {available_gb:.2f} GB available")
            
        logger.info("✅ System requirements check passed")
        
    except Exception as e:
        logger.error(f"System requirements check failed: {str(e)}")
        raise

def install_or_update_dst_server():
    """Install or update the Don't Starve Together dedicated server with file injection"""
    with OperationTimer(logger, "DST Server Installation"):
        try:
            logger.info("🔄 Installing Don't Starve Together Dedicated Server...")
            
            # Log system requirements check
            logger.info("Checking system requirements...")
            _check_system_requirements()
            
            # Log network connectivity
            logger.log_network_diagnostics()
            
            # Method 1: Try SteamCMD installation with file injection
            logger.info("🧬 Attempting SteamCMD installation with file injection...")
            
            context = {
                "installation_method": "SteamCMD with file injection",
                "app_id": DST_CONFIG['app_id'],
                "server_directory": SERVER_DIR,
                "executable": DST_CONFIG['executable']
            }

            if install_dst_server():
                logger.log_operation_success("DST Installation", details=context)
                return True
            else:
                logger.error("❌ All installation methods failed")
                logger.error("Installation context:")
                for key, value in context.items():
                    logger.error(f"  {key}: {value}")
                return False
                
        except Exception as e:
            context = {
                "installation_method": "SteamCMD with file injection",
                "app_id": DST_CONFIG['app_id'],
                "server_directory": SERVER_DIR,
                "executable": DST_CONFIG['executable'],
                "python_version": sys.version,
                "working_directory": os.getcwd()
            }
            logger.log_operation_failure("DST Server Installation", e, context=context)
            return False

def install_dst_server():
    """Install DST server with automatic file injection for missing components"""
    with OperationTimer(logger, "DST Installation with File Injection"):
        try:
            logger.info("🔄 Installing DST with enhanced file support...")
            
            # Log pre-installation state
            logger.info(f"Target server directory: {SERVER_DIR}")
            logger.info(f"Target executable: {EXECUTABLE_NAME}")
            logger.info(f"DST App ID: {DST_APPID}")
            
            # Check if server directory already exists
            if os.path.exists(SERVER_DIR):
                logger.info(f"Server directory already exists: {SERVER_DIR}")
                existing_files = len(list(Path(SERVER_DIR).rglob('*')))
                logger.info(f"Existing files in server directory: {existing_files}")
            else:
                logger.info("Server directory does not exist - will be created")
            
            # Try SteamCMD installation first
            logger.info("Attempting SteamCMD installation...")
            steamcmd_success = SteamCMDUtils.install_or_update_server(DST_APPID, SERVER_DIR, EXECUTABLE_NAME)
            
            if not steamcmd_success:
                logger.error("❌ SteamCMD installation failed")
                logger.error("Checking if SteamCMD is accessible...")
                
                # Additional diagnostics
                steamcmd_path = SteamCMDUtils._get_steamcmd_path()
                logger.error(f"SteamCMD path: {steamcmd_path}")
                logger.error(f"SteamCMD exists: {os.path.exists(steamcmd_path) if steamcmd_path else 'Path not found'}")
                
                return False
            
            logger.info("✅ DST server installation completed!")
            return True
            
        except Exception as e:
            context = {
                "target_directory": SERVER_DIR,
                "executable_name": EXECUTABLE_NAME,
                "app_id": DST_APPID,
                "steamcmd_available": hasattr(SteamCMDUtils, '_get_steamcmd_path'),
                "server_dir_exists": os.path.exists(SERVER_DIR) if SERVER_DIR else False
            }
            logger.log_operation_failure("DST Installation with File Injection", e, context=context)
            return False

def validate_server_token(token):
    """Validate the server token format"""
    if not token or len(token.strip()) == 0:
        return False, "Server token cannot be empty"
    
    # Basic validation - DST tokens are typically long alphanumeric strings
    token = token.strip()
    if len(token) < 20:
        return False, "Server token appears to be too short"
    
    # Check for basic format (allow alphanumeric and common token characters)
    # DST tokens can contain: letters, numbers, -, _, ^, /, +, =
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_^/+=')
    if not all(c in allowed_chars for c in token):
        return False, "Server token contains invalid characters"
    
    return True, "Token format appears valid"

def create_dst_configuration(server_name, server_description, max_players, password, server_token, enable_caves=True):
    """Create the DST server configuration files"""
    try:
        config_path = get_dst_config_path()
        
        # Create directory structure
        os.makedirs(config_path, exist_ok=True)
        os.makedirs(os.path.join(config_path, 'Master'), exist_ok=True)
        if enable_caves:
            os.makedirs(os.path.join(config_path, 'Caves'), exist_ok=True)
        
        # Create cluster.ini
        cluster_config = f"""[GAMEPLAY]
game_mode = survival
max_players = {max_players}
pvp = false
pause_when_empty = true

[NETWORK]
cluster_name = {server_name}
cluster_description = {server_description}
cluster_password = {password}
cluster_intention = cooperative
autosaver_enabled = true
enable_snapshots = true
offline_cluster = false

[MISC]
console_enabled = true

[SHARD]
shard_enabled = {str(enable_caves).lower()}
bind_ip = 127.0.0.1
master_ip = 127.0.0.1
master_port = {DST_DEFAULT_MASTER_PORT - 1}
cluster_key = supersecretkey
"""
        
        with open(os.path.join(config_path, 'cluster.ini'), 'w') as f:
            f.write(cluster_config)
        
        # Create cluster_token.txt
        token_file_path = os.path.join(config_path, 'cluster_token.txt')
        print(f"DEBUG: Writing token to: {token_file_path}")
        print(f"DEBUG: Token length: {len(server_token.strip())}")
        print(f"DEBUG: Token content: '{server_token.strip()}'")
        
        with open(token_file_path, 'w', encoding='utf-8') as f:
            f.write(server_token.strip())
        
        # Verify what was written
        with open(token_file_path, 'r', encoding='utf-8') as f:
            written_token = f.read()
            print(f"DEBUG: Verification - written token: '{written_token}'")
            print(f"DEBUG: Verification - tokens match: {written_token == server_token.strip()}")
        
        # Create Master shard configuration
        master_config = f"""[NETWORK]
server_port = {DST_DEFAULT_MASTER_PORT}

[SHARD]
is_master = true

[STEAM]
master_server_port = {DST_STEAM_MASTER_PORT}
authentication_port = {DST_AUTH_MASTER_PORT}
"""
        
        with open(os.path.join(config_path, 'Master', 'server.ini'), 'w') as f:
            f.write(master_config)
        
        # Create Master world generation override
        master_worldgen = """return {
    override_enabled = true,
    preset = "SURVIVAL_TOGETHER",
}"""
        
        with open(os.path.join(config_path, 'Master', 'worldgenoverride.lua'), 'w') as f:
            f.write(master_worldgen)
        
        if enable_caves:
            # Create Caves shard configuration
            caves_config = f"""[NETWORK]
server_port = {DST_DEFAULT_CAVES_PORT}

[SHARD]
is_master = false
name = Caves

[STEAM]
master_server_port = {DST_STEAM_CAVES_PORT}
authentication_port = {DST_AUTH_CAVES_PORT}
"""
            
            with open(os.path.join(config_path, 'Caves', 'server.ini'), 'w') as f:
                f.write(caves_config)
            
            # Create Caves world generation override
            caves_worldgen = """return {
    override_enabled = true,
    preset = "DST_CAVE",
}"""
            
            with open(os.path.join(config_path, 'Caves', 'worldgenoverride.lua'), 'w') as f:
                f.write(caves_worldgen)
        
        print("✅ DST server configuration created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating DST configuration: {str(e)}")
        return False

def setup_upnp_port_forwarding():
    """Set up UPnP port forwarding for DST server"""
    ports_to_forward = [
        DST_DEFAULT_MASTER_PORT,
        DST_DEFAULT_CAVES_PORT,
        DST_STEAM_MASTER_PORT,
        DST_STEAM_CAVES_PORT,
        DST_AUTH_MASTER_PORT,
        DST_AUTH_CAVES_PORT
    ]
    
    success = True
    for port in ports_to_forward:
        if not UPnPUtils.setup_port_forwarding(port, "UDP", f"DST Server Port {port}"):
            success = False
    
    return success

def start_dst_server(enable_caves=True):
    """Start the Don't Starve Together dedicated server with diagnostics"""
    try:
        print("🚀 Starting Don't Starve Together dedicated server...")
        server_exe = os.path.join(SERVER_DIR, 'bin', EXECUTABLE_NAME)
        config_path = get_dst_config_path()
        
        if not os.path.exists(server_exe):
            print("❌ DST server executable not found. Please install the server first.")
            return False
        
        if not os.path.exists(os.path.join(config_path, 'cluster_token.txt')):
            print("❌ Server configuration not found. Please configure the server first.")
            return False
        
        print("🚀 Starting Don't Starve Together dedicated server...")
        print(f"Server executable: {server_exe}")
        print(f"Configuration path: {config_path}")
        print(f"Working directory: {SERVER_DIR}")
        
        # Ensure we're in the correct working directory
        bin_dir = os.path.join(SERVER_DIR, 'bin')
        
        # Start Master shard
        master_cmd = [
            server_exe,
            '-console',
            '-persistent_storage_root', os.path.join(os.environ.get('USERPROFILE', ''), 'Documents', 'Klei'),
            '-conf_dir', 'DoNotStarveTogether', 
            '-cluster', 'MyDediServer',
            '-shard', 'Master'
        ]
        
        print("🌍 Starting Master shard...")
        print(f"Command: {' '.join(master_cmd)}")
        print(f"Working directory: {bin_dir}")
        
        subprocess.Popen(
            master_cmd,
            cwd=bin_dir,  # Use bin directory as working directory
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        if enable_caves:
            # Wait a moment for Master to start
            print("⏳ Waiting for Master shard to initialize...")
            time.sleep(10)
            
            # Start Caves shard
            caves_cmd = [
                server_exe,
                '-console',
                '-persistent_storage_root', os.path.join(os.environ.get('USERPROFILE', ''), 'Documents', 'Klei'),
                '-conf_dir', 'DoNotStarveTogether', 
                '-cluster', 'MyDediServer',
                '-shard', 'Caves'
            ]
            
            print("🕳️ Starting Caves shard...")
            subprocess.Popen(
                caves_cmd,
                cwd=bin_dir,  # Use bin directory as working directory  
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        
        print("✅ Don't Starve Together server started successfully!")
        print(f"🌐 Connect to your server using IP: localhost:{DST_DEFAULT_MASTER_PORT}")
        print("📝 Check the server console windows for status and logs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error starting DST server: {str(e)}")
        return False

def uninstall_dst_server():
    """Uninstall the Don't Starve Together server and remove configuration"""
    try:
        print("🗑️ Uninstalling Don't Starve Together server...")
        
        # Remove server files using utility function
        success = ServerUtils.uninstall_server(SERVER_DIR)

        # Remove DST configuration directory
        config_path = get_dst_config_path()
        if os.path.exists(config_path):
            try:
                import shutil
                shutil.rmtree(config_path)
                print("✅ DST configuration files removed")
            except Exception as e:
                print(f"⚠️ Failed to remove configuration files: {e}")
        
        if success:
            print("✅ Don't Starve Together server uninstalled successfully!")
        
        return success
        
    except Exception as e:
        print(f"❌ Error uninstalling DST server: {str(e)}")
        return False

def remove_dst_port_forwarding():
    """Remove all DST-related port forwarding rules"""
    ports_to_remove = [
        DST_DEFAULT_MASTER_PORT,
        DST_DEFAULT_CAVES_PORT,
        DST_STEAM_MASTER_PORT,
        DST_STEAM_CAVES_PORT,
        DST_AUTH_MASTER_PORT,
        DST_AUTH_CAVES_PORT
    ]
    
    success = True
    for port in ports_to_remove:
        if not UPnPUtils.remove_port_forwarding(port, "UDP"):
            success = False
    
    return success


def main():
    """Main function for standalone execution"""
    print("Don't Starve Together Dedicated Server Setup")
    print("=" * 50)
    
    # Example usage
    if uninstall_dst_server():
        remove_dst_port_forwarding()

if __name__ == "__main__":
    main()
