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

def install_or_update_dst_server():
    """Install or update the Don't Starve Together dedicated server with file injection"""
    try:
        print("🔄 Installing Don't Starve Together Dedicated Server...")
        
        # Method 1: Try SteamCMD installation with file injection
        print("🧬 Attempting SteamCMD installation with file injection...")
        if install_dst_with_file_injection():
            return True
        else:
            print("❌ All installation methods failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during DST server installation: {str(e)}")
        return False

def install_dst_with_file_injection():
    """Install DST server with automatic file injection for missing components"""
    try:
        print("🔄 Installing DST with enhanced file support...")
        
        # Try SteamCMD installation first
        if not SteamCMDUtils.install_or_update_server(DST_APPID, SERVER_DIR, EXECUTABLE_NAME):
            print("❌ SteamCMD installation failed")
            return False
            
        # Validate installation and inject missing files if needed
        if not validate_and_repair_dst_installation():
            print("❌ Installation validation and repair failed")
            return False
            
        print("✅ DST server installation completed with file injection!")
        return True
        
    except Exception as e:
        print(f"❌ Error during DST installation: {str(e)}")
        return False

def validate_and_repair_dst_installation():
    """Validate DST installation and inject missing files from bundled resources"""
    try:
        print("🔍 Validating DST installation...")
        
        # Check basic structure
        if not check_server_structure():
            return False
            
        # Check for critical files and inject if missing
        return True
        return inject_missing_files()
        
    except Exception as e:
        print(f"❌ Error during validation and repair: {str(e)}")
        return False

def inject_missing_files():
    """Inject missing DST files from bundled resources"""
    try:
        bundled_dir = os.path.join(os.path.dirname(__file__), '..', 'bundled_files', 'dst_core')
        
        if not os.path.exists(bundled_dir):
            print("❌ Bundled DST files not found in application")
            return False
            
        server_data_dir = os.path.join(SERVER_DIR, 'data')
        os.makedirs(server_data_dir, exist_ok=True)
        
        # Essential files to check and inject
        critical_files = [
            'scripts/main.lua',
            'scripts/constants.lua',
            'scripts/class.lua',
            'scripts/vector3.lua',
            'scripts/util.lua',
            'scripts/mathutil.lua',
            'scripts/debugprint.lua',
            'scripts/gamelogic.lua',
            'scripts/networking.lua',
            'scripts/simutil.lua'
        ]
        
        injected_count = 0
        
        for file_path in critical_files:
            server_file = os.path.join(server_data_dir, file_path)
            bundled_file = os.path.join(bundled_dir, file_path)
            
            # Check if file exists and is valid
            file_missing = not os.path.exists(server_file)
            file_empty = os.path.exists(server_file) and os.path.getsize(server_file) == 0
            
            if (file_missing or file_empty) and os.path.exists(bundled_file):
                print(f"💉 Injecting missing file: {file_path}")
                
                # Create directory if needed
                os.makedirs(os.path.dirname(server_file), exist_ok=True)
                
                # Copy bundled file
                shutil.copy2(bundled_file, server_file)
                injected_count += 1
                
        if injected_count > 0:
            print(f"✅ Injected {injected_count} missing files")
        else:
            print("✅ No file injection needed - all files present")
            
        # Final validation
        return validate_dst_installation()
        
    except Exception as e:
        print(f"❌ Error during file injection: {str(e)}")
        return False

def validate_dst_installation():
    """Validate that the DST installation has all required files"""
    try:
        exe_path = os.path.join(SERVER_DIR, 'bin', EXECUTABLE_NAME)
        scripts_path = os.path.join(SERVER_DIR, 'data', 'scripts', 'main.lua')
        
        if not os.path.exists(exe_path):
            print(f"❌ Server executable not found: {exe_path}")
            return False
            
        if not os.path.exists(scripts_path):
            print(f"❌ Main Lua script not found: {scripts_path}")
            return False
            
        print("✅ All required DST files found")
        return True
        
    except Exception as e:
        print(f"❌ Error validating DST installation: {str(e)}")
        return False

def find_steam_dst_installation():
    """Find existing Steam DST installation with expanded search"""
    print("🔍 Searching for Steam DST installation...")
    
    # Common Steam installation paths (using proper Windows path handling)
    steam_paths = [
        # User Steam directory
        os.path.join(os.path.expanduser("~"), "Steam", "steamapps", "common", DST_STEAM_DIR_NAME),
        # Alternative user Steam locations
        os.path.join("C:", "Users", os.environ.get("USERNAME", ""), "Steam", "steamapps", "common", DST_STEAM_DIR_NAME),
        os.path.join("D:", "Steam", "steamapps", "common", DST_STEAM_DIR_NAME),
        os.path.join("E:", "Steam", "steamapps", "common", DST_STEAM_DIR_NAME),
        # Program Files locations
        f"C:\\Program Files (x86)\\Steam\\steamapps\\common\\{DST_STEAM_DIR_NAME}",
        f"C:\\Program Files\\Steam\\steamapps\\common\\{DST_STEAM_DIR_NAME}",
        f"D:\\Program Files (x86)\\Steam\\steamapps\\common\\{DST_STEAM_DIR_NAME}",
        f"D:\\Program Files\\Steam\\steamapps\\common\\{DST_STEAM_DIR_NAME}",
        # Steam library folders (common alternative locations)
        f"C:\\SteamLibrary\\steamapps\\common\\{DST_STEAM_DIR_NAME}",
        f"D:\\SteamLibrary\\steamapps\\common\\{DST_STEAM_DIR_NAME}",
        f"E:\\SteamLibrary\\steamapps\\common\\{DST_STEAM_DIR_NAME}",
    ]
    
    for path in steam_paths:
        print(f"Checking: {path}")
        if os.path.exists(path):
            exe_path = os.path.join(path, 'bin', EXECUTABLE_NAME)
            if os.path.exists(exe_path):
                print(f"✅ Found Steam DST installation: {path}")
                return path
            else:
                print(f"❌ Directory exists but no executable found: {exe_path}")
        else:
            print(f"❌ Path does not exist: {path}")
    
    print("❌ No Steam DST installation found in any common location")
    return None

def show_manual_installation_instructions():
    """Show manual installation instructions to user"""
    print("\n❌ No Steam DST installation found!")
    print("\n📋 Manual Installation Instructions:")
    print("1. Open Steam client")
    print("2. Go to Library > Tools")
    print("3. Install 'Don't Starve Together Dedicated Server'")
    print("4. Run this setup again")
    print("\nAlternatively, you can:")
    print("1. Install DST normally through Steam")
    print("2. In Steam, right-click Don't Starve Together")
    print("3. Properties > DLC > Check 'Don't Starve Together Dedicated Server'")
    print("4. Let it download, then run this setup again")

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
        # Run diagnostics before starting
        print("🔍 Running pre-startup diagnostics...")
        if not diagnose_and_fix_dst_server():
            print("❌ Pre-startup diagnostics failed. Please fix issues before starting.")
            return False
            
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

def diagnose_and_fix_dst_server():
    """Diagnose and attempt to fix common DST server issues"""
    try:
        print("\n🔍 Running DST Server Diagnostics...")
        
        if not check_server_structure():
            return False
            
        if not check_data_files():
            return attempt_data_repair()
            
        print("✅ DST server diagnostics completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during diagnostics: {str(e)}")
        return False

def check_server_structure():
    """Check basic server directory structure"""
    if not os.path.exists(SERVER_DIR):
        print("❌ Server directory not found")
        return False
        
    exe_path = os.path.join(SERVER_DIR, 'bin', EXECUTABLE_NAME)
    if not os.path.exists(exe_path):
        print(f"❌ Server executable not found: {exe_path}")
        return False
    else:
        print(f"✅ Server executable found: {exe_path}")
        
    return True

def check_data_files():
    """Check for essential data files and scripts"""
    data_dir = os.path.join(SERVER_DIR, 'data')
    scripts_dir = os.path.join(data_dir, 'scripts')
    main_lua = os.path.join(scripts_dir, 'main.lua')
    
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return False
    print(f"✅ Data directory found: {data_dir}")
        
    if not os.path.exists(scripts_dir):
        print(f"❌ Scripts directory not found: {scripts_dir}")
        return False
    print(f"✅ Scripts directory found: {scripts_dir}")
        
    if not os.path.exists(main_lua):
        print(f"❌ Main Lua script not found: {main_lua}")
        return False
    print(f"✅ Main Lua script found: {main_lua}")
        
    # Check file readability
    try:
        with open(main_lua, 'r') as f:
            content = f.read(100)
            if not content.strip():
                print("❌ Main Lua script is empty")
                return False
            print("✅ Main Lua script is readable and has content")
    except Exception as e:
        print(f"❌ Cannot read main Lua script: {e}")
        return False
        
    return True

def attempt_data_repair():
    """Attempt to repair missing DST data files"""
    try:
        print("\n🔧 Attempting to repair DST server data...")
        
        # Try to find data files in Steam installation (using proper Windows paths)
        steam_paths = [
            os.path.join(os.path.expanduser("~"), "Steam", "steamapps", "common", DST_STEAM_DIR_NAME),
            f"C:\\Program Files (x86)\\Steam\\steamapps\\common\\{DST_STEAM_DIR_NAME}",
            f"C:\\Program Files\\Steam\\steamapps\\common\\{DST_STEAM_DIR_NAME}"
        ]
        
        for steam_path in steam_paths:
            steam_data = os.path.join(steam_path, 'data')
            if os.path.exists(steam_data):
                print(f"✅ Found Steam data directory: {steam_data}")
                
                # Copy missing data files
                server_data = os.path.join(SERVER_DIR, 'data')
                if not os.path.exists(server_data):
                    print("📁 Copying data directory from Steam installation...")
                    shutil.copytree(steam_data, server_data)
                    return True
                else:
                    # Copy specific missing files
                    steam_scripts = os.path.join(steam_data, 'scripts')
                    server_scripts = os.path.join(server_data, 'scripts')
                    
                    if not os.path.exists(server_scripts) and os.path.exists(steam_scripts):
                        print("📁 Copying scripts directory from Steam installation...")
                        shutil.copytree(steam_scripts, server_scripts)
                        return True
                        
        print("❌ Could not find Steam data files to repair with")
        print("\n💡 Suggested fix:")
        print("1. Reinstall DST Dedicated Server through Steam")
        print("2. Verify game files integrity in Steam")
        print("3. Run this setup again")
        return False
        
    except Exception as e:
        print(f"❌ Error during data repair: {str(e)}")
        return False

def main():
    """Main function for standalone execution"""
    print("Don't Starve Together Dedicated Server Setup")
    print("=" * 50)
    
    # Example usage
    if uninstall_dst_server():
        remove_dst_port_forwarding()

if __name__ == "__main__":
    main()
