import requests

import json

class Game:
    def __init__(self, name):
        self.name = name
        self.description = "No description available."
        self.genre = "Unknown"
        self.image_url = None
        self.platforms = []
        self.load_info_from_json()

    def load_info_from_json(self):
        try:
            with open("game_info.json", "r") as f:
                game_list = json.load(f)
            for game in game_list:
                if game.get("name", "").lower() == self.name.lower():
                    self.description = game.get("summary", self.description)
                    genres = game.get("genres", [])
                    self.genre = ", ".join(genres) if genres else self.genre
                    self.image_url = game.get("image", None)
                    self.platforms = game.get("platforms", [])
                    break
        except Exception as e:
            print(f"Error loading game info for {self.name}: {e}")

    def __str__(self):
        return f"{self.name} ({self.genre}): {self.description}"

