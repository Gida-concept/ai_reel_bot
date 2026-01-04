import requests
import time
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger("sora_client")


class SoraClient:
    """
    Client for Sora 2 video generation via RapidAPI
    """

    def __init__(self, config: Dict[str, Any]):
        self.api_key = config['sora']['key']
        self.host = config['sora']['host']
        self.api_url = config['sora']['api_url']
        self.max_retries = config['video']['max_retries']

    def generate_video(self, visual_prompt: str, output_path: str) -> str:
        """
        Generate video using Sora 2 API

        Args:
            visual_prompt: Detailed scene description
            output_path: Where to save the video

        Returns:
            Path to downloaded video file
        """
        try:
            # Enhance prompt for Pocket-FM style
            enhanced_prompt = f"""Pocket-FM style cinematic short video: {visual_prompt}

Style requirements:
- Vertical 9:16 portrait format
- Cinematic color grading
- Dramatic lighting
- Emotional atmosphere
- Professional film quality
- Smooth camera movement
- 30 seconds duration
- High detail and realism"""

            headers = {
                "X-Rapidapi-Key": self.api_key,
                "X-Rapidapi-Host": self.host,
                "Content-Type": "application/json"
            }

            payload = {
                "input": enhanced_prompt,
                "model": "Sora 2",
                "videoCount": "1",
                "type": "text/video",
                "resolution": "portrait"
            }

            logger.info("Requesting video generation from Sora 2...")

            for attempt in range(self.max_retries):
                try:
                    response = requests.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=300  # 5 minutes timeout
                    )
                    response.raise_for_status()

                    result = response.json()
                    logger.info(f"Sora API Response: {result}")

                    # Handle different response formats
                    video_url = None

                    if isinstance(result, dict):
                        # Try different possible keys
                        video_url = (result.get('video_url') or
                                     result.get('url') or
                                     result.get('output') or
                                     result.get('data', {}).get('url'))

                        # If status is processing, wait and poll
                        if result.get('status') == 'processing':
                            task_id = result.get('task_id') or result.get('id')
                            if task_id:
                                video_url = self._poll_video_status(task_id, headers)

                    if video_url:
                        logger.info(f"Video URL received: {video_url}")
                        return self._download_video(video_url, output_path)
                    else:
                        logger.warning(f"Attempt {attempt + 1}: No video URL in response")

                except requests.exceptions.RequestException as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < self.max_retries - 1:
                        time.sleep(10)
                    else:
                        raise

            raise Exception("Failed to generate video after all retries")

        except Exception as e:
            logger.error(f"Error in video generation: {str(e)}")
            raise

    def _poll_video_status(self, task_id: str, headers: Dict, max_wait: int = 300) -> str:
        """
        Poll for video generation completion
        """
        logger.info(f"Polling for video completion (task: {task_id})...")
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                # Adjust this endpoint based on actual API documentation
                status_url = f"{self.api_url}/{task_id}"
                response = requests.get(status_url, headers=headers, timeout=30)
                response.raise_for_status()

                result = response.json()
                status = result.get('status')

                if status == 'completed':
                    return result.get('video_url') or result.get('url')
                elif status == 'failed':
                    raise Exception(f"Video generation failed: {result.get('error')}")

                logger.info(f"Status: {status}, waiting...")
                time.sleep(10)

            except Exception as e:
                logger.warning(f"Polling error: {str(e)}")
                time.sleep(10)

        raise Exception("Video generation timeout")

    def _download_video(self, video_url: str, output_path: str) -> str:
        """
        Download video from URL
        """
        logger.info(f"Downloading video to {output_path}...")

        response = requests.get(video_url, stream=True, timeout=120)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"✓ Video downloaded: {output_path}")
        return output_path