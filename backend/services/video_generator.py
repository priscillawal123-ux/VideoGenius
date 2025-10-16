"""
Video generation service using MoviePy and text-to-speech.
"""

import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

from backend.storage.cloud_storage import CloudStorageService

logger = logging.getLogger(__name__)


class VideoGeneratorService:
    """Service for generating videos from scripts."""

    def __init__(self, cloud_storage: CloudStorageService):
        """Initialize video generator service.

        Args:
            cloud_storage: Cloud Storage service instance
        """
        self.cloud_storage = cloud_storage
        logger.info("Initialized VideoGeneratorService")

    async def generate_video_from_script(
        self,
        script_data: Dict[str, str],
        job_id: str,
        output_filename: Optional[str] = None,
    ) -> str:
        """Generate video from script data.

        Args:
            script_data: Script data containing title, hook, and full script
            job_id: Job ID for tracking
            output_filename: Optional output filename

        Returns:
            Cloud Storage URL of the generated video

        Raises:
            ValueError: If video generation fails
        """
        if not output_filename:
            output_filename = f"video_{job_id}.mp4"

        try:
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Generate audio from script
                audio_path = temp_path / "script_audio.mp3"
                await self._generate_audio(script_data, audio_path)

                # Create video clips
                video_clips = await self._create_video_clips(script_data, temp_path)

                # Combine clips with audio
                final_video_path = temp_path / "final_video.mp4"
                await self._combine_video_and_audio(
                    video_clips, audio_path, final_video_path
                )

                # Upload to Cloud Storage
                with open(final_video_path, "rb") as video_file:
                    video_url = await self.cloud_storage.upload_file(
                        file_obj=video_file,
                        filename=output_filename,
                        content_type="video/mp4",
                        metadata={
                            "job_id": job_id,
                            "title": script_data.get("title", ""),
                            "duration_seconds": str(
                                await self._get_audio_duration(audio_path)
                            ),
                        },
                    )

                logger.info(f"Video generated and uploaded: {output_filename}")
                return video_url

        except Exception as e:
            logger.error(f"Video generation failed for job {job_id}: {e}")
            raise ValueError(f"Failed to generate video: {e}") from e

    async def _generate_audio(
        self, script_data: Dict[str, str], output_path: Path
    ) -> None:
        """Generate audio from script text.

        Args:
            script_data: Script data
            output_path: Output path for audio file
        """
        # Combine all script text
        full_script = "\n".join(
            [script_data.get("hook", ""), script_data.get("script", "")]
        )

        # Generate speech
        tts = gTTS(text=full_script, lang="en", slow=False)
        tts.save(str(output_path))

        logger.info(f"Audio generated: {output_path}")

    async def _create_video_clips(
        self, script_data: Dict[str, str], temp_path: Path
    ) -> List:
        """Create video clips from script data.

        Args:
            script_data: Script data
            temp_path: Temporary directory path

        Returns:
            List of video clips
        """
        clips = []

        # Create background image
        bg_image_path = temp_path / "background.png"
        await self._create_background_image(script_data, bg_image_path)

        # Hook clip (first 5 seconds)
        hook_text = script_data.get("hook", "")
        hook_clip = await self._create_text_clip(
            hook_text, bg_image_path, duration=5, fontsize=60
        )
        clips.append(hook_clip)

        # Main script clips
        script_text = script_data.get("script", "")
        script_clips = await self._create_script_clips(script_text, bg_image_path)
        clips.extend(script_clips)

        return clips

    async def _create_background_image(
        self, script_data: Dict[str, str], output_path: Path
    ) -> None:
        """Create background image with title.

        Args:
            script_data: Script data
            output_path: Output path for background image
        """
        # Create 1920x1080 image
        img = Image.new("RGB", (1920, 1080), color="#1a1a2e")
        draw = ImageDraw.Draw(img)

        # Try to load a font, fallback to default if not available
        try:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            font = ImageFont.truetype(font_path, 80)
        except Exception:
            font = ImageFont.load_default()

        # Add title
        title = script_data.get("title", "Video Genius")
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]

        x = (1920 - text_width) // 2
        y = 100

        # Add text with shadow effect
        shadow_offset = 2
        shadow_pos = (x + shadow_offset, y + shadow_offset)
        draw.text(shadow_pos, title, font=font, fill="#000000")
        draw.text((x, y), title, font=font, fill="#ffffff")

        img.save(str(output_path))
        logger.info(f"Background image created: {output_path}")

    async def _create_text_clip(
        self, text: str, bg_image_path: Path, duration: float, fontsize: int = 50
    ) -> ImageClip:
        """Create a text clip with background.

        Args:
            text: Text to display
            bg_image_path: Background image path
            duration: Clip duration in seconds
            fontsize: Font size

        Returns:
            MoviePy clip
        """
        # Create background clip
        bg_clip = ImageClip(str(bg_image_path)).set_duration(duration)

        return bg_clip

    async def _create_script_clips(self, script_text: str, bg_image_path: Path) -> List:
        """Create clips for script text.

        Args:
            script_text: Full script text
            bg_image_path: Background image path

        Returns:
            List of video clips
        """
        clips = []

        # Split script into segments (roughly 10 seconds per segment)
        words = script_text.split()
        words_per_segment = 50  # Adjust based on speaking speed

        for i in range(0, len(words), words_per_segment):
            segment_words = words[i : i + words_per_segment]
            segment_text = " ".join(segment_words)

            # Estimate duration based on word count
            # (roughly 150 words per minute)
            duration = max(3, len(segment_words) * 60 / 150)

            clip = await self._create_text_clip(
                segment_text, bg_image_path, duration, fontsize=40
            )
            clips.append(clip)

        return clips

    async def _combine_video_and_audio(
        self, video_clips: List, audio_path: Path, output_path: Path
    ) -> None:
        """Combine video clips with audio.

        Args:
            video_clips: List of video clips
            audio_path: Audio file path
            output_path: Output video path
        """
        # Concatenate video clips
        if len(video_clips) == 1:
            video = video_clips[0]
        else:
            video = concatenate_videoclips(video_clips, method="compose")

        # Load audio
        audio = AudioFileClip(str(audio_path))

        # Set audio to video
        final_video = video.set_audio(audio)

        # Write final video
        temp_audio = str(output_path.with_suffix(".m4a"))
        final_video.write_videofile(
            str(output_path),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=temp_audio,
            remove_temp=True,
            verbose=False,
            logger=None,
        )

        logger.info(f"Video created: {output_path}")

    async def _get_audio_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds.

        Args:
            audio_path: Audio file path

        Returns:
            Duration in seconds
        """
        audio = AudioFileClip(str(audio_path))
        duration = float(audio.duration)
        audio.close()
        return duration
