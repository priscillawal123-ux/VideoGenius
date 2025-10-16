import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes.agents import router as agents_router
from .agents.base_agent import AgentRegistry
from .agents.image_analysis_agent import ImageAnalysisAgent
# from .agents.video_analysis_agent import VideoAnalysisAgent # Temporariamente desabilitado
from .agents.story_creator_agent import StoryCreatorAgent
from .services.google_cloud_service import GoogleCloudPipelineOrchestrator

# Configuração do Logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VideoGenius Orchestrator API",
    version="1.0.0",
    description="API para orquestrar agentes de IA e pipelines no Google Cloud.",
    openapi_url="/api/v1/openapi.json"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja para o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Inicialização de Recursos (Orquestrador e Agentes) ---

orchestrator = GoogleCloudPipelineOrchestrator(
    project_id=settings.PROJECT_ID,
    location=settings.GCP_LOCATION
)

image_agent = ImageAnalysisAgent(
    agent_id="image_analyzer_v1",
    config={},
    google_cloud_orchestrator=orchestrator
)
AgentRegistry.register_agent("image_analysis_agent", image_agent)

# video_agent = VideoAnalysisAgent(
#     agent_id="video_analyzer_v1",
#     config={"temp_gcs_bucket": settings.STORAGE_BUCKET}, # Bucket para frames temporários
#     google_cloud_orchestrator=orchestrator
# )
# AgentRegistry.register_agent("video_analysis_agent", video_agent)

story_agent = StoryCreatorAgent(
    agent_id="story_creator_v1",
    config={},
    google_cloud_orchestrator=orchestrator
)
AgentRegistry.register_agent("story_creator_agent", story_agent)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.get("/health", tags=["Monitoring"])
def health_check():
    """Verifica a saúde da aplicação."""
    logger.info("Health check solicitado.")
    return {"status": "healthy", "project_id": settings.PROJECT_ID}


# Incluir as rotas da API
app.include_router(agents_router, prefix="/api/v1")

logger.info(f"Aplicação VideoGenius iniciada no ambiente: {settings.ENVIRONMENT}")