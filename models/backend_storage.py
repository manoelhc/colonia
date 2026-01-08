"""Backend Storage model for Colonia."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class BackendStorage(SQLModel, table=True):
    """Backend Storage model representing S3-compatible storage configuration."""

    __tablename__ = "backend_storages"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True, nullable=False)
    endpoint_url: str = Field(max_length=500, nullable=False)
    bucket_name: str = Field(max_length=255, nullable=False)
    region: str = Field(default="us-east-1", max_length=100, nullable=False)
    # Credentials will be stored in Vault, this stores the vault path
    vault_path: str = Field(max_length=500, nullable=False)
    # Access key and secret key names in Vault
    access_key_field: str = Field(default="access_key", max_length=255, nullable=False)
    secret_key_field: str = Field(default="secret_key", max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "name": "Production S3 Storage",
                "endpoint_url": "https://s3.amazonaws.com",
                "bucket_name": "colonia-terraform-state",
                "region": "us-east-1",
                "vault_path": "colonia/backend-storage",
                "access_key_field": "access_key",
                "secret_key_field": "secret_key",
            }
        }
