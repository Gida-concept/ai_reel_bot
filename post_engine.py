import requests
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger("post_engine")


class PostEngine:
    """
    Publish videos to social media via SocialBu API
    """

    def __init__(self, config: Dict[str, Any]):
        self.api_key = config['socialbu']['api_key']
        self.api_url = config['socialbu']['api_url']
        self.page_id = config['socialbu']['facebook_page_id']

    def publish_to_facebook(
            self,
            video_path: str,
            title: str,
            description: str
    ) -> Dict[str, Any]:
        """
        Publish video to Facebook

        Args:
            video_path: Path to final video
            title: Post title
            description: Post description

        Returns:
            API response
        """
        try:
            logger.info(f"Publishing '{title}' to Facebook...")

            # Prepare caption with hashtags
            caption = f"{title}\n\n{description}\n\n#PocketFM #Shorts #DramaStory #Reels"

            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }

            # Upload video
            with open(video_path, 'rb') as video_file:
                files = {
                    'video': video_file
                }

                data = {
                    'page_id': self.page_id,
                    'caption': caption,
                    'post_type': 'reel'
                }

                response = requests.post(
                    self.api_url,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=300
                )

                response.raise_for_status()
                result = response.json()

                logger.info(f"✓ Published successfully: {result}")
                return result

        except Exception as e:
            logger.error(f"Error publishing to Facebook: {str(e)}")
            raise