import asyncio
import edge_tts
import os
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger("voice_engine")


class VoiceEngine:
    """
    Generate voice-overs using Edge-TTS
    """

    def __init__(self, config: Dict[str, Any]):
        self.voice = config['edge_tts']['voice']
        self.rate = config['edge_tts']['rate']
        self.pitch = config['edge_tts']['pitch']

    async def _generate_async(self, text: str, output_path: str):
        """
        Async voice generation
        """
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            pitch=self.pitch
        )
        await communicate.save(output_path)

    def generate_voiceover(self, script: str, output_path: str) -> str:
        """
        Generate voice-over from script

        Args:
            script: The narration text
            output_path: Where to save the audio file

        Returns:
            Path to generated audio file
        """
        try:
            logger.info("Generating voice-over...")

            # Run async function
            asyncio.run(self._generate_async(script, output_path))

            if os.path.exists(output_path):
                logger.info(f"✓ Voice-over generated: {output_path}")
                return output_path
            else:
                raise Exception("Voice file not created")

        except Exception as e:
            logger.error(f"Error generating voice-over: {str(e)}")
            raise