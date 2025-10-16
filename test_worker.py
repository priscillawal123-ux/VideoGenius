#!/usr/bin/env python3
"""
Testes de unidade para o worker do VideoGenius.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from backend.worker import process_message, VideoIdea

@pytest.fixture
def mock_publisher():
    """Fixture que cria um mock do PublisherClient."""
    publisher = MagicMock()
    mock_future = MagicMock()
    mock_future.result.return_value = "mock_message_id_abc"
    publisher.publish.return_value = mock_future
    return publisher

@pytest.fixture
def mock_generative_model():
    """Fixture que cria um mock do GenerativeModel do Vertex AI."""
    model = MagicMock()
    return model

@pytest.fixture
def mock_pubsub_message():
    """Fixture que cria uma mensagem Pub/Sub simulada."""
    def _create_message(data: dict, message_id: str = "12345"):
        message = MagicMock()
        message.message_id = message_id
        message.data = json.dumps(data).encode('utf-8')
        message.ack = MagicMock()
        message.nack = MagicMock()
        return message
    return _create_message

def test_process_message_success(mock_publisher, mock_generative_model, mock_pubsub_message):
    """
    Testa o caminho de sucesso do processamento de uma mensagem válida.
    """
    # Arrange: Configura os mocks
    video_idea_payload = {
        "title": "Teste de Sucesso",
        "topic": "Tópico de teste",
        "audience": "Testadores",
    }
    
    generated_blueprint = {
        "title": "Blueprint Gerado",
        "description": "Descrição do blueprint",
        "script_outline": {},
        "visual_suggestions": {},
        "tags": ["teste"]
    }
    
    # Simula a resposta do Gemini
    mock_response = MagicMock()
    mock_response.text = json.dumps(generated_blueprint)
    mock_generative_model.generate_content.return_value = mock_response
    
    message = mock_pubsub_message(video_idea_payload)
    output_topic = "projects/test-proj/topics/output-topic"

    # Act: Executa a função a ser testada
    process_message(message, mock_publisher, mock_generative_model, output_topic)

    # Assert: Verifica os resultados
    mock_generative_model.generate_content.assert_called_once()
    mock_publisher.publish.assert_called_once_with(output_topic, json.dumps(generated_blueprint).encode('utf-8'))
    message.ack.assert_called_once()
    message.nack.assert_not_called()

def test_process_message_validation_error(mock_publisher, mock_generative_model, mock_pubsub_message):
    """
    Testa o comportamento quando a mensagem tem dados inválidos (falha de validação Pydantic).
    """
    # Arrange: Payload inválido (falta o campo 'topic')
    invalid_payload = {
        "title": "Payload Inválido",
        "audience": "Ninguém",
    }
    message = mock_pubsub_message(invalid_payload)
    output_topic = "projects/test-proj/topics/output-topic"

    # Act
    process_message(message, mock_publisher, mock_generative_model, output_topic)

    # Assert
    mock_generative_model.generate_content.assert_not_called()
    mock_publisher.publish.assert_not_called()
    message.ack.assert_not_called()
    message.nack.assert_called_once()

def test_process_message_processing_error(mock_publisher, mock_generative_model, mock_pubsub_message):
    """
    Testa o comportamento quando ocorre um erro durante a geração do blueprint.
    """
    # Arrange
    video_idea_payload = {
        "title": "Teste de Erro",
        "topic": "Tópico que vai falhar",
        "audience": "Testadores",
    }
    # Simula uma exceção na chamada ao Gemini
    mock_generative_model.generate_content.side_effect = Exception("Falha na API do Gemini")
    
    message = mock_pubsub_message(video_idea_payload)
    output_topic = "projects/test-proj/topics/output-topic"

    # Act
    process_message(message, mock_publisher, mock_generative_model, output_topic)

    # Assert
    message.ack.assert_not_called()
    message.nack.assert_called_once()

def test_process_message_processing_error(mock_publisher, mock_generative_model, mock_pubsub_