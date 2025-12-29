"""TeamPermission model for Colonia."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class TeamPermission(SQLModel, table=True):
    """TeamPermission model representing team access permissions to resources."""

    __tablename__ = "team_permissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id", nullable=False)
    resource_type: str = Field(max_length=50, nullable=False)  # project, environment, stack
    resource_id: int = Field(nullable=False)
    all_stacks: bool = Field(default=False, nullable=False)  # Apply to all stacks in project/environment
    can_view: bool = Field(default=True, nullable=False)
    can_plan: bool = Field(default=False, nullable=False)
    can_apply: bool = Field(default=False, nullable=False)
    can_view_dependencies: bool = Field(default=False, nullable=False)  # View dependent stacks
    can_plan_dependencies: bool = Field(default=False, nullable=False)  # Plan dependent stacks
    can_apply_dependencies: bool = Field(default=False, nullable=False)  # Apply dependent stacks
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "team_id": 1,
                "resource_type": "stack",
                "resource_id": 1,
                "can_view": True,
                "can_plan": True,
                "can_apply": False,
            }
        }
