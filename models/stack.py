"""Stack model for Colonia."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON


class Stack(SQLModel, table=True):
    """Stack model representing an infrastructure stack."""

    __tablename__ = "stacks"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", nullable=False, index=True)
    name: str = Field(max_length=255, nullable=False)
    stack_id: Optional[str] = Field(default=None, max_length=255, index=True)
    stack_path: str = Field(max_length=500, nullable=False)
    depends_on: Optional[list] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "project_id": 1,
                "name": "VPC",
                "stack_id": "vpc",
                "stack_path": "stacks/vpc",
                "depends_on": ["other-stack"],
            }
        }
