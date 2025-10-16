"""
Script generation service using Vertex AI.
"""

import logging
from typing import Any, Dict, Optional

from backend.services.vertex_ai_client import VertexAIClient

logger = logging.getLogger(__name__)


class ScriptGeneratorService:
    """Service for generating video scripts using Vertex AI."""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
    ):
        """Initialize script generator.

        Args:
            project_id: GCP project ID
            location: Vertex AI location
        """
        self.vertex_ai_client = VertexAIClient(project_id=project_id, location=location)
        logger.info("Initialized ScriptGeneratorService with lazy VertexAIClient")

    async def generate_script(
        self,
        topic: str,
        duration_seconds: int,
        style: str = "educational",
        additional_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate video script based on topic and parameters.

        Args:
            topic: Main topic for the video
            duration_seconds: Target video duration
            style: Script style (educational, entertaining, documentary)
            additional_context: Extra context or requirements

        Returns:
            Dict containing script, title, and metadata

        Raises:
            ValueError: If generation fails or parameters invalid
        """
        if duration_seconds < 30 or duration_seconds > 600:
            raise ValueError("Duration must be between 30 and 600 seconds")

        # For development/testing, return mock data
        # instead of calling Vertex AI
        logger.info(f"Mock script generation for topic: {topic}")

        # Estrutura de roteiro mais detalhada com sugestões de busca
        mock_scenes = [
            {
                "text": f"Olá! Bem-vindo ao nosso vídeo sobre {topic}.",
                "search_query": f"abstrato boas-vindas tecnologia",
            },
            {
                "text": f"{topic} é um assunto fascinante que tem impactado nossa vida cotidiana.",
                "search_query": f"{topic} conceito",
            },
            {
                "text": "Neste vídeo, vamos explorar os conceitos fundamentais e aplicações práticas.",
                "search_query": f"{topic} aplicações práticas",
            },
            {
                "text": "Obrigado por assistir! Não esqueça de curtir e se inscrever.",
                "search_query": "ícones de redes sociais like subscribe",
            },
        ]

        return {
            "title": f"Entendendo {topic}",
            "hook": f"Você sabia que {topic} está revolucionando "
            "nossa forma de viver?",
            "script": " ".join([scene["text"] for scene in mock_scenes]),
            "scenes": mock_scenes,
            "key_points": [
                f"Conceitos básicos de {topic}",
                f"Aplicações práticas de {topic}",
                f"Impacto futuro de {topic}",
            ],
            "metadata": {
                "topic": topic,
                "duration": duration_seconds,
                "style": style,
                "model": "mock-generator",
            },
        }

    def _build_prompt(
        self, topic: str, duration: int, style: str, context: Optional[str]
    ) -> str:
        """Build generation prompt.

        Args:
            topic: Video topic
            duration: Duration in seconds
            style: Script style
            context: Additional context

        Returns:
            Formatted prompt
        """
        words_estimate = (duration * 150) // 60  # ~150 words per minute

        prompt = f"""Generate a {style} video script about: {topic}

Requirements:
- Target duration: {duration} seconds (~{words_estimate} words)
- Style: {style}
- Include engaging hook in first 5 seconds
- Clear structure: intro, main content, conclusion
- Natural narration flow

{"Additional context: " + context if context else ""}

Format the response as:
TITLE: [engaging title]
HOOK: [first 5 seconds]
SCRIPT: [full script]
KEY_POINTS: [3-5 bullet points]
"""
        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse model response into structured data.

        Args:
            response: Raw model response

        Returns:
            Structured script data
        """
        lines = response.strip().split("\n")
        data: Dict[str, Any] = {"title": "", "hook": "", "script": "", "key_points": []}

        current_section = None
        script_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith("TITLE:"):
                data["title"] = line.replace("TITLE:", "").strip()
            elif line.startswith("HOOK:"):
                data["hook"] = line.replace("HOOK:", "").strip()
            elif line.startswith("SCRIPT:"):
                current_section = "script"
            elif line.startswith("KEY_POINTS:"):
                current_section = "key_points"
            elif current_section == "script" and line:
                script_lines.append(line)
            elif current_section == "key_points" and line.startswith("-"):
                data["key_points"].append(line.lstrip("- "))

        data["script"] = "\n".join(script_lines)
        return data
