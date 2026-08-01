import os
import subprocess
from models.game import Game
from services.game_library import GameLibrary

class GameLauncher: 
    def __init__(self, game_library: GameLibrary): 
        self.game_library = game_library
    
    def launch_game(self, game: Game) -> bool: 
        """Launch a game executable"""
        # Check if executable exists
        if not os.path.exists(game.executable_path): 
            print(f"Game executable not found: {game.executable_path}")
            return False
        
        try: 
            # Launch the game
            subprocess.Popen([game.executable_path], cwd=game.install_dir)
            
            # Update play count and last played
            game.increment_play_count()
            
            # Save changes
            self.game_library.update_game(game.id, game)
            
            return True
        except Exception as e: 
            print(f"Error launching game: {e}")
            return False