"""Pub/Sub client for asynchronous messaging."""

from typing import Dict, Any, Optional
import logging
import json
from google.cloud import pubsub_v1
from google.api_core import exceptions

from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PubSubClient:
    """Client for Google Cloud Pub/Sub operations."""

    def __init__(
        self,
        project_id: str,
    ):
        """Initialize Pub/Sub client.

        Args:
            project_id: GCP project ID
        """
        self.project_id = project_id
        self._publisher = None
        self._subscriber = None

    @property
    def publisher(self):
        """Lazy initialize publisher client."""
        if self._publisher is None:
            self._publisher = pubsub_v1.PublisherClient()
        return self._publisher

    @property
    def subscriber(self):
        """Lazy initialize subscriber client."""
        if self._subscriber is None:
            self._subscriber = pubsub_v1.SubscriberClient()
        return self._subscriber

    async def publish_message(
        self,
        topic_name: str,
        message: Dict[str, Any],
        attributes: Optional[Dict[str, str]] = None,
    ) -> str:
        """Publish a message to a Pub/Sub topic.

        Args:
            topic_name: Name of the topic (without project prefix)
            message: JSON-serializable message payload
            attributes: Optional message attributes

        Returns:
            Message ID

        Raises:
            ValueError: If publishing fails
        """
        try:
            topic_path = self.publisher.topic_path(self.project_id, topic_name)

            # Convert message to JSON bytes
            message_data = json.dumps(message).encode("utf-8")

            # Create message
            pubsub_message = pubsub_v1.types.PubsubMessage(
                data=message_data,
                attributes=attributes or {},
            )

            # Publish message
            future = self.publisher.publish(
                topic_path, message_data, **(attributes or {})
            )
            message_id = future.result()

            logger.info(f"Message published to {topic_name}: {message_id}")
            return message_id

        except exceptions.GoogleAPICallError as e:
            logger.error(f"Failed to publish message to {topic_name}: {e}")
            raise ValueError(f"Message publishing failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error publishing message: {e}")
            raise ValueError(f"Message publishing failed: {e}") from e

    async def create_topic(self, topic_name: str) -> None:
        """Create a Pub/Sub topic if it doesn't exist.

        Args:
            topic_name: Name of the topic to create

        Raises:
            ValueError: If topic creation fails
        """
        try:
            topic_path = self.publisher.topic_path(self.project_id, topic_name)

            # Check if topic exists
            try:
                self.publisher.get_topic(request={"topic": topic_path})
                logger.info(f"Topic {topic_name} already exists")
                return
            except exceptions.NotFound:
                pass

            # Create topic
            self.publisher.create_topic(request={"name": topic_path})
            logger.info(f"Topic created: {topic_name}")

        except exceptions.GoogleAPICallError as e:
            logger.error(f"Failed to create topic {topic_name}: {e}")
            raise ValueError(f"Topic creation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error creating topic: {e}")
            raise ValueError(f"Topic creation failed: {e}") from e

    async def create_subscription(
        self,
        topic_name: str,
        subscription_name: str,
        push_endpoint: Optional[str] = None,
        ack_deadline_seconds: int = 60,
    ) -> None:
        """Create a Pub/Sub subscription.

        Args:
            topic_name: Name of the topic
            subscription_name: Name of the subscription
            push_endpoint: Optional push endpoint URL
            ack_deadline_seconds: Acknowledgment deadline in seconds

        Raises:
            ValueError: If subscription creation fails
        """
        try:
            topic_path = self.publisher.topic_path(self.project_id, topic_name)
            subscription_path = self.subscriber.subscription_path(
                self.project_id, subscription_name
            )

            # Check if subscription exists
            try:
                self.subscriber.get_subscription(
                    request={"subscription": subscription_path}
                )
                logger.info(f"Subscription {subscription_name} already exists")
                return
            except exceptions.NotFound:
                pass

            # Create subscription
            request = {
                "name": subscription_path,
                "topic": topic_path,
                "ack_deadline_seconds": ack_deadline_seconds,
            }

            if push_endpoint:
                request["push_config"] = pubsub_v1.types.PushConfig(
                    push_endpoint=push_endpoint
                )

            self.subscriber.create_subscription(request=request)
            logger.info(f"Subscription created: {subscription_name}")

        except exceptions.GoogleAPICallError as e:
            logger.error(f"Failed to create subscription {subscription_name}: {e}")
            raise ValueError(f"Subscription creation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error creating subscription: {e}")
            raise ValueError(f"Subscription creation failed: {e}") from e
