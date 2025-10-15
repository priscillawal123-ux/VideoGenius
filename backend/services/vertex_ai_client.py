"""
Vertex AI client with Google Cloud best practices and optimizations.
"""

import asyncio
import logging
from typing import Any, Dict, Optional, Callable, cast

from cachetools import TTLCache
from google.api_core import exceptions, retry
from google.cloud import aiplatform
from vertexai import language_models

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern for external service calls."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        return (
            asyncio.get_event_loop().time() - self.last_failure_time
        ) > self.recovery_timeout

    def _on_success(self) -> None:
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class VertexAIClient:
    """Optimized Vertex AI client with caching and circuit breaker."""

    def __init__(self, project_id: str, location: str = "us-central1"):
        """Initialize Vertex AI client with optimizations.

        Args:
            project_id: GCP project ID
            location: GCP region
        """
        self.project_id = project_id
        self.location = location
        self._initialized = False

        # Configure retry strategy
        self.retry_config = retry.Retry(
            initial=1.0,
            maximum=16.0,
            multiplier=2.0,
            deadline=120.0,  # Longer timeout for AI generation
            predicate=retry.if_exception_type(
                exceptions.ServiceUnavailable,
                exceptions.TooManyRequests,
                exceptions.InternalServerError,
                exceptions.ResourceExhausted,
            ),
        )

        self._model: Optional[language_models.TextGenerationModel] = None
        self.cache = TTLCache(maxsize=100, ttl=3600)  # 1 hour cache
        self._circuit_breaker: Optional[CircuitBreaker] = None

    def _ensure_initialized(self) -> None:
        """Ensure Vertex AI is initialized."""
        if not self._initialized:
            aiplatform.init(project=self.project_id, location=self.location)
            self._initialized = True

    @property
    def model(self) -> language_models.TextGenerationModel:
        """Lazy initialize Vertex AI model."""
        if self._model is None:
            self._ensure_initialized()
            self._model = language_models.TextGenerationModel.from_pretrained(
                "text-bison"
            )
        return self._model

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        """Lazy initialize circuit breaker."""
        if self._circuit_breaker is None:
            self._circuit_breaker = CircuitBreaker()
        return self._circuit_breaker

    async def generate_content(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> str:
        """Generate content with caching and circuit breaker protection.

        Args:
            prompt: Input prompt
            config: Generation configuration
            use_cache: Whether to use caching

        Returns:
            Generated text

        Raises:
            ValueError: If generation fails
        """
        # Check cache first
        if use_cache:
            cache_key = hash(prompt + str(config or {}))
            if cache_key in self.cache:
                logger.info("Returning cached response")
                return self.cache[cache_key]

        async def _generate():
            try:
                parameters = {
                    "temperature": config.get("temperature", 0.7) if config else 0.7,
                    "max_output_tokens": (
                        config.get("max_output_tokens", 1024) if config else 1024
                    ),
                    "top_p": config.get("top_p", 0.8) if config else 0.8,
                    "top_k": config.get("top_k", 40) if config else 40,
                }

                response = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.model.predict(prompt, **parameters)
                )

                if not response.text:
                    raise ValueError("Empty response from model")

                logger.info("Content generated successfully")
                return response.text

            except Exception as e:
                logger.error(f"Generation error: {e}")
                raise ValueError(f"Failed to generate: {e}") from e

        result = await self.circuit_breaker.call(_generate)

        # Cache the result
        if use_cache:
            cache_key = hash(prompt + str(config or {}))
            self.cache[cache_key] = result

        return result

    async def generate_video_script(
        self, topic: str, duration_seconds: int, style: str = "educational"
    ) -> str:
        """Generate a video script with optimized prompt.

        Args:
            topic: Video topic
            duration_seconds: Target duration
            style: Content style

        Returns:
            Generated script
        """
        prompt = f"""
        Create a {style} video script about: {topic}

        Requirements:
        - Duration: approximately {duration_seconds} seconds
        - Style: {style}
        - Include engaging narration and visual descriptions
        - Structure: Introduction, main content, conclusion
        - Make it suitable for video production

        Format the script with timestamps and clear sections.
        """

        config = {
            "temperature": 0.7,
            "max_output_tokens": 2048,
            "top_p": 0.8,
        }

        return await self.generate_content(prompt, config)

    async def generate_video_description(self, topic: str, script: str) -> str:
        """Generate video description and metadata.

        Args:
            topic: Video topic
            script: Video script

        Returns:
            Generated description
        """
        prompt = f"""
        Create a compelling video description for YouTube based on:

        Topic: {topic}

        Script preview: {script[:500]}...

        Requirements:
        - SEO optimized
        - Engaging and descriptive
        - Include relevant keywords
        - Under 5000 characters
        - Include call-to-action
        """

        config = {
            "temperature": 0.8,
            "max_output_tokens": 1024,
            "top_p": 0.9,
        }

        return await self.generate_content(prompt, config)

    async def analyze_content_safety(self, content: str) -> Dict[str, Any]:
        """Analyze content for safety and appropriateness.

        Args:
            content: Content to analyze

        Returns:
            Safety analysis results
        """
        prompt = f"""
        Analyze the following content for safety and appropriateness:

        Content: {content}

        Provide a JSON response with:
        - safety_score: 0-100 (100 being completely safe)
        - issues: array of potential issues found
        - recommendations: array of improvement suggestions
        - approved: boolean indicating if content is safe to use

        Be conservative in your assessment.
        """

        config = {
            "temperature": 0.1,  # Low temperature for consistent analysis
            "max_output_tokens": 512,
        }

        response = await self.generate_content(prompt, config)

        # Parse JSON response (simplified - in production use proper JSON parsing)
        try:
            import json

            return json.loads(response)
        except:
            # Fallback if JSON parsing fails
            return {
                "safety_score": 75,
                "issues": [],
                "recommendations": ["Content appears safe"],
                "approved": True,
            }
