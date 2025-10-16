from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class VideoRenderRequest(BaseModel):
    """
    Modelo para a requisição de renderização de vídeo.
    """
    topic: str = Field(..., description="O tópico principal do vídeo.", example="Inteligência Artificial")
    voice_name: str = Field("pt-BR-Wavenet-B", description="A voz a ser usada para a narração.")
    aspect_ratio: str = Field("16:9", description="A proporção do vídeo ('16:9', '9:16', '1:1').")
    resolution: str = Field("1080p", description="A resolução do vídeo ('720p', '1080p', '4k').")
    
    # Campos opcionais para assets personalizados
    background_music_path: Optional[str] = Field(None, description="Caminho para a música de fundo em GCS.")
    intro_clip_path: Optional[str] = Field(None, description="Caminho para o clipe de introdução em GCS.")
    outro_clip_path: Optional[str] = Field(None, description="Caminho para o clipe de encerramento em GCS.")
    watermark_path: Optional[str] = Field(None, description="Caminho para a imagem da marca d'água em GCS.")

class JobResponse(BaseModel):
    """
    Modelo para a resposta do job enfileirado.
    """
    job_name: str
    message: str