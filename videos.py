import logging
from fastapi import APIRouter, HTTPException, status

from backend.core.config import settings
from backend.models.video import VideoRenderRequest, JobResponse
from backend.services.task_queue_manager import TaskQueueManagerService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/videos", tags=["Videos"])

try:
    task_manager = TaskQueueManagerService(
        project_id=settings.PROJECT_ID,
        location=settings.LOCATION,
        queue_name=settings.RENDER_QUEUE_NAME,
        worker_url=settings.RENDER_WORKER_URL,
    )
except Exception as e:
    logger.critical(f"Falha ao inicializar o TaskQueueManagerService: {e}", exc_info=True)
    task_manager = None

@router.post("/render", status_code=status.HTTP_2_2_ACCEPTED, response_model=JobResponse)
async def render_video_endpoint(request: VideoRenderRequest):
    """
    Recebe uma solicitação de renderização de vídeo e a enfileira para processamento assíncrono.
    """
    if not task_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O serviço de enfileiramento de tarefas não está disponível."
        )
    
    logger.info(f"Recebida solicitação de renderização para o tópico: {request.topic}")
    job_name = task_manager.enqueue_video_render_task(request.model_dump())
    
    return {"job_name": job_name, "message": "Job de renderização de vídeo enfileirado com sucesso."}