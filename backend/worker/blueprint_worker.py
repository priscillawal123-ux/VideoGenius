"""
Blueprint Generation Worker for VideoGenius.

This worker is triggered by Pub/Sub messages to generate video scripts
using Google Gemini AI.
"""

import json
import logging
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from backend.services.vertex_ai_client import VertexAIClient
from backend.core.config import get_settings

logger = logging.getLogger(__name__)

app = FastAPI(title="VideoGenius Blueprint Worker")

settings = get_settings()


class PubSubMessage(BaseModel):
    """Pub/Sub message structure."""

    message: Dict[str, Any]
    subscription: str


class BlueprintRequest(BaseModel):
    """Blueprint generation request."""

    job_id: str
    topic: str
    requirements: Dict[str, Any]


@app.post("/generate-blueprint")
async def generate_blueprint(request: Request):
    """
    Generate video blueprint using Gemini AI.

    Triggered by Pub/Sub push subscription.
    """
    try:
        # Parse Pub/Sub message
        body = await request.json()
        pubsub_message = PubSubMessage(**body)

        # Extract message data
        message_data = json.loads(pubsub_message.message.get("data", "{}"))

        job_id = message_data.get("job_id")
        topic = message_data.get("topic")
        requirements = message_data.get("requirements", {})

        if not job_id or not topic:
            raise HTTPException(status_code=400, detail="Missing job_id or topic")

        logger.info(f"Generating blueprint for job {job_id}, topic: {topic}")

        # Generate blueprint using Vertex AI
        vertex_client = VertexAIClient()

        prompt = f"""
        Generate a detailed video script for the topic: {topic}

        Requirements: {json.dumps(requirements, indent=2)}

        Please provide:
        1. A compelling hook (10-15 seconds)
        2. Main content script (45-60 seconds)
        3. Call to action

        Format as JSON with keys: hook, script, title
        """

        response = await vertex_client.generate_text(prompt)

        # Parse response (assuming it's JSON)
        try:
            blueprint = json.loads(response)
        except json.JSONDecodeError:
            # Fallback if not JSON
            blueprint = {
                "title": f"Video about {topic}",
                "hook": response[:200] + "...",
                "script": response,
            }

        logger.info(f"Blueprint generated for job {job_id}")

        # Here you could store the blueprint in BigQuery or trigger next step
        # For now, just return success

        return {"status": "success", "job_id": job_id, "blueprint": blueprint}

    except Exception as e:
        logger.error(f"Error generating blueprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.worker.blueprint_worker:app", host="0.0.0.0", port=8080, reload=True
    )
