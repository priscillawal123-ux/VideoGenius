"""
Models for video editing templates.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class EditType(str, Enum):
    """Tipos de edição suportados."""

    TEXT_OVERLAY = "text_overlay"
    IMAGE_OVERLAY = "image_overlay"
    AUDIO_MIX = "audio_mix"
    TRANSITION = "transition"


class EditAction(BaseModel):
    """Ação de edição individual."""

    type: EditType = Field(..., description="Tipo de edição")
    timestamp_start: float = Field(ge=0, description="Timestamp inicial (segundos)")
    duration: Optional[float] = Field(
        None, ge=0, description="Duração da edição (opcional)"
    )
    content: Dict[str, Any] = Field(
        ..., description="Conteúdo da edição (ex.: texto, URL de imagem)"
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Valida que o conteúdo não está vazio."""
        if not v:
            raise ValueError("Conteúdo não pode estar vazio")
        return v


class VideoEditTemplate(BaseModel):
    """Template para edições de vídeo."""

    base_video_url: Optional[str] = Field(
        None, description="URL do vídeo base (opcional)"
    )
    edits: List[EditAction] = Field(
        default_factory=list, description="Lista de edições a aplicar"
    )
    output_format: str = Field(default="mp4", description="Formato de saída")
