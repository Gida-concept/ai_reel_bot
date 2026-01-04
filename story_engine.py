import random
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger("story_engine")


class StoryEngine:
    """
    Manage story generation and theme tracking
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.genres = config['genres']
        self.history_file = "output/story_history.json"
        self.history = self._load_history()

    def _load_history(self) -> Dict:
        """Load story history"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return {"stories": []}
        return {"stories": []}

    def _save_history(self):
        """Save story history"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def get_next_genre(self) -> str:
        """
        Get next genre, rotating through available genres
        """
        today = datetime.now().strftime('%Y-%m-%d')

        # Get genres used today
        used_today = [
            s['genre'] for s in self.history['stories']
            if s['date'] == today
        ]

        # Find unused genres
        available = [g for g in self.genres if g not in used_today]

        if not available:
            # All genres used, pick random
            genre = random.choice(self.genres)
        else:
            # Pick from available
            genre = random.choice(available)

        logger.info(f"Selected genre: {genre}")
        return genre

    def get_recent_themes(self, days: int = 7) -> List[str]:
        """
        Get themes used in recent days to avoid repetition
        """
        recent = self.history['stories'][-days:]
        return [s['theme'] for s in recent if 'theme' in s]

    def record_story(self, story_data: Dict[str, Any]):
        """
        Record generated story in history
        """
        record = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "time": datetime.now().strftime('%H:%M:%S'),
            "genre": story_data.get('genre', 'Unknown'),
            "title": story_data.get('title', ''),
            "theme": story_data.get('theme', ''),
            "video_path": story_data.get('video_path', '')
        }

        self.history['stories'].append(record)
        self._save_history()
        logger.info(f"Story recorded in history")