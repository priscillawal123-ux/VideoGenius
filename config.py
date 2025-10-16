import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Gerencia as configurações da aplicação carregadas de variáveis de ambiente.
    """
    PROJECT_ID: str = os.getenv("GCP_PROJECT", "your-gcp-project-id")
    LOCATION: str = "us-central1"
    
    # Configurações do Cloud Tasks
    RENDER_QUEUE_NAME: str = "video-render-queue"
    RENDER_WORKER_URL: str = os.getenv("RENDER_WORKER_URL", "https://your-worker-service-url.a.run.app")

    class Config:
        env_file = ".env"

settings = Settings()