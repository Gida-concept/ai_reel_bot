import subprocess
import os
from typing import Optional
from utils.logger import setup_logger

logger = setup_logger("ffmpeg_engine")


class FFmpegEngine:
    """
    Video editing and composition using FFmpeg
    """

    def __init__(self, config):
        self.resolution = config['video']['resolution']
        self.fps = config['video']['fps']
        self.duration = config['video']['duration']

    def compose_final_video(
            self,
            video_path: str,
            audio_path: str,
            music_path: Optional[str],
            srt_path: str,
            output_path: str
    ) -> str:
        """
        Compose final video with all elements

        Args:
            video_path: Raw video file
            audio_path: Voice-over audio
            music_path: Background music (optional)
            srt_path: Subtitle file
            output_path: Final output path

        Returns:
            Path to final video
        """
        try:
            logger.info("Composing final video with FFmpeg...")

            width, height = self.resolution.split('x')

            # Build FFmpeg command
            # Complex filter for: subtitles + audio mixing + effects

            filter_complex = []

            # Add subtle zoom/pan effect
            filter_complex.append(
                f"[0:v]scale={int(width) * 1.1}:{int(height) * 1.1},"
                f"zoompan=z='min(zoom+0.0005,1.1)':d={self.fps * self.duration}:s={width}x{height},"
                f"format=yuv420p[v]"
            )

            # Add subtitles with styling
            subtitle_style = (
                "FontName=Arial,FontSize=28,PrimaryColour=&H00FFFFFF,"
                "OutlineColour=&H00000000,BorderStyle=3,Outline=2,"
                "Shadow=1,Alignment=2,MarginV=80,Bold=1"
            )

            filter_complex.append(
                f"[v]subtitles='{srt_path}':force_style='{subtitle_style}'[vout]"
            )

            # Audio mixing
            if music_path and os.path.exists(music_path):
                # Mix voice-over with background music
                audio_filter = "[1:a]volume=1.0[voice];[2:a]volume=0.3[music];[voice][music]amix=inputs=2:duration=first[aout]"

                cmd = [
                    'ffmpeg',
                    '-i', video_path,
                    '-i', audio_path,
                    '-i', music_path,
                    '-filter_complex', ';'.join(filter_complex + [audio_filter]),
                    '-map', '[vout]',
                    '-map', '[aout]',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-t', str(self.duration),
                    '-y',
                    output_path
                ]
            else:
                # Just voice-over
                cmd = [
                    'ffmpeg',
                    '-i', video_path,
                    '-i', audio_path,
                    '-filter_complex', ';'.join(filter_complex),
                    '-map', '[vout]',
                    '-map', '1:a',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-t', str(self.duration),
                    '-y',
                    output_path
                ]

            logger.info(f"Running FFmpeg command...")
            logger.debug(f"Command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise Exception(f"FFmpeg failed with code {result.returncode}")

            if os.path.exists(output_path):
                logger.info(f"✓ Final video created: {output_path}")
                return output_path
            else:
                raise Exception("Output video not created")

        except Exception as e:
            logger.error(f"Error composing video: {str(e)}")
            raise

    def add_intro_outro(self, video_path: str, output_path: str) -> str:
        """
        Add fade in/out effects
        """
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', 'fade=t=in:st=0:d=0.5,fade=t=out:st=29.5:d=0.5',
                '-c:a', 'copy',
                '-y',
                output_path
            ]

            subprocess.run(cmd, check=True, timeout=120)
            return output_path

        except Exception as e:
            logger.error(f"Error adding intro/outro: {str(e)}")
            return video_path