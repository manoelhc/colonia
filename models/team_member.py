"""TeamMember model for Colonia."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class TeamMember(SQLModel, table=True):
    """TeamMember model representing user membership in a team."""

    __tablename__ = "team_members"

    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id", nullable=False)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    role: str = Field(max_length=50, nullable=False, default="member")  # member, admin
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "team_id": 1,
                "user_id": 1,
                "role": "member",
            }
        }
