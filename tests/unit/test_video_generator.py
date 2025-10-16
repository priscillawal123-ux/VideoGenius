"""
Unit tests for VideoGeneratorService.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.video_generator import VideoGeneratorService
from backend.storage.cloud_storage import CloudStorageService


class TestVideoGeneratorService:
    """Test cases for VideoGeneratorService."""

    @pytest.fixture
    def cloud_storage_mock(self):
        """Mock CloudStorageService."""
        return MagicMock(spec=CloudStorageService)

    @pytest.fixture
    def service(self, cloud_storage_mock):
        """Create service instance with mocked dependencies."""
        return VideoGeneratorService(cloud_storage_mock)

    @pytest.mark.asyncio
    async def test_generate_video_from_script_success(
        self, service, cloud_storage_mock
    ):
        """Test successful video generation from script."""
        # Given
        script_data = {
            "title": "Test Video",
            "hook": "Welcome to our test!",
            "script": "This is a test script for video generation.",
        }
        job_id = "test-job-123"
        expected_url = "https://storage.googleapis.com/bucket/video_test-job-123.mp4"

        cloud_storage_mock.upload_file.return_value = expected_url

        # Mock all the internal methods
        with patch.object(
            service, "_generate_audio", new_callable=AsyncMock
        ) as mock_audio:
            with patch.object(
                service, "_create_video_clips", new_callable=AsyncMock
            ) as mock_clips:
                with patch.object(
                    service, "_combine_video_and_audio", new_callable=AsyncMock
                ) as mock_combine:
                    with patch.object(
                        service, "_get_audio_duration", new_callable=AsyncMock
                    ) as mock_duration:
                        with patch("builtins.open", MagicMock()) as mock_open:
                            with patch(
                                "backend.services.video_generator.tempfile.TemporaryDirectory"
                            ) as mock_temp:
                                mock_temp.return_value.__enter__.return_value = (
                                    "/tmp/test"
                                )
                                mock_temp.return_value.__exit__.return_value = None
                                mock_duration.return_value = 10.5

                                # When
                                result = await service.generate_video_from_script(
                                    script_data, job_id
                                )

                                # Then
                                assert result == expected_url
                                cloud_storage_mock.upload_file.assert_called_once()
                                call_args = cloud_storage_mock.upload_file.call_args
                                assert (
                                    call_args[1]["filename"] == "video_test-job-123.mp4"
                                )
                                assert call_args[1]["content_type"] == "video/mp4"
                                assert call_args[1]["metadata"]["job_id"] == job_id
                                assert call_args[1]["metadata"]["title"] == "Test Video"

    @pytest.mark.asyncio
    async def test_generate_video_from_script_custom_filename(
        self, service, cloud_storage_mock
    ):
        """Test video generation with custom filename."""
        # Given
        script_data = {"title": "Test", "hook": "Hook", "script": "Script"}
        job_id = "test-job"
        custom_filename = "custom_video.mp4"
        expected_url = "https://storage.googleapis.com/bucket/custom_video.mp4"

        cloud_storage_mock.upload_file.return_value = expected_url

        # Mock internal methods
        with patch.object(service, "_generate_audio", new_callable=AsyncMock):
            with patch.object(service, "_create_video_clips", new_callable=AsyncMock):
                with patch.object(
                    service, "_combine_video_and_audio", new_callable=AsyncMock
                ):
                    with patch.object(
                        service, "_get_audio_duration", new_callable=AsyncMock
                    ) as mock_duration:
                        with patch("builtins.open", MagicMock()):
                            with patch(
                                "backend.services.video_generator.tempfile.TemporaryDirectory"
                            ) as mock_temp:
                                mock_temp.return_value.__enter__.return_value = (
                                    "/tmp/test"
                                )
                                mock_temp.return_value.__exit__.return_value = None
                                mock_duration.return_value = 5.0

                                # When
                                result = await service.generate_video_from_script(
                                    script_data, job_id, custom_filename
                                )

                                # Then
                                assert result == expected_url
                                cloud_storage_mock.upload_file.assert_called_once()
                                assert (
                                    cloud_storage_mock.upload_file.call_args[1][
                                        "filename"
                                    ]
                                    == custom_filename
                                )

    @pytest.mark.asyncio
    async def test_generate_video_from_script_failure(
        self, service, cloud_storage_mock
    ):
        """Test video generation failure."""
        script_data = {"title": "Test", "hook": "Hook", "script": "Script"}
        job_id = "test-job"

        # Mock to raise exception
        with patch.object(
            service, "_generate_audio", new_callable=AsyncMock
        ) as mock_audio:
            mock_audio.side_effect = Exception("Audio generation failed")

            with patch("backend.services.video_generator.tempfile.TemporaryDirectory"):
                # When/Then
                with pytest.raises(
                    ValueError,
                    match="Failed to generate video: Audio generation failed",
                ):
                    await service.generate_video_from_script(script_data, job_id)

    @pytest.mark.asyncio
    async def test_generate_audio(self, service):
        """Test audio generation from script."""
        script_data = {"hook": "Welcome!", "script": "This is the main content."}

        with patch("backend.services.video_generator.gTTS") as mock_gtts:
            mock_tts_instance = MagicMock()
            mock_gtts.return_value = mock_tts_instance

            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = Path(temp_dir) / "test_audio.mp3"

                # When
                await service._generate_audio(script_data, output_path)

                # Then
                mock_gtts.assert_called_once_with(
                    text="Welcome!\nThis is the main content.", lang="en", slow=False
                )
                mock_tts_instance.save.assert_called_once_with(str(output_path))

    @pytest.mark.asyncio
    async def test_create_video_clips(self, service):
        """Test video clips creation."""
        script_data = {
            "title": "Test Title",
            "hook": "Test hook",
            "script": "This is a longer script that should be split into multiple segments for testing purposes.",
        }

        with patch.object(
            service, "_create_background_image", new_callable=AsyncMock
        ) as mock_bg:
            with patch.object(
                service, "_create_text_clip", new_callable=AsyncMock
            ) as mock_text_clip:
                with patch.object(
                    service, "_create_script_clips", new_callable=AsyncMock
                ) as mock_script_clips:
                    mock_bg.return_value = None
                    mock_text_clip.return_value = MagicMock()
                    mock_script_clips.return_value = [MagicMock(), MagicMock()]

                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir)
                        bg_path = temp_path / "background.png"

                        # When
                        clips = await service._create_video_clips(
                            script_data, temp_path
                        )

                        # Then
                        mock_bg.assert_called_once_with(script_data, bg_path)
                        mock_text_clip.assert_called_once_with(
                            "Test hook", bg_path, duration=5, fontsize=60
                        )
                        mock_script_clips.assert_called_once_with(
                            "This is a longer script that should be split into multiple segments for testing purposes.",
                            bg_path,
                        )
                        assert len(clips) == 3  # hook clip + 2 script clips

    @pytest.mark.asyncio
    async def test_create_background_image(self, service):
        """Test background image creation."""
        script_data = {"title": "Test Video Title"}

        with patch("backend.services.video_generator.Image") as mock_image:
            with patch("backend.services.video_generator.ImageDraw") as mock_draw:
                with patch("backend.services.video_generator.ImageFont") as mock_font:
                    mock_img = MagicMock()
                    mock_image.new.return_value = mock_img
                    mock_draw_instance = MagicMock()
                    mock_draw.return_value = mock_draw_instance
                    mock_font_instance = MagicMock()
                    mock_font.truetype.return_value = mock_font_instance

                    with tempfile.TemporaryDirectory() as temp_dir:
                        output_path = Path(temp_dir) / "background.png"

                        # When
                        await service._create_background_image(script_data, output_path)

                        # Then
                        mock_image.new.assert_called_once_with(
                            "RGB", (1920, 1080), color="#1a1a2e"
                        )
                        mock_img.save.assert_called_once_with(str(output_path))

    @pytest.mark.asyncio
    async def test_create_text_clip(self, service):
        """Test text clip creation."""
        with patch("backend.services.video_generator.ImageClip") as mock_image_clip:
            mock_clip = MagicMock()
            mock_image_clip.return_value = mock_clip
            mock_clip.set_duration.return_value = mock_clip

            with tempfile.TemporaryDirectory() as temp_dir:
                bg_path = Path(temp_dir) / "bg.png"

                # When
                result = await service._create_text_clip("Test text", bg_path, 5.0, 50)

                # Then
                mock_image_clip.assert_called_once_with(str(bg_path))
                mock_clip.set_duration.assert_called_once_with(5.0)
                assert result == mock_clip

    @pytest.mark.asyncio
    async def test_create_script_clips(self, service):
        """Test script clips creation."""
        script_text = "This is a test script with enough words to create multiple segments for testing."

        with patch.object(
            service, "_create_text_clip", new_callable=AsyncMock
        ) as mock_text_clip:
            mock_clip = MagicMock()
            mock_text_clip.return_value = mock_clip

            with tempfile.TemporaryDirectory() as temp_dir:
                bg_path = Path(temp_dir) / "bg.png"

                # When
                clips = await service._create_script_clips(script_text, bg_path)

                # Then
                # Should create clips for segments
                assert len(clips) > 0
                assert all(clip == mock_clip for clip in clips)

    @pytest.mark.asyncio
    async def test_combine_video_and_audio(self, service):
        """Test video and audio combination."""
        video_clips = [MagicMock(), MagicMock()]

        with patch(
            "backend.services.video_generator.concatenate_videoclips"
        ) as mock_concat:
            with patch(
                "backend.services.video_generator.AudioFileClip"
            ) as mock_audio_clip:
                with patch("pathlib.Path") as mock_path:
                    mock_video = MagicMock()
                    mock_concat.return_value = mock_video
                    mock_audio = MagicMock()
                    mock_audio_clip.return_value = mock_audio
                    mock_video.set_audio.return_value = mock_video

                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir)
                        audio_path = temp_path / "audio.mp3"
                        output_path = temp_path / "output.mp4"

                        # When
                        await service._combine_video_and_audio(
                            video_clips, audio_path, output_path
                        )

                        # Then
                        mock_concat.assert_called_once_with(
                            video_clips, method="compose"
                        )
                        mock_audio_clip.assert_called_once_with(str(audio_path))
                        mock_video.set_audio.assert_called_once_with(mock_audio)
                        mock_video.write_videofile.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_audio_duration(self, service):
        """Test audio duration retrieval."""
        with patch("backend.services.video_generator.AudioFileClip") as mock_audio_clip:
            mock_audio = MagicMock()
            mock_audio.duration = 10.5
            mock_audio_clip.return_value = mock_audio

            with tempfile.TemporaryDirectory() as temp_dir:
                audio_path = Path(temp_dir) / "test.mp3"

                # When
                duration = await service._get_audio_duration(audio_path)

                # Then
                assert duration == 10.5
                mock_audio.close.assert_called_once()
