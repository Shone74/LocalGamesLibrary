import json
import os
from typing import List, Dict, Any
from models.game import Game

class JsonStorage: 
    def __init__(self, file_path: str = "data/games.json"): 
        self.file_path = file_path
        self.settings_path = os.path.join(os.path.dirname(file_path), "settings.json")
        self.last_error = ""
        self.ensure_data_directory()
    
    def ensure_data_directory(self): 
        """Ensure the data directory exists"""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory): 
            os.makedirs(directory)
    
    def save_games(self, games: List[Game]) -> bool: 
        """Save games to JSON file"""
        try: 
            data = [game.to_dict() for game in games]
            with open(self.file_path, 'w', encoding='utf-8') as f: 
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.last_error = ""
            return True
        except Exception as e: 
            self.last_error = f"Could not save the game library: {e}"
            print(self.last_error)
            return False
    
    def load_games(self) -> List[Game]: 
        """Load games from JSON file"""
        try: 
            if not os.path.exists(self.file_path): 
                return []
            
            with open(self.file_path, 'r', encoding='utf-8') as f: 
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("the root value must be a list of games")
            self.last_error = ""
            return [Game.from_dict(game_data) for game_data in data]
        except Exception as e: 
            self.last_error = f"Could not load the game library: {e}"
            print(self.last_error)
            return []

    def load_settings(self) -> Dict[str, Any]:
        """Load UI preferences, returning safe defaults for missing/corrupt files."""
        defaults = {
            "theme": "Dark",
            "default_view": "All Games",
            "confirm_delete": True,
            "launch_behavior": "Keep library open",
        }
        try:
            if not os.path.exists(self.settings_path):
                return defaults
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            if not isinstance(saved, dict):
                raise ValueError("settings must be an object")
            return {**defaults, **saved}
        except Exception as e:
            self.last_error = f"Could not load settings: {e}"
            print(self.last_error)
            return defaults

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save UI preferences separately from the game library."""
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            self.last_error = ""
            return True
        except Exception as e:
            self.last_error = f"Could not save settings: {e}"
            print(self.last_error)
            return False
