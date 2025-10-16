"""
YouTube uploader service for Video Genius.
"""

import logging
import os
import pickle
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from backend.core.config import settings

logger = logging.getLogger(__name__)


class YouTubeUploaderService:
    """Serviço para upload de vídeos ao YouTube."""

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    def __init__(self):
        """Inicializa cliente YouTube."""
        self.credentials = self._get_credentials()
        if self.credentials:
            self.youtube = build("youtube", "v3", credentials=self.credentials)
        else:
            self.youtube = None
            logger.warning("YouTube credentials not available")

    def _get_credentials(self) -> Optional[Credentials]:
        """Obtém credenciais OAuth do YouTube."""
        creds = None

        # Carregar credenciais salvas
        if settings.youtube_oauth_credentials and os.path.exists(
            settings.youtube_oauth_credentials
        ):
            with open(settings.youtube_oauth_credentials, "rb") as token:
                creds = pickle.load(token)

        # Se não há credenciais válidas, fazer login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not settings.youtube_client_secrets_file:
                    logger.error("YouTube client secrets file not configured")
                    return None

                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.youtube_client_secrets_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Salvar credenciais
            if settings.youtube_oauth_credentials:
                with open(settings.youtube_oauth_credentials, "wb") as token:
                    pickle.dump(creds, token)

        return creds

    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        privacy_status: str = "private",
    ) -> Dict[str, Any]:
        """Faz upload de vídeo para YouTube.

        Args:
            video_path: Caminho do vídeo
            title: Título
            description: Descrição
            tags: Lista de tags
            privacy_status: Status de privacidade

        Returns:
            Dados do vídeo enviado

        Raises:
            ValueError: Se upload falhar
        """
        if not self.youtube:
            raise ValueError("YouTube client not initialized")

        try:
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

            request = self.youtube.videos().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "tags": tags or [],
                        "categoryId": "22",  # People & Blogs
                    },
                    "status": {"privacyStatus": privacy_status},
                },
                media_body=media,
            )

            response = request.execute()

            logger.info(f"Vídeo enviado ao YouTube: {response['id']}")
            return {
                "video_id": response["id"],
                "url": f"https://www.youtube.com/watch?v={response['id']}",
                "status": "uploaded",
            }

        except Exception as e:
            logger.error(f"Upload YouTube falhou: {e}")
            raise ValueError(f"Falha no upload: {e}") from e
