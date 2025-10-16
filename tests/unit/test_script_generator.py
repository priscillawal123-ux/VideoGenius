"""
Unit tests for ScriptGeneratorService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.services.script_generator import ScriptGeneratorService


class TestScriptGeneratorService:
    """Test cases for ScriptGeneratorService."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked dependencies."""
        with patch("backend.services.script_generator.aiplatform") as mock_aiplatform:
            with patch(
                "backend.services.script_generator.TextGenerationModel"
            ) as mock_model:
                service = ScriptGeneratorService(
                    project_id="test-project",
                    location="us-central1",
                    model_name="text-bison",
                )
                return service

    @pytest.mark.asyncio
    async def test_generate_script_success(self, service):
        """Test successful script generation."""
        # Given
        topic = "Machine Learning"
        duration = 120
        style = "educational"

        # When
        result = await service.generate_script(topic, duration, style)

        # Then
        assert isinstance(result, dict)
        assert "title" in result
        assert "hook" in result
        assert "script" in result
        assert "key_points" in result
        assert "metadata" in result

        assert result["metadata"]["topic"] == topic
        assert result["metadata"]["duration"] == duration
        assert result["metadata"]["style"] == style
        assert result["title"] == f"Entendendo {topic}"

    @pytest.mark.asyncio
    async def test_generate_script_duration_too_short(self, service):
        """Test script generation with duration too short."""
        with pytest.raises(
            ValueError, match="Duration must be between 30 and 600 seconds"
        ):
            await service.generate_script("Test", 10)

    @pytest.mark.asyncio
    async def test_generate_script_duration_too_long(self, service):
        """Test script generation with duration too long."""
        with pytest.raises(
            ValueError, match="Duration must be between 30 and 600 seconds"
        ):
            await service.generate_script("Test", 700)

    @pytest.mark.asyncio
    async def test_generate_script_with_context(self, service):
        """Test script generation with additional context."""
        topic = "Python Programming"
        duration = 90
        style = "tutorial"
        context = "Focus on beginners"

        result = await service.generate_script(topic, duration, style, context)

        assert result["metadata"]["topic"] == topic
        assert result["metadata"]["style"] == style
        assert "Python Programming" in result["script"]

    def test_build_prompt(self, service):
        """Test prompt building."""
        topic = "AI Ethics"
        duration = 180
        style = "documentary"
        context = "Include real-world examples"

        prompt = service._build_prompt(topic, duration, style, context)

        assert topic in prompt
        assert str(duration) in prompt
        assert style in prompt
        assert context in prompt
        assert "TITLE:" in prompt
        assert "HOOK:" in prompt
        assert "SCRIPT:" in prompt
        assert "KEY_POINTS:" in prompt

    def test_build_prompt_no_context(self, service):
        """Test prompt building without context."""
        topic = "Data Science"
        duration = 120
        style = "educational"

        prompt = service._build_prompt(topic, duration, style, None)

        assert topic in prompt
        assert str(duration) in prompt
        assert style in prompt
        assert "Additional context:" not in prompt

    def test_parse_response(self, service):
        """Test response parsing."""
        response = """TITLE: Understanding AI
HOOK: Did you know AI is everywhere?
SCRIPT:
Welcome to our AI video!

AI is transforming our world in amazing ways.
From smartphones to cars, AI is everywhere.

Thank you for watching!
KEY_POINTS:
- AI fundamentals
- Real-world applications
- Future implications
"""

        result = service._parse_response(response)

        assert result["title"] == "Understanding AI"
        assert result["hook"] == "Did you know AI is everywhere?"
        assert "Welcome to our AI video!" in result["script"]
        assert "AI fundamentals" in result["key_points"]
        assert len(result["key_points"]) == 3

    def test_parse_response_minimal(self, service):
        """Test parsing minimal response."""
        response = """TITLE: Test Title
HOOK: Test Hook
SCRIPT:
Test script content
KEY_POINTS:
- Point 1
"""

        result = service._parse_response(response)

        assert result["title"] == "Test Title"
        assert result["hook"] == "Test Hook"
        assert result["script"] == "Test script content"
        assert result["key_points"] == ["Point 1"]

    def test_initialization(self):
        """Test service initialization."""
        with patch("backend.services.script_generator.aiplatform") as mock_aiplatform:
            with patch(
                "backend.services.script_generator.TextGenerationModel"
            ) as mock_model:
                service = ScriptGeneratorService(
                    project_id="test-project",
                    location="us-central1",
                    model_name="text-bison",
                )

                mock_aiplatform.init.assert_called_once_with(
                    project="test-project", location="us-central1"
                )
                mock_model.from_pretrained.assert_called_once_with("text-bison")
                assert service.model_name == "text-bison"
