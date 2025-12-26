"""Environment model for Colonia."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Environment(SQLModel, table=True):
    """Environment model representing a deployment environment."""

    __tablename__ = "environments"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", nullable=False, index=True)
    name: str = Field(max_length=255, nullable=False)
    directory: str = Field(max_length=500, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "project_id": 1,
                "name": "development",
                "directory": "example/environments/development",
            }
        }
