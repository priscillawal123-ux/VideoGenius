import asyncio
import logging
import hashlib
import os
from typing import Any, Dict, List

import aiohttp
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class AssetManagerService:
    """
    Gerencia a busca e o download de assets de mídia (imagens e vídeos)
    para as cenas do vídeo.
    """

    def __init__(self):
        """Inicializa o serviço com a chave de API do Pexels."""
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        if not self.pexels_api_key:
            logger.warning(
                "Chave de API do Pexels não encontrada. O serviço de busca de assets será desativado."
            )
            self.enabled = False
        else:
            self.enabled = True
            self.headers = {"Authorization": self.pexels_api_key}
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def _search_pexels(self, query: str, asset_type: str) -> str | None:
        """Busca um asset no Pexels e retorna a URL para download."""
        if not self.enabled or not self.session:
            return None

        base_url = f"https://api.pexels.com/{asset_type}/search"
        params = {"query": query, "per_page": 1, "orientation": "landscape"}
        
        try:
            async with self.session.get(base_url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                if asset_type == "videos" and data.get("videos"):
                    video_files = data["videos"][0].get("video_files", [])
                    # Procura por um vídeo com qualidade próxima a HD
                    hd_video = next((f for f in video_files if f.get("quality") == "hd"), None)
                    return hd_video["link"] if hd_video else video_files[0]["link"]
                
                if asset_type == "v1" and data.get("photos"): # API de fotos usa /v1/
                    return data["photos"][0]["src"]["large2x"]

        except aiohttp.ClientError as e:
            logger.error(f"Erro ao buscar no Pexels para '{query}': {e}")
        return None

    async def _download_asset(self, url: str, save_path: str) -> None:
        """Baixa um asset de uma URL e o salva localmente."""
        if not self.session:
            return
        try:
            async with self.session.get(url, headers={}) as response: # Usa headers vazios para download
                response.raise_for_status()
                with open(save_path, "wb") as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
            logger.info(f"Asset baixado com sucesso e salvo em: {save_path}")
        except aiohttp.ClientError as e:
            logger.error(f"Falha ao baixar o asset de {url}: {e}")

    async def fetch_assets_for_script(
        self, script_data: Dict[str, Any], temp_dir: str
    ) -> Dict[str, Any]:
        """Orquestra a busca e o download de assets para cada cena do roteiro."""
        if not self.enabled:
            raise ConnectionError("AssetManagerService está desativado. Verifique a PEXELS_API_KEY.")

        scenes = script_data.get("scenes", [])
        download_tasks = []
        assets_map = {}

        async def process_scene(i, scene):
            query = scene.get("search_query", script_data.get("topic", ""))
            asset_type = "videos" if i % 2 == 0 else "v1"  # Alterna entre vídeo e foto
            file_extension = ".mp4" if asset_type == "videos" else ".jpg"

            # Cache Inteligente: Gera um nome de arquivo baseado no hash da query
            query_hash = hashlib.md5(query.encode()).hexdigest()
            cached_asset_path = os.path.join(temp_dir, f"asset_{query_hash}{file_extension}")

            if os.path.exists(cached_asset_path):
                logger.info(f"Usando asset em cache para a query '{query}': {cached_asset_path}")
                assets_map[f"scene{i+1}"] = {"path": cached_asset_path, "text": scene["text"]}
            else:
                url = await self._search_pexels(query, asset_type)
                if url:
                    await self._download_asset(url, cached_asset_path)
                    assets_map[f"scene{i+1}"] = {"path": cached_asset_path, "text": scene["text"]}

        tasks = [process_scene(i, scene) for i, scene in enumerate(scenes)]
        await asyncio.gather(*tasks)

        return {"scenes": assets_map}