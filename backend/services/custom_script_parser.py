"""
Serviço para analisar (parse) roteiros de vídeo personalizados.
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class CustomScriptParserService:
    """
    Analisa um roteiro de vídeo fornecido em formato de texto e o converte
    em uma estrutura de dados padronizada.
    """

    def parse(self, custom_script_text: str) -> Dict[str, Any]:
        """
        Converte o texto do roteiro em um dicionário estruturado.

        O formato esperado é:
        TITLE: O Título do Vídeo
        HOOK: A frase de impacto inicial.
        ---
        SCENE: Descrição visual da cena 1.
        NARRATION: Texto da narração para a cena 1.
        ---
        SCENE: Descrição visual da cena 2.
        NARRATION: Texto da narração para a cena 2.

        Returns:
            Um dicionário com a estrutura de dados do roteiro.
        """
        logger.info("Analisando roteiro personalizado...")
        try:
            title = ""
            hook = ""
            scenes: List[str] = []
            narrations: List[str] = []

            # Separa o cabeçalho (título/hook) do corpo do roteiro
            parts = custom_script_text.split("---", 1)
            header = parts[0]
            body = parts[1] if len(parts) > 1 else ""

            for line in header.strip().splitlines():
                if line.upper().startswith("TITLE:"):
                    title = line[len("TITLE:"):].strip()
                elif line.upper().startswith("HOOK:"):
                    hook = line[len("HOOK:"):].strip()

            # Processa as cenas
            scene_blocks = body.strip().split("---")
            for block in scene_blocks:
                if not block.strip():
                    continue
                scene_desc = ""
                narration_text = ""
                for line in block.strip().splitlines():
                    if line.upper().startswith("SCENE:"):
                        scene_desc = line[len("SCENE:"):].strip()
                    elif line.upper().startswith("NARRATION:"):
                        narration_text = line[len("NARRATION:"):].strip()
                if scene_desc and narration_text:
                    scenes.append(scene_desc)
                    narrations.append(narration_text)

            if not title or not scenes:
                raise ValueError("Roteiro inválido. 'TITLE' e pelo menos uma 'SCENE' são obrigatórios.")

            logger.info(f"Roteiro '{title}' analisado com sucesso com {len(scenes)} cenas.")
            return {
                "title": title,
                "hook": hook,
                "script": "\n".join(narrations),  # O roteiro completo é a junção de todas as narrações
                "key_points": scenes,  # Os 'key_points' visuais são as descrições de cena
            }
        except Exception as e:
            logger.error(f"Falha ao analisar o roteiro personalizado: {e}", exc_info=True)
            raise ValueError(f"Formato de roteiro inválido: {e}") from e