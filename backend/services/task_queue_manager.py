import json
import logging
import os
from typing import Any, Dict, Optional

from google.cloud import tasks_v2
from google.protobuf import duration_pb2, timestamp_pb2

logger = logging.getLogger(__name__)


class TaskQueueManagerService:
    """
    Gerencia a criação e o enfileiramento de tarefas no Google Cloud Tasks.
    """

    def __init__(
        self, project_id: str, location: str, queue_name: str, worker_url: str
    ):
        """
        Inicializa o cliente do Cloud Tasks.

        Args:
            project_id: ID do projeto no Google Cloud.
            location: Localização da fila do Cloud Tasks (ex: 'us-central1').
            queue_name: Nome da fila.
            worker_url: URL do serviço de worker que processará a tarefa (ex: um endpoint no Cloud Run).
        """
        self._client: Optional[tasks_v2.CloudTasksClient] = None
        self.project_id = project_id
        self.location = location
        self.queue_name = queue_name
        self.worker_url = worker_url

    @property
    def client(self) -> tasks_v2.CloudTasksClient:
        """Lazy initialize Cloud Tasks client."""
        if self._client is None:
            self._client = tasks_v2.CloudTasksClient()
        return self._client
        self.parent = self.client.queue_path(project_id, location, queue_name)
        logger.info(f"TaskQueueManagerService inicializado para a fila '{queue_name}'.")

    def enqueue_video_render_task(self, payload: Dict[str, Any]) -> str:
        """
        Cria e enfileira uma nova tarefa de renderização de vídeo.

        Args:
            payload: O corpo da requisição a ser enviado para o worker.

        Returns:
            O nome da tarefa criada.
        """
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": self.worker_url,
                "headers": {"Content-type": "application/json"},
                "body": json.dumps(payload).encode(),
            }
        }

        # Define um timeout para a tarefa
        dispatch_deadline = duration_pb2.Duration()
        dispatch_deadline.seconds = 600  # 10 minutos de timeout
        task["dispatch_deadline"] = dispatch_deadline

        response = self.client.create_task(parent=self.parent, task=task)
        logger.info(
            f"Tarefa de renderização '{response.name}' enfileirada com sucesso."
        )

        return response.name
