import base64
import json
import logging
import os
from email.mime.text import MIMEText

import google.auth
from google.auth.transport.requests import Request
from google.cloud import secretmanager
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from backend.core.config import settings

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.send",
]

SECRET_NAME_OAUTH_TOKEN = "videogenius-oauth-refresh-token"
SECRET_NAME_OAUTH_CLIENT = "videogenius-oauth-client-secret"


class DeliveryService:
    """
    Serviço para entregar os vídeos gerados via Google Drive e notificar via Gmail.
    """

    def __init__(self):
        """Inicializa o serviço e autentica com as APIs do Google."""
        self._creds: Credentials | None = None
        self._drive_service = None
        self._gmail_service = None
        logger.info("DeliveryService initialized with lazy authentication.")

    @property
    def creds(self) -> Credentials | None:
        """Lazy initialize credentials."""
        if self._creds is None:
            self._creds = self._get_credentials()
        return self._creds

    @property
    def drive_service(self):
        """Lazy initialize Drive service."""
        if self._drive_service is None and self.creds:
            self._drive_service = build("drive", "v3", credentials=self.creds)
        return self._drive_service

    @property
    def gmail_service(self):
        """Lazy initialize Gmail service."""
        if self._gmail_service is None and self.creds:
            self._gmail_service = build("gmail", "v1", credentials=self.creds)
        return self._gmail_service

    def _get_credentials(self) -> Credentials | None:
        """
        Obtém credenciais para as APIs do Google, priorizando o fluxo OAuth 2.0
        com refresh token armazenado no Secret Manager.
        """
        try:
            secret_client = secretmanager.SecretManagerServiceClient()
            project_id = settings.GCP_PROJECT_ID

            # 1. Tenta obter o refresh token do Secret Manager
            token_secret_path = secret_client.secret_version_path(
                project_id, SECRET_NAME_OAUTH_TOKEN, "latest"
            )
            token_response = secret_client.access_secret_version(
                request={"name": token_secret_path}
            )
            refresh_token = token_response.payload.data.decode("UTF-8")

            # 2. Tenta obter o client secret do OAuth
            client_secret_path = secret_client.secret_version_path(
                project_id, SECRET_NAME_OAUTH_CLIENT, "latest"
            )
            client_secret_response = secret_client.access_secret_version(
                request={"name": client_secret_path}
            )
            client_config = json.loads(
                client_secret_response.payload.data.decode("UTF-8")
            )
            client_id = client_config["web"]["client_id"]
            client_secret = client_config["web"]["client_secret"]

            if refresh_token and client_id and client_secret:
                logger.info(
                    "Refresh token encontrado no Secret Manager. Usando credenciais OAuth."
                )
                creds = Credentials.from_authorized_user_info(
                    info={"refresh_token": refresh_token}, scopes=SCOPES
                )
                creds.client_id = client_id
                creds.client_secret = client_secret

                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                return creds

        except Exception as e:
            logger.warning(
                f"Não foi possível obter o refresh token do Secret Manager: {e}. "
                "Fazendo fallback para ADC."
            )

        try:
            logger.info("Usando Application Default Credentials (ADC).")
            creds, _ = google.auth.default(scopes=SCOPES)
            if (
                creds
                and hasattr(creds, "refresh")
                and creds.expired
                and creds.refresh_token
            ):
                creds.refresh(Request())
            return creds
        except Exception as e:
            logger.error(f"Falha ao carregar credenciais (ADC e OAuth): {e}")
            return None

    async def upload_to_drive(
        self, file_path: str, folder_name: str, user_email: str
    ) -> str | None:
        """Faz o upload de um arquivo para uma pasta específica no Google Drive."""
        if not self.drive_service:
            logger.error("Serviço do Drive não inicializado. Upload cancelado.")
            return None

        if not user_email:
            raise ValueError("user_email não pode ser nulo ou vazio.")

        try:
            logger.info(f"Iniciando upload para o Drive na pasta '{folder_name}'")
            folder_id = await self._find_or_create_folder(folder_name)

            file_metadata = {
                "name": os.path.basename(file_path),
                "parents": [folder_id],
            }
            media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)

            file = (
                self.drive_service.files()
                .create(body=file_metadata, media_body=media, fields="id, webViewLink")
                .execute()
            )

            file_id = file.get("id")
            web_view_link = file.get("webViewLink")
            logger.info(
                f"Arquivo '{os.path.basename(file_path)}' enviado com ID: {file_id}"
            )

            await self._share_file_with_user(file_id, user_email)
            return web_view_link

        except HttpError as error:
            logger.error(f"Erro no upload para o Drive: {error}")
            return None

    async def send_notification_email(
        self, to_email: str, subject: str, project_topic: str, drive_link: str
    ):
        """Envia um e-mail de notificação com o link do vídeo."""
        if not self.gmail_service:
            logger.error(
                "Serviço do Gmail não inicializado. Envio de e-mail cancelado."
            )
            return

        if not to_email:
            raise ValueError("to_email não pode ser nulo ou vazio.")

        try:
            logger.info(f"Enviando notificação por e-mail para {to_email}")
            message_text = f"""Olá,\n\nO seu vídeo sobre "{project_topic}" foi gerado com sucesso!\n\nVocê pode acessá-lo através do seguinte link:\n{drive_link}\n\nObrigado por usar o VideoGenius!"""
            mime_message = MIMEText(message_text)
            mime_message["to"] = to_email
            mime_message["from"] = "me"
            mime_message["subject"] = subject

            encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
            create_message = {"raw": encoded_message}

            self.gmail_service.users().messages().send(
                userId="me", body=create_message
            ).execute()
            logger.info(f"E-mail de notificação enviado com sucesso para {to_email}.")

        except HttpError as error:
            logger.error(f"Erro ao enviar e-mail: {error}")

    async def _share_file_with_user(self, file_id: str, user_email: str):
        """Compartilha um arquivo no Drive com um usuário específico."""
        try:
            permission = {"type": "user", "role": "reader", "emailAddress": user_email}
            self.drive_service.permissions().create(
                fileId=file_id, body=permission, sendNotificationEmail=False
            ).execute()
            logger.info(f"Arquivo {file_id} compartilhado com {user_email}.")
        except HttpError as error:
            logger.error(
                f"Erro ao compartilhar arquivo {file_id} com {user_email}: {error}"
            )

    async def _find_or_create_folder(self, folder_name: str) -> str | None:
        """Encontra uma pasta no Drive com o nome especificado ou a cria."""
        try:
            query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
            response = (
                self.drive_service.files()
                .list(q=query, spaces="drive", fields="files(id)")
                .execute()
            )

            if files := response.get("files", []):
                folder_id = files[0].get("id")
                logger.info(f"Pasta '{folder_name}' encontrada com ID: {folder_id}")
                return folder_id

            logger.info(f"Pasta '{folder_name}' não encontrada. Criando...")
            folder_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            folder = (
                self.drive_service.files()
                .create(body=folder_metadata, fields="id")
                .execute()
            )
            folder_id = folder.get("id")
            logger.info(f"Pasta '{folder_name}' criada com ID: {folder_id}")
            return folder_id

        except HttpError as error:
            logger.error(f"Erro ao buscar ou criar pasta no Drive: {error}")
            return None
