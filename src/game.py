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
        Load game information from the JSON configuration file.
        
        Searches for a game_info.json file in the same directory as this script
        and attempts to find matching game data by name (case-insensitive).
        If found, updates the instance properties with the loaded data.
        
        The JSON file should contain an array of game objects with properties:
        - name: Game name (string)
        - summary: Game description (string)
        - genres: Array of genre strings
        - image: Relative path to image file (string)
        - platforms: Array of platform strings
        
        Handles file not found and JSON parsing errors gracefully by printing
        error messages and leaving default values in place.
        """
        try:
            # Determine the path to the game_info.json file
            # Look in the same directory as this script file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(script_dir, "game_info.json")
            
            # Load and parse the JSON configuration file
            with open(json_path, "r") as f:
                game_list = json.load(f)
            
            # Search for this game in the loaded data
            for game in game_list:
                # Case-insensitive name matching for flexibility
                if game.get("name", "").lower() == self.name.lower():
                    # Update instance properties with loaded data
                    self._update_from_json_data(game)
                    break  # Stop searching once we find a match
                    
        except FileNotFoundError:
            print(f"Warning: game_info.json not found for {self.name}")
        except json.JSONDecodeError as e:
            print(f"Error parsing game_info.json for {self.name}: {e}")
        except Exception as e:
            print(f"Error loading game info for {self.name}: {e}")

    def _update_from_json_data(self, game_data):
        """
        Update instance properties from loaded JSON data.
        
        Safely extracts and assigns properties from the JSON game object,
        handling missing or malformed data gracefully by keeping default values.
        
        Args:
            game_data (dict): Game data object from JSON file
        """
        # Update description/summary
        self.description = game_data.get("summary", self.description)
        
        # Process genre information
        # Genres may be a list that needs to be joined into a string
        genres = game_data.get("genres", [])
        if genres:
            self.genre = ", ".join(genres)
        # If no genres or empty list, keep the default "Unknown"
        
        # Set image path (may be None if not specified)
        self.image_url = game_data.get("image", None)
        
        # Set supported platforms list
        self.platforms = game_data.get("platforms", [])

    def get_display_name(self):
        """
        Get the game's display name.
        
        Returns the name formatted for display in the UI. Currently just
        returns the name as-is, but this method allows for future formatting
        changes without affecting the rest of the codebase.
        
        Returns:
            str: The game's display name
        """
        return self.name

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

