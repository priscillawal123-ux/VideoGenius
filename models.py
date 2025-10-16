from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class VideoStyle(str, Enum):
    TUTORIAL = "tutorial"
    DOCUMENTARY = "documentary"
    NEWS = "news"
    ENTERTAINMENT = "entertainment"

class VideoBlueprint(BaseModel):
    topic: str = Field(..., description="O tópico principal do vídeo.")
    style: VideoStyle = Field(default=VideoStyle.TUTORIAL, description="O estilo do vídeo.")
    target_audience: str = Field(..., description="O público-alvo do vídeo.")
    duration_minutes: int = Field(5, gt=0, le=60, description="Duração estimada em minutos.")

class GeneratedScript(BaseModel):
    title: str
    scenes: List[str]
    voiceover: str

class VideoProject(BaseModel):
    id: str = Field(..., description="ID único do projeto de vídeo.")
    blueprint: VideoBlueprint
    script: Optional[GeneratedScript] = None
    status: str = Field("pending", description="Status atual do projeto.")

class VideoProjectCreate(BaseModel):
    blueprint: VideoBlueprint

class StatusResponse(BaseModel):
    status: str
    details: str
    project_id: Optional[str] = None