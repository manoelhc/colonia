"""Context Secret model for Colonia."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class ContextSecret(SQLModel, table=True):
    """Context Secret model representing a secret key, environment variable name, and its Vault path."""

    __tablename__ = "context_secrets"

    id: Optional[int] = Field(default=None, primary_key=True)
    context_id: int = Field(foreign_key="contexts.id", nullable=False, index=True)
    env_var_name: str = Field(max_length=255, nullable=False)
    secret_key: str = Field(max_length=255, nullable=False)
    vault_path: str = Field(max_length=500, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "context_id": 1,
                "env_var_name": "DB_PASSWORD",
                "secret_key": "database_password",
                "vault_path": "colonia/data/prod/db",
            }
        }
