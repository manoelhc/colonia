"""Project model for Colonia."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Project(SQLModel, table=True):
    """Project model representing an infrastructure project."""

    __tablename__ = "projects"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    repository_url: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "name": "My Project",
                "description": "A sample infrastructure project",
                "repository_url": "https://github.com/user/repo",
            }
        }
