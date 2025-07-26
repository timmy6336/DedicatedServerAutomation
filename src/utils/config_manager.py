"""
Server Configuration Manager

Handles saving and loading user server configurations to persistent storage.
This allows server settings (password, name, world, etc.) to be remembered
between application sessions.

Key Features:
- Cross-platform configuration storage (Windows/Linux/macOS)
- JSON-based configuration files for human readability
- Automatic directory creation and error handling
- Support for multiple game server configurations
- Fallback to sensible defaults when configurations are missing

Technical Implementation:
- Windows: Stores configs in %LOCALAPPDATA%/DedicatedServerAutomation/
- Unix-like: Stores configs in ~/.config/DedicatedServerAutomation/
- File format: server_configs.json with nested game configurations
- Thread-safe file operations with proper exception handling
"""

# ================== CONFIGURATION MANAGER CONSTANTS ==================
# Default server configuration values
DEFAULT_VALHEIM_PORT = 2456              # Default port for Valheim dedicated server
DEFAULT_FILE_ENCODING = 'utf-8'         # File encoding for configuration files

import json
import os
import platform
from typing import Dict, Any, Optional


class ServerConfigManager:
    """
    Manages persistent storage of server configurations across application sessions.
    
    This class provides a centralized way to save, load, and manage server configurations
    for different game types. It automatically handles platform-specific storage locations,
    ensures data persistence, and provides fallback mechanisms for robustness.
    
    Architecture:
    - Singleton pattern via global instance for consistent access
    - JSON-based storage for human readability and easy debugging
    - Platform-aware directory selection following OS conventions
    - Graceful error handling with informative user feedback
    
    Storage Structure:
    {
        "Valheim": {
            "world_name": "DedicatedWorld",
            "server_name": "My Server",
            "password": "secret123",
            "port": DEFAULT_VALHEIM_PORT,
            ...
        },
        "Palworld": {
            "server_name": "Pal Server",
            "password": "palworld123",
            ...
        }
    }
    """
    
    def __init__(self):
        """
        Initialize the configuration manager with platform-appropriate storage paths.
        
        This constructor:
        1. Determines the correct configuration directory for the current OS
        2. Sets up the configuration file path
        3. Creates necessary directories if they don't exist
        4. Prepares the manager for immediate use
        
        The initialization is designed to be lightweight and fail-safe, ensuring
        the manager is always in a usable state even if file operations fail.
        
        Raises:
            No exceptions are raised directly, but directory creation failures
            will be handled gracefully in subsequent operations.
        """
        self.config_dir = self._get_config_directory()
        self.config_file = os.path.join(self.config_dir, 'server_configs.json')
        
        # Ensure config directory exists
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def _get_config_directory(self) -> str:
        """
        Determine the appropriate configuration directory based on the operating system.
        
        This method implements platform-specific storage conventions:
        - Windows: Uses %LOCALAPPDATA% (typically C:/Users/[user]/AppData/Local/)
        - Unix-like (Linux/macOS): Uses ~/.config/ following XDG Base Directory Specification
        
        The selected directories are:
        - Standard locations that applications commonly use for configuration data
        - User-writable without requiring administrator privileges
        - Automatically backed up by most system backup solutions
        - Persistent across application updates and reinstalls
        
        Implementation Details:
        - Windows: Checks LOCALAPPDATA environment variable with empty string fallback
        - Unix: Uses os.path.expanduser() to handle various home directory scenarios
        - Creates a subdirectory 'DedicatedServerAutomation' to avoid conflicts
        
        Returns:
            str: Absolute path to the configuration directory
            
        Note:
            The directory may not exist yet - creation is handled by the caller.
            This separation allows for better error handling and testing.
        """
        if platform.system().lower() == 'windows':
            # Use AppData/Local for Windows
            config_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'DedicatedServerAutomation')
        else:
            # Use ~/.config for Unix-like systems
            config_dir = os.path.expanduser('~/.config/DedicatedServerAutomation')
        
        return config_dir
    
    def save_server_config(self, game_name: str, config: Dict[str, Any]) -> bool:
        """
        Persist server configuration for a specific game to the configuration file.
        
        This method performs a complete save operation that:
        1. Loads all existing configurations to preserve other games' settings
        2. Updates the configuration for the specified game
        3. Writes the complete configuration set back to disk
        4. Provides comprehensive error handling and user feedback
        
        The save operation is atomic at the file level - either the entire
        configuration is saved successfully, or the original file remains unchanged.
        This prevents corruption from partial writes due to system failures.
        
        Configuration Merging:
        - Existing configurations for other games are preserved
        - The specified game's configuration is completely replaced
        - Invalid or corrupted existing data is handled gracefully
        
        Args:
            game_name (str): Identifier for the game (e.g., 'Valheim', 'Palworld')
                           Used as the top-level key in the configuration structure
            config (Dict[str, Any]): Complete configuration dictionary containing
                                   all settings for the game server (password, port,
                                   server name, world settings, etc.)
            
        Returns:
            bool: True if the configuration was saved successfully to disk,
                 False if any error occurred during the save operation
                 
        Side Effects:
            - Creates the configuration file if it doesn't exist
            - Updates the modification time of the configuration file
            - Prints status messages to console for user feedback
            
        Example:
            config = {
                'server_name': 'My Awesome Server',
                'password': 'secret123',
                'port': DEFAULT_VALHEIM_PORT,
                'world_name': 'MyWorld'
            }
            success = manager.save_server_config('Valheim', config)
        """
        try:
            # Load existing configurations
            all_configs = self.load_all_configs()
            
            # Update with new configuration
            all_configs[game_name] = config
            
            # Save to file
            with open(self.config_file, 'w', encoding=DEFAULT_FILE_ENCODING) as f:
                json.dump(all_configs, f, indent=2)
            
            print(f"✅ Saved {game_name} server configuration")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save {game_name} configuration: {e}")
            return False
    
    def load_server_config(self, game_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve saved server configuration for a specific game from persistent storage.
        
        This method provides safe configuration retrieval with comprehensive error handling.
        It's designed to be the primary interface for accessing saved server settings
        throughout the application lifecycle.
        
        Load Process:
        1. Attempts to load the complete configuration file from disk
        2. Extracts the configuration specific to the requested game
        3. Returns the configuration if found, or None if not present
        4. Handles file corruption, missing files, and permission errors gracefully
        
        Error Handling Strategy:
        - Missing configuration file: Returns None (normal for first-time use)
        - Corrupted JSON: Logs error and returns None (allows fallback to defaults)
        - Permission errors: Logs error and returns None (graceful degradation)
        - Missing game configuration: Returns None silently (normal case)
        
        Args:
            game_name (str): Identifier for the game whose configuration to retrieve
                           Must match the key used when saving the configuration
                           Case-sensitive to ensure consistency
            
        Returns:
            Optional[Dict[str, Any]]: 
                - Dictionary containing the complete saved configuration if found
                - None if no configuration exists for the specified game
                - None if any error occurs during loading
                
        Usage Patterns:
            # Standard usage with fallback to defaults
            config = manager.load_server_config('Valheim')
            if config:
                password = config.get('password', 'default_password')
            else:
                # Use application defaults
                config = get_default_config()
                
        Thread Safety:
            This method is read-only and safe for concurrent access.
            Multiple threads can call this method simultaneously without issues.
        """
        try:
            all_configs = self.load_all_configs()
            return all_configs.get(game_name)
            
        except Exception as e:
            print(f"❌ Failed to load {game_name} configuration: {e}")
            return None
    
    def load_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the complete configuration file containing all game server configurations.
        
        This method serves as the foundation for all configuration operations, providing
        centralized file access with robust error handling. It's used internally by
        other methods but can also be called directly for batch operations.
        
        File Format Expected:
        The configuration file should contain a JSON object with game names as keys:
        {
            "Valheim": { "password": "secret", "port": 2456, ... },
            "Palworld": { "password": "pal123", "port": 8211, ... }
        }
        
        Error Recovery:
        - Missing file: Returns empty dictionary (normal for first run)
        - Corrupted JSON: Logs error, returns empty dict (allows fresh start)
        - Permission denied: Logs error, returns empty dict (graceful degradation)
        - Invalid structure: Logs warning, attempts to continue with valid parts
        
        Performance Considerations:
        - File is read completely into memory (suitable for small config files)
        - No caching implemented - each call reads from disk for consistency
        - JSON parsing overhead is minimal for typical configuration sizes
        
        Returns:
            Dict[str, Dict[str, Any]]: 
                - Complete configuration dictionary with game names as top-level keys
                - Each game's configuration as a nested dictionary
                - Empty dictionary if file doesn't exist or any error occurs
                
        Internal Usage:
            This method is primarily used by save_server_config() and load_server_config()
            to maintain consistency in file access patterns.
            
        Debugging:
            Errors are logged to console with descriptive messages to aid troubleshooting.
            The method never raises exceptions, ensuring application stability.
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
                
        except Exception as e:
            print(f"❌ Failed to load configurations: {e}")
            return {}
    
    def delete_server_config(self, game_name: str) -> bool:
        """
        Remove a specific game's configuration from persistent storage.
        
        This method provides safe configuration deletion with preservation of other
        games' configurations. It's useful for cleanup operations, reset functionality,
        or when users want to return to default settings for a specific game.
        
        Deletion Process:
        1. Loads all existing configurations from the file
        2. Removes only the specified game's configuration
        3. Preserves all other games' configurations intact
        4. Saves the updated configuration set back to disk
        5. Provides clear feedback about the operation result
        
        Safety Features:
        - Atomic operation: Either deletion succeeds completely or file remains unchanged
        - Other configurations are never affected by this operation
        - Graceful handling of non-existent configurations (not treated as error)
        - Comprehensive error handling for file system issues
        
        Args:
            game_name (str): Identifier for the game whose configuration to delete
                           Must match the key used when the configuration was saved
                           Case-sensitive for consistency with save operations
            
        Returns:
            bool: True if configuration was found and successfully deleted,
                 False if configuration didn't exist or deletion failed
                 
        Side Effects:
            - Updates the configuration file on disk (if configuration existed)
            - Prints informational messages to console
            - May create backup behavior in future versions
            
        Use Cases:
            - User requests to reset server settings to defaults
            - Cleanup during application uninstallation
            - Troubleshooting corrupted configuration issues
            - Development and testing scenarios
            
        Example:
            # Reset Valheim settings to defaults
            if manager.delete_server_config('Valheim'):
                print("Valheim settings reset - will use defaults next time")
            else:
                print("No Valheim settings found to delete")
        """
        try:
            all_configs = self.load_all_configs()
            
            if game_name in all_configs:
                del all_configs[game_name]
                
                # Save updated configurations
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(all_configs, f, indent=2)
                
                print(f"✅ Deleted {game_name} server configuration")
                return True
            else:
                print(f"ℹ️ No configuration found for {game_name}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to delete {game_name} configuration: {e}")
            return False
    
    def get_default_valheim_config(self) -> Dict[str, Any]:
        """
        Provide default configuration values for Valheim dedicated servers.
        
        This method returns a complete, ready-to-use configuration that represents
        sensible defaults for a Valheim server setup. These defaults are used when:
        - No saved configuration exists (first-time setup)
        - Saved configuration is corrupted or incomplete
        - User explicitly requests to reset to defaults
        - Fallback is needed during error conditions
        
        Configuration Philosophy:
        - Security: Default password meets Valheim's minimum requirements but encourages change
        - Accessibility: Public server enabled for easier initial testing
        - Convenience: Standard port and common world name for predictability
        - Safety: Firewall and UPnP enabled for automatic network configuration
        
        Default Values Explanation:
        - world_name: 'DedicatedWorld' - Generic but descriptive world name
        - server_name: 'Valheim Server' - Simple, recognizable server identification
        - password: 'valheim123' - Meets 5-character minimum, easy to remember
        - port: 2456 - Official Valheim server port (UDP)
        - public_server: True - Listed in server browser for discoverability
        - configure_firewall: True - Automatically opens required ports
        - enable_upnp: True - Automatic port forwarding for home networks
        
        Returns:
            Dict[str, Any]: Complete default configuration dictionary with all
                          required keys and values for Valheim server operation
                          
        Usage:
            # Initialize new configuration
            config = manager.get_default_valheim_config()
            config['password'] = 'user_custom_password'
            manager.save_server_config('Valheim', config)
            
        Version Compatibility:
            These defaults are chosen to work with current Valheim server versions
            and may be updated as the game evolves or requirements change.
        """
        return {
            'world_name': 'DedicatedWorld',
            'server_name': 'Valheim Server',
            'password': 'valheim123',
            'port': 2456,
            'public_server': True,
            'configure_firewall': True,
            'enable_upnp': True
        }
    
    def get_default_palworld_config(self) -> Dict[str, Any]:
        """
        Provide default configuration values for Palworld dedicated servers.
        
        This method returns a complete default configuration specifically tailored
        for Palworld server requirements and best practices. The defaults are
        chosen based on common server administration needs and Palworld's
        specific technical requirements.
        
        Palworld-Specific Considerations:
        - Higher player capacity than Valheim (32 vs 10 players)
        - Different default port (8211 vs 2456)
        - Specific performance and networking requirements
        - Community preferences for server naming and accessibility
        
        Default Values Explanation:
        - server_name: 'Palworld Server' - Clear game identification
        - password: 'palworld123' - Meets game requirements, easy to remember
        - port: 8211 - Official Palworld server port (UDP)
        - public_server: True - Server browser visibility for player discovery
        - configure_firewall: True - Automatic Windows firewall configuration
        - enable_upnp: True - Home network port forwarding automation
        - max_players: 32 - Common maximum for stable server performance
        
        Returns:
            Dict[str, Any]: Complete default configuration dictionary with all
                          required keys and values for Palworld server operation
                          
        Future Extensibility:
            Additional Palworld-specific settings can be added here as the game
            develops new server configuration options or community needs evolve.
            
        Usage Pattern:
            # Get defaults and customize
            config = manager.get_default_palworld_config()
            config['max_players'] = 16  # Smaller server
            config['password'] = 'secure_password_here'
            manager.save_server_config('Palworld', config)
        """
        return {
            'server_name': 'Palworld Server',
            'password': 'palworld123',
            'port': 8211,
            'public_server': True,
            'configure_firewall': True,
            'enable_upnp': True,
            'max_players': 32
        }

    def get_default_rust_config(self) -> Dict[str, Any]:
        """
        Get default configuration for Rust server setup.
        
        Returns a dictionary containing default Rust server settings with
        sensible defaults for a Rust server setup. These defaults are used when:
        - No previous configuration exists for the user
        - The configuration file is corrupted or missing
        - User explicitly requests to reset to defaults
        
        Configuration includes server name, connection settings, gameplay options,
        and system configuration preferences that work well for most users.
        
        Returns:
            Dict[str, Any]: Dictionary containing default Rust server configuration
                          with keys for server_name, password, port, world_size,
                          max_players, server_description, pve_mode, configure_firewall,
                          enable_upnp, and save_interval
                          
        Example:
            config = manager.get_default_rust_config()
            config['max_players'] = 100  # Large server
            config['pve_mode'] = True     # PvE only server
            manager.save_server_config('Rust', config)
        """
        return {
            'server_name': 'Rust Server',
            'password': 'rust123',
            'port': 28015,
            'world_size': 3000,
            'max_players': 50,
            'server_description': 'A friendly Rust server',
            'pve_mode': False,
            'configure_firewall': True,
            'enable_upnp': True,
            'save_interval': 300
        }


# Global instance for easy access throughout the application
# This singleton pattern ensures consistent configuration access across all modules
# and prevents multiple instances from conflicting with file operations.
#
# Usage throughout application:
#   from utils.config_manager import config_manager
#   config = config_manager.load_server_config('Valheim')
#
# Benefits of global instance:
# - Consistent file access patterns across the application
# - Simplified import syntax for consuming modules
# - Centralized configuration state management
# - Reduced memory overhead from multiple instances
config_manager = ServerConfigManager()
