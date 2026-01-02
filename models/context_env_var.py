"""Context Environment Variable model for Colonia."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class ContextEnvVar(SQLModel, table=True):
    """Context Environment Variable model representing non-secret key/value pairs."""

    __tablename__ = "context_env_vars"

    id: Optional[int] = Field(default=None, primary_key=True)
    context_id: int = Field(foreign_key="contexts.id", nullable=False, index=True)
    key: str = Field(max_length=255, nullable=False)
    value: str = Field(max_length=1000, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "context_id": 1,
                "key": "NODE_ENV",
                "value": "production",
            }
        }
