from typing import List, Optional
from models.game import Game
from storage.json_storage import JsonStorage

class GameLibrary: 
    def __init__(self, storage: JsonStorage): 
        self.storage = storage
        self.games: List[Game] = self.storage.load_games()
    
    def add_game(self, game: Game) -> bool: 
        """Add a new game to the library"""
        # Check if game already exists
        if self.get_game_by_executable(game.executable_path): 
            return False
        
        self.games.append(game)
        if self.save_library():
            return True
        self.games.pop()
        return False
    
    def remove_game(self, game_id: str) -> bool: 
        """Remove a game from the library"""
        game = self.get_game_by_id(game_id)
        if game: 
            index = self.games.index(game)
            self.games.pop(index)
            if self.save_library():
                return True
            self.games.insert(index, game)
        return False
    
    def update_game(self, game_id: str, updated_game: Game) -> bool: 
        """Update an existing game"""
        game = self.get_game_by_id(game_id)
        if game: 
            # Replace the game in the list
            index = self.games.index(game)
            self.games[index] = updated_game
            if self.save_library():
                return True
            self.games[index] = game
        return False
    
    def get_game_by_id(self, game_id: str) -> Optional[Game]: 
        """Get a game by its ID"""
        for game in self.games: 
            if game.id == game_id: 
                return game
        return None
    
    def get_game_by_executable(self, executable_path: str) -> Optional[Game]: 
        """Get a game by its executable path"""
        for game in self.games: 
            if game.executable_path == executable_path: 
                return game
        return None
    
    def get_all_games(self) -> List[Game]: 
        """Get all games"""
        return self.games
    
    def get_favorite_games(self) -> List[Game]: 
        """Get favorite games"""
        return [game for game in self.games if game.is_favorite]
    
    def save_library(self) -> bool: 
        """Save the library to storage"""
        return self.storage.save_games(self.games)
