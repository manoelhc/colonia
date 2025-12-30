"""Team model for Colonia."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Team(SQLModel, table=True):
    """Team model representing a group of users."""

    __tablename__ = "teams"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True, nullable=False, unique=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "name": "DevOps Team",
                "description": "Team responsible for infrastructure management",
            }
        }
