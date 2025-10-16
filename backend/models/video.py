"""
Modelos de dados Pydantic para o fluxo de geração de vídeo.
"""
from typing import Optional, Literal

from pydantic import BaseModel, root_validator


class VideoRequest(BaseModel):
    """
    Modelo para a requisição de geração de vídeo.
    Permite gerar a partir de um tópico ou de um roteiro personalizado.
    """
    topic: Optional[str] = None
    custom_script: Optional[str] = None
    duration_seconds: int = 60
    style: str = "educational"
    voice_name: Optional[str] = "pt-BR-Wavenet-B" # Voz feminina WaveNet
    # Outras opções de voz:
    # "pt-BR-Wavenet-A" (Feminina)
    # "pt-BR-Wavenet-C" (Masculina)
    # "pt-BR-Wavenet-D" (Masculina)

    @root_validator(pre=True)
    def check_topic_or_script_exists(cls, values):
        """Garante que 'topic' ou 'custom_script' seja fornecido, mas não ambos."""
        if 'topic' in values and 'custom_script' in values:
            raise ValueError("Forneça 'topic' ou 'custom_script', mas não ambos.")
        if 'topic' not in values and 'custom_script' not in values:
            raise ValueError("É necessário fornecer 'topic' ou 'custom_script'.")
        return values