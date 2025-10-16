"""
Serviço para aplicar templates de edição usando FFmpeg.
"""

import logging
import os
import subprocess
from typing import List

from backend.models.edit_template import EditAction, EditType, VideoEditTemplate

logger = logging.getLogger(__name__)


class EditTemplateService:
    """Serviço para aplicar templates de edição usando FFmpeg."""

    async def apply_template(
        self, template: VideoEditTemplate, input_video_path: str, output_path: str
    ) -> str:
        """Aplica template de edição ao vídeo.

        Args:
            template: Template de edição
            input_video_path: Caminho do vídeo de entrada
            output_path: Caminho de saída

        Returns:
            Caminho do vídeo editado

        Raises:
            ValueError: Se edição falhar
        """
        try:
            # Construir comando FFmpeg baseado no template
            ffmpeg_cmd = self._build_ffmpeg_command(
                template, input_video_path, output_path
            )

            # Executar FFmpeg
            subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)

            if not os.path.exists(output_path):
                raise ValueError("Vídeo editado não foi gerado")

            logger.info(f"Template aplicado: {output_path}")
            return output_path

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg erro: {e.stderr}")
            raise ValueError(f"Falha na edição: {e.stderr}") from e
        except Exception as e:
            logger.error(f"Erro ao aplicar template: {e}")
            raise ValueError(f"Edição falhou: {e}") from e

    def _build_ffmpeg_command(
        self, template: VideoEditTemplate, input_path: str, output_path: str
    ) -> List[str]:
        """Constrói comando FFmpeg para o template.

        Args:
            template: Template
            input_path: Entrada
            output_path: Saída

        Returns:
            Comando FFmpeg
        """
        cmd = ["ffmpeg", "-i", input_path]

        # Adicionar filtros para cada edição
        filters = []
        for edit in template.edits:
            if edit.type == EditType.TEXT_OVERLAY:
                text_filter = self._text_overlay_filter(edit)
                filters.append(text_filter)
            # Adicionar outros tipos conforme necessário

        if filters:
            cmd.extend(["-vf", ",".join(filters)])

        cmd.extend(["-c:a", "copy", output_path])
        return cmd

    def _text_overlay_filter(self, edit: EditAction) -> str:
        """Gera filtro FFmpeg para texto overlay.

        Args:
            edit: Ação de edição

        Returns:
            String de filtro
        """
        text = edit.content.get("text", "")
        x = edit.content.get("x", 10)
        y = edit.content.get("y", 10)
        fontsize = edit.content.get("fontsize", 24)

        duration_filter = ""
        if edit.duration:
            duration_filter = (
                f":enable='between(t,{edit.timestamp_start},"
                f"{edit.timestamp_start + edit.duration})'"
            )

        return (
            f"drawtext=text='{text}':x={x}:y={y}:fontsize={fontsize}"
            f"{duration_filter}"
        )
