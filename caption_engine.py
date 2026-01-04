import re
from typing import List, Dict
from utils.logger import setup_logger

logger = setup_logger("caption_engine")


class CaptionEngine:
    """
    Generate SRT captions for videos
    """

    def __init__(self):
        pass

    def generate_srt(self, script: str, output_path: str, duration: int = 30) -> str:
        """
        Generate SRT subtitle file from script

        Args:
            script: The narration text
            output_path: Where to save the SRT file
            duration: Total video duration in seconds

        Returns:
            Path to SRT file
        """
        try:
            logger.info("Generating captions...")

            # Split script into chunks (every 3-5 words)
            words = script.split()
            chunks = []

            chunk_size = 4
            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i + chunk_size])
                chunks.append(chunk)

            # Calculate timing
            time_per_chunk = duration / len(chunks)

            srt_content = []
            for i, chunk in enumerate(chunks):
                start_time = i * time_per_chunk
                end_time = (i + 1) * time_per_chunk

                srt_content.append(f"{i + 1}")
                srt_content.append(
                    f"{self._format_time(start_time)} --> {self._format_time(end_time)}"
                )
                srt_content.append(chunk)
                srt_content.append("")

            # Write SRT file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(srt_content))

            logger.info(f"✓ Captions generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error generating captions: {str(e)}")
            raise

    def _format_time(self, seconds: float) -> str:
        """
        Format seconds to SRT time format (HH:MM:SS,mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"