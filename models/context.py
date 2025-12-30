"""Context model for Colonia."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Context(SQLModel, table=True):
    """Context model representing a collection of environment variables and secrets."""

    __tablename__ = "contexts"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    project_id: int = Field(foreign_key="projects.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "name": "Production Context",
                "description": "Shared environment variables for production",
                "project_id": 1,
            }
        }
