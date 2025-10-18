"""Compatibility shim: expose CloudTasksClient at old path used by tests.

Some tests patch 'backend.services.cloud_tasks_client.CloudTasksClient'. The
project's real implementation lives under infrastructure.messaging; provide a
thin shim that imports and re-exports the concrete class so existing tests
continue to work without changing all patch targets.
"""

from backend.infrastructure.messaging.cloud_tasks_client import CloudTasksClient

# Re-export
__all__ = ["CloudTasksClient"]
