"""
Custom Pydantic base model for Video Genius.
"""

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict


def datetime_to_gmt_str(dt: datetime) -> str:
    """Convert datetime to GMT string format."""
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    """Custom base model with enhanced serialization and utilities."""

    model_config = ConfigDict(
        json_encoders={datetime: datetime_to_gmt_str},
        populate_by_name=True,
        from_attributes=True,  # Enable ORM mode for SQLAlchemy compatibility
    )

    def serializable_dict(self, **kwargs) -> dict[str, Any]:
        """Return a dict which contains only serializable fields."""
        default_dict = self.model_dump()
        return jsonable_encoder(default_dict)

    def model_dump_json_safe(self, **kwargs) -> dict[str, Any]:
        """Return a JSON-safe dict representation."""
        return self.model_dump(mode="json", **kwargs)
