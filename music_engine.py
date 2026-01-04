import requests
import random
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger("music_engine")


class MusicEngine:
    """
    Fetch background music from Pixabay
    """

    def __init__(self, config: Dict[str, Any]):
        self.api_key = config['pixabay']['api_key']
        self.api_url = config['pixabay']['api_url']

    def get_background_music(self, genre: str, output_path: str) -> str:
        """
        Fetch appropriate background music

        Args:
            genre: Story genre to match music mood
            output_path: Where to save the music file

        Returns:
            Path to downloaded music file
        """
        try:
            # Map genre to music categories
            mood_map = {
                "Romance": "emotional",
                "CEO/Billionaire": "corporate",
                "Betrayal": "dark",
                "Heartbreak": "sad",
                "Rise from Poverty": "inspiring",
                "Power & Secrets": "suspense"
            }

            mood = mood_map.get(genre, "dramatic")

            logger.info(f"Fetching {mood} background music...")

            params = {
                "key": self.api_key,
                "q": mood,
                "per_page": 20
            }

            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('hits'):
                # Pick random track
                track = random.choice(data['hits'])
                audio_url = track['videos']['medium']['url']

                logger.info(f"Downloading music: {track.get('tags', 'Unknown')}")

                # Download
                audio_response = requests.get(audio_url, timeout=60)
                audio_response.raise_for_status()

                with open(output_path, 'wb') as f:
                    f.write(audio_response.content)

                logger.info(f"✓ Music downloaded: {output_path}")
                return output_path
            else:
                logger.warning("No music found, using silent background")
                return None

        except Exception as e:
            logger.error(f"Error fetching music: {str(e)}")
            return None