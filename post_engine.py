import requests
import os
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger("post_engine")

class PostEngine:
    """
    Publish videos to social media via SocialBu API
    """
    def __init__(self, config: Dict[str, Any]):
        self.bearer_token = config['socialbu']['bearer_token']
        self.api_url = config['socialbu']['api_url']
        self.account_id = config['socialbu'].get('account_id', '')
    
    def publish_to_facebook(
        self,
        video_path: str,
        title: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Publish video to Facebook via SocialBu
        
        Args:
            video_path: Path to final video
            title: Post title
            description: Post description
            
        Returns:
            API response
        """
        try:
            logger.info(f"Publishing '{title}' to Facebook via SocialBu...")
            
            # Prepare caption with hashtags
            caption = f"{title}\n\n{description}\n\n#PocketFM #Shorts #DramaStory #Reels #Viral"
            
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Accept": "application/json"
            }
            
            # Check if video exists
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            file_size_mb = os.path.getsize(video_path) / (1024*1024)
            logger.info(f"Video file size: {file_size_mb:.2f} MB")
            
            # Prepare multipart form data
            with open(video_path, 'rb') as video_file:
                files = {
                    'media[]': (os.path.basename(video_path), video_file, 'video/mp4')
                }
                
                data = {
                    'accounts[]': self.account_id,
                    'caption': caption,
                    'post_type': 'reel',
                    'publish_now': '1'
                }
                
                logger.info(f"Uploading to SocialBu (Account ID: {self.account_id})...")
                logger.info(f"API URL: {self.api_url}")
                
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=600  # 10 minute timeout for large video uploads
                )
                
                logger.info(f"Response Status: {response.status_code}")
                
                # Log response for debugging
                try:
                    result = response.json()
                    logger.info(f"Response JSON: {result}")
                except:
                    logger.info(f"Response Text: {response.text}")
                    result = {"status": response.status_code, "text": response.text}
                
                response.raise_for_status()
                
                logger.info(f"✓ Successfully published to Facebook!")
                
                return result
                
        except FileNotFoundError as e:
            logger.error(f"File error: {str(e)}")
            raise
        except requests.exceptions.Timeout:
            logger.error("Upload timeout - video might be too large or connection is slow")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Status Code: {e.response.status_code}")
                logger.error(f"Response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
