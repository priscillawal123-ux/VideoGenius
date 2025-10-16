"""
Módulo contendo a tarefa de background para processamento de vídeo.
"""
import logging

from backend.services.checkpoint import save_progress_checkpoint
from backend.services.script_generator import ScriptGeneratorService
from backend.services.custom_script_parser import CustomScriptParserService
from backend.models.video import VideoRequest
# Supondo que você tenha um cliente BigQuery e outros serviços
# from backend.database.bigquery_client import BigQueryClient

logger = logging.getLogger(__name__)


async def process_video_generation(
    job_id: str,
    request: VideoRequest,
    user_id: str,
    script_service: ScriptGeneratorService,
    # db_client: BigQueryClient, # Descomente quando o cliente DB estiver pronto
) -> None:
    """Background task to process video generation."""
    try:
        # await db_client.update_job_status(job_id, "processing_script")
        logger.info(f"Job {job_id}: Iniciando processamento do roteiro.")

        script_data = {}
        if request.custom_script:
            # Se um roteiro personalizado foi fornecido, use o parser
            parser = CustomScriptParserService()
            script_data = parser.parse(request.custom_script)
        elif request.topic:
            # Caso contrário, gere o roteiro a partir do tópico
            script_data = await script_service.generate_script(
                topic=request.topic,
                duration_seconds=request.duration_seconds,
                style=request.style,
            )

        if not script_data:
            raise ValueError("Falha ao obter dados do roteiro.")

        logger.info(f"Job {job_id}: Roteiro processado. Título: '{script_data.get('title')}'")

        # A partir daqui, o fluxo continua normalmente com o 'script_data' padronizado
        # await db_client.update_job_data(job_id, {"script": script_data})
        # await save_progress_checkpoint(job_id, db_client, 10, {"step": "script_processed"})

        logger.info(f"Job {job_id}: Próximo passo seria gerar os assets de vídeo...")
        # await db_client.update_job_status(job_id, "generating_assets")

    except Exception as e:
        logger.error(f"Falha na geração do vídeo para o job {job_id}: {e}", exc_info=True)
        # await db_client.update_job_status(job_id, "failed", error=str(e))
