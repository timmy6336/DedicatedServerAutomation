"""
Game Data Model Module

This module defines the Game class which represents a video game and its metadata.
The Game class is responsible for loading game information from JSON files and
providing a standardized interface for accessing game properties throughout
the application.

The Game class supports:
- Loading game metadata from JSON configuration files
- Storing game properties like name, description, genre, platforms
- Managing game image paths for UI display
- Providing string representation for debugging

This is a core data model used by the main window and game details page
to display game information and manage server installations.
"""

import requests
import os
import json


class Game:
    """
    Represents a video game and its associated metadata.
    
    This class encapsulates all information about a game including its name,
    description, genre, platforms, and image assets. Game data is loaded from
    a JSON configuration file that contains detailed game information.
    
    Attributes:
        name (str): The game's display name
        description (str): Detailed description or summary of the game
        genre (str): Game genre(s), comma-separated if multiple
        image_url (str): Relative path to the game's image file
        platforms (list): List of platforms the game supports
    """
    
    def __init__(self, name):
        """
        Initialize a new Game instance.
        
        Creates a Game object with the specified name and loads additional
        metadata from the JSON configuration file. If the game is not found
        in the configuration, default values are used.
        
        Args:
            name (str): The name of the game to create
        """
        # Set the primary identifier
        self.name = name
        
        # Initialize default values for all properties
        # These will be overridden if found in the JSON file
        self.description = "No description available."
        self.genre = "Unknown"
        self.image_url = None
        self.platforms = []
        
        # Load detailed information from configuration file
        self.load_info_from_json()

    def load_info_from_json(self):
        """
        Load game information from individual JSON configuration files.
        
        Searches for a game-specific JSON file in the games/ directory and
        loads detailed game metadata. The file should be named after the game
        (e.g., "palworld.json", "valheim.json") and contain comprehensive
        game information including server details, system requirements, and
        configuration options.
        
        The JSON file should contain a game object with properties:
        - name: Game name (string)
        - display_name: Formatted display name (string)
        - description: Game description (string)
        - genre: Game genre(s) (string)
        - platforms: Array of platform strings
        - server_info: Server configuration details
        - system_requirements: Hardware requirements
        - features: Array of game features
        - And many other detailed properties
        
        Handles file not found and JSON parsing errors gracefully by printing
        error messages and leaving default values in place.
        """
        try:
            # Determine the path to the individual game JSON file
            # Look in the games/ subdirectory for game-specific files
            script_dir = os.path.dirname(os.path.abspath(__file__))
            games_dir = os.path.join(script_dir, "games")
            
            # Create filename from game name (lowercase, spaces replaced with underscores)
            filename = f"{self.name.lower().replace(' ', '_')}.json"
            json_path = os.path.join(games_dir, filename)
            
            # Load and parse the JSON configuration file
            with open(json_path, "r", encoding='utf-8') as f:
                game_data = json.load(f)
            
            # Update instance properties with loaded data
            self._update_from_json_data(game_data)
                    
        except FileNotFoundError:
            print(f"Warning: {filename} not found in games/ directory for {self.name}")
        except json.JSONDecodeError as e:
            print(f"Error parsing {filename} for {self.name}: {e}")
        except Exception as e:
            print(f"Error loading game info for {self.name}: {e}")

    def _update_from_json_data(self, game_data):
        """
        Update instance properties from loaded JSON data.
        
        Safely extracts and assigns properties from the comprehensive JSON game 
        object, handling missing or malformed data gracefully by keeping default 
        values. This method now supports the enhanced JSON structure with detailed
        game information, server configuration, and system requirements.
        
        Args:
            game_data (dict): Game data object from JSON file
        """
        # Update description - try 'description' first, fall back to 'summary'
        self.description = game_data.get("description", game_data.get("summary", self.description))
        
        # Process genre information - handle both string and array formats
        genre_data = game_data.get("genre")
        if genre_data:
            if isinstance(genre_data, list):
                self.genre = ", ".join(genre_data)
            else:
                self.genre = str(genre_data)
        # If no genre data, keep the default "Unknown"
        
        # Set image path - look for 'image' or 'image_url'
        self.image_url = game_data.get("image", game_data.get("image_url", None))
        
        # Set supported platforms list
        self.platforms = game_data.get("platforms", [])
        
        # Store additional detailed information for potential future use
        # These aren't used in the current UI but provide rich data for expansion
        self.display_name = game_data.get("display_name", self.name)
        self.developer = game_data.get("developer", "Unknown")
        self.publisher = game_data.get("publisher", "Unknown")
        self.release_date = game_data.get("release_date", "Unknown")
        
        # Server-specific information
        server_info = game_data.get("server_info", {})
        self.app_id = server_info.get("app_id", "Unknown")
        self.default_port = server_info.get("default_port", 0)
        self.executable = server_info.get("executable", "Unknown")
        
        # Multiplayer information
        multiplayer_info = game_data.get("multiplayer", {})
        self.max_players = multiplayer_info.get("max_players", 0)
        self.min_players = multiplayer_info.get("min_players", 1)
        
        # Game features
        self.features = game_data.get("features", [])

    def get_display_name(self):
        """
        Get the game's display name.
        
        Returns the formatted display name if available, otherwise falls back
        to the basic name. This allows for games to have different internal
        names versus user-facing display names.
        
        Returns:
            str: The game's display name
        """
        return getattr(self, 'display_name', self.name)

    def get_server_info(self):
        """
        Get server-specific information for this game.
        
        Returns a dictionary containing key server configuration details
        like app ID, port, and executable name.
        
        Returns:
            dict: Server configuration information
        """
        return {
            'app_id': getattr(self, 'app_id', 'Unknown'),
            'default_port': getattr(self, 'default_port', 0),
            'executable': getattr(self, 'executable', 'Unknown'),
            'max_players': getattr(self, 'max_players', 0),
            'min_players': getattr(self, 'min_players', 1)
        }

    def get_multiplayer_info(self):
        """
        Get multiplayer capability information.
        
        Returns details about the game's multiplayer support including
        player limits and gameplay modes.
        
        Returns:
            str: Formatted multiplayer information
        """
        max_players = getattr(self, 'max_players', 0)
        min_players = getattr(self, 'min_players', 1)
        
        if max_players > 1:
            return f"{min_players}-{max_players} players"
        elif max_players == 1:
            return "Single player only"
        else:
            return "Multiplayer support unknown"

    def get_developer_info(self):
        """
        Get developer and publisher information.
        
        Returns formatted information about who developed and published
        the game.
        
        Returns:
            str: Developer and publisher information
        """
        developer = getattr(self, 'developer', 'Unknown')
        publisher = getattr(self, 'publisher', 'Unknown')
        
        if developer == publisher:
            return f"Developed by {developer}"
        else:
            return f"Developed by {developer}, Published by {publisher}"

    def get_genre_display(self):
        """
        Get a formatted genre string for display.
        
        Returns the genre information in a format suitable for UI display.
        Handles the case where no genre information is available.
        
        Returns:
            str: Formatted genre string, or "Unknown" if no genre info
        """
        return self.genre if self.genre and self.genre != "Unknown" else "Genre not specified"

    def get_platforms_display(self):
        """
        Get a formatted platforms string for display.
        
        Converts the platforms list into a readable string format for UI display.
        
        Returns:
            str: Comma-separated platform names, or "Not specified" if none
        """
        if self.platforms:
            return ", ".join(self.platforms)
        return "Platforms not specified"

    def has_image(self):
        """
        Check if the game has an associated image.
        
        Returns:
            bool: True if an image URL is specified, False otherwise
        """
        return self.image_url is not None and self.image_url.strip() != ""

    def __str__(self):
        """
        Return a string representation of the game.
        
        Provides a human-readable summary of the game including its name,
        genre, and description. Useful for debugging and logging.
        
        Returns:
            str: Formatted string representation of the game
        """
        return f"{self.name} ({self.genre}): {self.description}"

    def __repr__(self):
        """
        Return a detailed string representation for debugging.
        
        Provides a more detailed representation showing all key properties,
        useful for development and debugging purposes.
        
        Returns:
            str: Detailed string representation
        """
        return (f"Game(name='{self.name}', genre='{self.genre}', "
                f"platforms={self.platforms}, has_image={self.has_image()})")

