from dataclasses import dataclass, asdict
from typing import Dict, Any
from datetime import datetime
import json

@dataclass
class Game: 
    id: str
    title: str
    executable_path: str
    install_dir: str
    genre: str = ""
    description: str = ""
    developer: str = ""
    publisher: str = ""
    release_date: str = ""
    cover_path: str = ""
    is_favorite: bool = False
    play_count: int = 0
    last_played: str = ""
    
    def to_dict(self) -> Dict[str, Any]: 
        """Convert game object to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Game': 
        """Create a game from saved data, tolerating older library entries."""
        known_fields = cls.__dataclass_fields__
        saved_fields = {key: value for key, value in data.items() if key in known_fields}
        return cls(**saved_fields)
    
    def increment_play_count(self): 
        """Increment play count and update last played time"""
        self.play_count += 1
        self.last_played = datetime.now().isoformat()
