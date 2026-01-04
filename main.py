import os
import sys
import yaml
import traceback
from datetime import datetime
from pathlib import Path

from utils.logger import setup_logger
from groc_client import GrocClient
from sora_client import SoraClient
from voice_engine import VoiceEngine
from music_engine import MusicEngine
from caption_engine import CaptionEngine
from ffmpeg_engine import FFmpegEngine
from post_engine import PostEngine
from story_engine import StoryEngine

logger = setup_logger("main")


class ReelAutomationBot:
    """
    Main orchestrator for AI Reel Automation
    """

    def __init__(self, config_path: str = "settings.yaml"):
        logger.info("=" * 60)
        logger.info("AI Reel Automation Bot Starting")
        logger.info("=" * 60)

        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Create output directories
        self._setup_directories()

        # Initialize components
        self.groc = GrocClient(self.config)
        self.sora = SoraClient(self.config)
        self.voice = VoiceEngine(self.config)
        self.music = MusicEngine(self.config)
        self.captions = CaptionEngine()
        self.ffmpeg = FFmpegEngine(self.config)
        self.publisher = PostEngine(self.config)
        self.story_engine = StoryEngine(self.config)

        logger.info("✓ All components initialized")

    def _setup_directories(self):
        """Create necessary directories"""
        for path in self.config['paths'].values():
            Path(path).mkdir(parents=True, exist_ok=True)

    def generate_reel(self) -> Dict:
        """
        Complete pipeline to generate one reel

        Returns:
            Dict with generation results
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        try:
            logger.info("\n" + "=" * 60)
            logger.info("STARTING NEW REEL GENERATION")
            logger.info("=" * 60)

            # Step 1: Select genre and generate story
            genre = self.story_engine.get_next_genre()
            recent_themes = self.story_engine.get_recent_themes()

            story_data = self.groc.generate_story_script(genre, recent_themes)
            story_data['genre'] = genre

            logger.info(f"\n📖 Story: {story_data['title']}")
            logger.info(f"Genre: {genre}")
            logger.info(f"Theme: {story_data['theme']}")

            # Step 2: Generate video with Sora
            raw_video_path = os.path.join(
                self.config['paths']['raw_videos'],
                f"raw_{timestamp}.mp4"
            )

            self.sora.generate_video(story_data['visual_prompt'], raw_video_path)

            # Step 3: Generate voice-over
            voice_path = os.path.join(
                self.config['paths']['voice'],
                f"voice_{timestamp}.mp3"
            )

            self.voice.generate_voiceover(story_data['script'], voice_path)

            # Step 4: Get background music
            music_path = os.path.join(
                self.config['paths']['music'],
                f"music_{timestamp}.mp3"
            )

            music_file = self.music.get_background_music(genre, music_path)

            # Step 5: Generate captions
            srt_path = os.path.join(
                self.config['paths']['voice'],
                f"captions_{timestamp}.srt"
            )

            self.captions.generate_srt(
                story_data['script'],
                srt_path,
                self.config['video']['duration']
            )

            # Step 6: Compose final video
            temp_video_path = os.path.join(
                self.config['paths']['final_videos'],
                f"temp_{timestamp}.mp4"
            )

            self.ffmpeg.compose_final_video(
                raw_video_path,
                voice_path,
                music_file,
                srt_path,
                temp_video_path
            )

            # Step 7: Add fade effects
            final_video_path = os.path.join(
                self.config['paths']['final_videos'],
                f"final_{timestamp}.mp4"
            )

            self.ffmpeg.add_intro_outro(temp_video_path, final_video_path)

            # Step 8: Publish to social media
            self.publisher.publish_to_facebook(
                final_video_path,
                story_data['title'],
                story_data['script'][:100] + "..."
            )

            # Record in history
            story_data['video_path'] = final_video_path
            self.story_engine.record_story(story_data)

            logger.info("\n" + "=" * 60)
            logger.info("✓ REEL GENERATION COMPLETE")
            logger.info("=" * 60)

            return {
                "success": True,
                "video_path": final_video_path,
                "title": story_data['title'],
                "genre": genre
            }

        except Exception as e:
            logger.error(f"\n❌ REEL GENERATION FAILED")
            logger.error(f"Error: {str(e)}")
            logger.error(traceback.format_exc())

            return {
                "success": False,
                "error": str(e)
            }


def main():
    """Main entry point"""
    try:
        bot = ReelAutomationBot()
        result = bot.generate_reel()

        if result['success']:
            logger.info(f"\n✅ SUCCESS: {result['title']}")
            sys.exit(0)
        else:
            logger.error(f"\n❌ FAILED: {result['error']}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()